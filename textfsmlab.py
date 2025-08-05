# textfsmlab.py
import netmiko
from pathlib import Path
import yaml

def generate_description_configs(hostname, cdp_data, interfaces_data):
    """
    Generates a list of configuration commands for interface descriptions.
    
    Args:
        hostname (str): The hostname of the current device.
        cdp_data (list of dict): Parsed output from 'show cdp neighbor detail'.
        interfaces_data (list of dict): Parsed output from 'show ip interface brief'.

    Returns:
        list: A list of configuration commands.
    """
    config_commands = []
    
    # สร้าง mapping ของ Local Port -> Remote Info เพื่อง่ายต่อการค้นหา
    cdp_map = {entry['local_port'].replace(' ', ''): entry for entry in cdp_data}
    
    for interface in interfaces_data:
        local_interface_name = interface['intf']
        
        # จัดการกรณีพิเศษสำหรับ G0/3 ของ R2
        if hostname == "R2" and local_interface_name == "GigabitEthernet0/3":
            description = "Connect to WAN"
        # ตรวจสอบว่า Interface นี้มีข้อมูลใน CDP หรือไม่
        elif local_interface_name.replace(' ', '') in cdp_map:
            remote_info = cdp_map[local_interface_name.replace(' ', '')]
            remote_port = remote_info['remote_port']
            remote_host = remote_info['destination_host']
            description = f"Connect to {remote_port} of {remote_host}"
        # ถ้าไม่มีข้อมูล CDP และไม่ใช่ Loopback ให้ถือว่าต่อกับ PC
        elif 'Loopback' not in local_interface_name:
            description = "Connect to PC"
        else:
            # ไม่ต้องใส่ description ให้ Loopback
            continue

        config_commands.append(f"interface {local_interface_name}")
        config_commands.append(f" description {description}")
        
    return config_commands

def main():
    """
    Main function to connect to devices and apply configurations.
    """
    # --- Load Data and Connection Settings ---
    try:
        with open("devices.yml") as f:
            data = yaml.safe_load(f)
        credentials = data['credentials']
        connection_options = data['connection_options']
        all_devices = data['devices']
        # กรองเอาเฉพาะ R1, R2, S1 (ถ้ามี S1 ใน YAML)
        devices_to_configure = [d for d in all_devices if d['name'] in ['R1', 'R2', 'S1']]
    except Exception as e:
        print(f"❌ ERROR: Could not load data from devices.yml: {e}")
        exit()

    # --- Main Loop ---
    for device_data in devices_to_configure:
        device_name = device_data['name']
        print(f"\n{'='*20} Processing {device_name} ({device_data['host']}) {'='*20}")
        
        try:
            netmiko_device = {
                'device_type': 'cisco_ios',
                'host': device_data['host'],
                'username': credentials['username'],
                'use_keys': True,
                'key_file': str(Path(credentials['key_file']).expanduser()),
                'conn_timeout': 20,
                **connection_options
            }
            
            with netmiko.ConnectHandler(**netmiko_device) as net_connect:
                print(f"✅ Connected to {device_name}.")
                
                # ดึงข้อมูล CDP และ Interfaces โดยใช้ ntc-templates
                print("... Fetching CDP and Interface data ...")
                # use_textfsm=True จะบอกให้ Netmiko ใช้ ntc-templates โดยอัตโนมัติ
                cdp_neighbors = net_connect.send_command("show cdp neighbor detail", use_textfsm=True)
                interfaces_brief = net_connect.send_command("show ip interface brief", use_textfsm=True)
                
                # สร้างคอนฟิกจากฟังก์ชันที่เราทดสอบแล้ว
                config_commands = generate_description_configs(device_name, cdp_neighbors, interfaces_brief)
                
                if config_commands:
                    print("--- Applying generated descriptions ---")
                    output = net_connect.send_config_set(config_commands)
                    print(output)
                    
                    print("--- Saving configuration ---")
                    output = net_connect.save_config()
                    print(output)
                else:
                    print("--- No descriptions to apply. ---")

        except Exception as e:
            print(f"❌ ERROR: Failed to process {device_name}: {e}")

if __name__ == "__main__":
    main()