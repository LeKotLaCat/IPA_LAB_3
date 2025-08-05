import netmiko
import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# --- 1. Load Data and Setup Jinja2 Environment ---

# โหลดข้อมูลตัวแปรทั้งหมดจากไฟล์ YAML
with open("devices.yml") as f:
    data = yaml.safe_load(f)

# แยกข้อมูลออกมาเป็นตัวแปรเพื่อง่ายต่อการใช้งาน
credentials = data['credentials']
connection_options = data['connection_options']
devices_to_configure = data['devices']

# ตั้งค่า Jinja2 Environment ให้มองหาไฟล์ template ในโฟลเดอร์ปัจจุบัน
env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)

# --- 2. Main Script Logic ---

for device in devices_to_configure:
    device_name = device['name']
    
    print(f"\n{'='*20} Processing {device_name} ({device['host']}) {'='*20}")

    # --- 2.1 Generate Configuration from Template ---
    try:
        # โหลดไฟล์ template ตามชื่อที่ระบุใน YAML
        template_file = device['template']
        template = env.get_template(template_file)
        
        # "Render" หรือ "สร้าง" คอนฟิกโดยส่งข้อมูลของ device เข้าไปใน template
        # Jinja2 จะแทนที่ {{...}} และ {%...%} ทั้งหมดด้วยข้อมูลจริง
        config_to_send = template.render(device)
        
        print("--- Generated Configuration ---")
        print(config_to_send)
        print("-----------------------------")

    except Exception as e:
        print(f"❌ ERROR: Failed to generate config for {device_name}: {e}")
        continue # ข้ามไปทำอุปกรณ์ตัวต่อไป

    # --- 2.2 Connect and Send Configuration using Netmiko ---
    try:
        # สร้าง Dictionary สำหรับการเชื่อมต่อ Netmiko
        netmiko_device = {
            'device_type': 'cisco_ios',
            'host': device['host'],
            'username': credentials['username'],
            'use_keys': True,
            'key_file': str(Path(credentials['key_file']).expanduser()), # ทำให้ Path ~ ใช้งานได้
            'conn_timeout': 20,
            **connection_options # รวม connection options พิเศษเข้าไป
        }
        
        with netmiko.ConnectHandler(**netmiko_device) as net_connect:
            print(f"✅ Connected to {device_name}.")
            
            # แปลง String คอนฟิกที่สร้างขึ้นให้เป็น List เพื่อส่งให้ send_config_set
            config_lines = config_to_send.strip().split('\n')
            
            output = net_connect.send_config_set(config_lines)
            print(f"--- Configuration sent to {device_name} ---")
            print(output)
            
            print(f"--- Saving configuration on {device_name} ---")
            output = net_connect.save_config()
            print(output)

    except Exception as e:
        print(f"❌ ERROR: Failed to configure {device_name}: {e}")

print(f"\n{'='*20} Script Finished {'='*20}")