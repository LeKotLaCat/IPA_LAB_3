import netmiko
from pathlib import Path

# --- 1. Define Devices and Key Path ---
r1_ip = '172.31.21.4'
r2_ip = '172.31.21.5'
username = "admin"

try:
    key_file = str(Path.home() / ".ssh" / "id_rsa")
    if not Path(key_file).is_file():
        raise FileNotFoundError
    print(f"✅ Using SSH key file: {key_file}")
except FileNotFoundError:
    print(f"❌ ERROR: SSH private key not found at {key_file}")
    exit()

# การตั้งค่า SSH ที่จำเป็น
base_device_settings = {
    'device_type': 'cisco_ios',
    'username': username,
    'use_keys': True,
    'key_file': key_file,
    'conn_timeout': 20,
    'disabled_algorithms': dict(
        # (ส่วนนี้เหมือนเดิม)
    ),
}

r1_device = {**base_device_settings, 'host': r1_ip}
r2_device = {**base_device_settings, 'host': r2_ip}

# --- 2. Define VRF-aware Configuration Commands ---

# ### NEW: สร้าง Config สำหรับ Management โดยเฉพาะ ###
management_config = [
    # ตรวจสอบให้แน่ใจว่า Default Route ของ Management VRF มีอยู่เสมอ
    'ip route vrf management 0.0.0.0 0.0.0.0 172.31.21.1'
]

# R1 Config: ทำให้ OSPF ทำงานใน VRF ที่ถูกต้อง
r1_full_config = [
    'interface Loopback0',
    'vrf forwarding control-data',
    'ip address 1.1.1.1 255.255.255.255',
    'exit',
    'router ospf 1 vrf control-data',
    'network 192.21.1.0 0.0.0.255 area 0',
    'network 192.21.2.0 0.0.0.255 area 0',
    'network 1.1.1.1 0.0.0.0 area 0',
]

# R2 Config: ย้ายทุกอย่างที่เกี่ยวข้องกับ Data Plane เข้าไปใน VRF
r2_full_config = [
    'interface Loopback0',
    'vrf forwarding control-data',
    'ip address 2.2.2.2 255.255.255.255',
    'exit',
    'interface GigabitEthernet0/3',
    'vrf forwarding control-data',
    'ip address dhcp',
    'ip nat outside',
    'no shutdown',
    'exit',
    'router ospf 1 vrf control-data',
    'network 192.21.2.0 0.0.0.255 area 0',
    'network 172.31.21.0 0.0.0.15 area 0',
    'network 2.2.2.2 0.0.0.0 area 0',
    'default-information originate',
    'exit',
    'no access-list 1',
    'access-list 1 permit any',
    'ip nat inside source list 1 interface GigabitEthernet0/3 overload',
]

# --- 3. Main Script Logic ---
all_devices_to_configure = [
    ("R1", r1_device),
    ("R2", r2_device)
]

for device_name, device_details in all_devices_to_configure:
    print(f"\n{'='*20} Connecting to {device_name} ({device_details['host']}) {'='*20}")
    
    try:
        with netmiko.ConnectHandler(**device_details) as net_connect:
            print(f"✅ Connected to {device_name}.")
            
            # ### NEW: ส่ง Config Management ก่อนเสมอ ###
            print(f"--- Ensuring Management Route exists on {device_name} ---")
            net_connect.send_config_set(management_config)
            
            if device_name == 'R1':
                print(f"--- Applying VRF-aware config to {device_name} ---")
                output = net_connect.send_config_set(r1_full_config)
            elif device_name == 'R2':
                print(f"--- Applying VRF-aware config to {device_name} ---")
                output = net_connect.send_config_set(r2_full_config)
            print(output)
            
            print(f"--- Saving configuration on {device_name} ---")
            output = net_connect.save_config()
            print(output)

    except Exception as e:
        print(f"❌ ERROR configuring {device_name}: {e}")

print(f"\n{'='*20} Script Finished {'='*20}")