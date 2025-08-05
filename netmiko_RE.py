import netmiko
import re
from pathlib import Path
import yaml

# --- 1. Load Device Data and Connection Settings ---
# เราจะใช้ไฟล์ devices.yml เดิม แต่จะโฟกัสแค่ R1 และ R2
try:
    with open("devices.yml") as f:
        data = yaml.safe_load(f)
    credentials = data['credentials']
    connection_options = data['connection_options']
    all_devices = data['devices']
    # กรองเอาเฉพาะ R1 และ R2
    routers_to_check = [d for d in all_devices if d['name'] in ['R1', 'R2']]
except (FileNotFoundError, KeyError) as e:
    print(f"❌ ERROR: Could not load data from devices.yml. Please check the file. Error: {e}")
    exit()

# --- 2. Define the Regular Expression Pattern ---
# Pattern นี้ถูกออกแบบมาเพื่อจับ 3 กลุ่มข้อมูล:
# 1. ([\w\/\.]+) -> ชื่อ Interface (เช่น GigabitEthernet0/0, Loopback0)
# 2. (is up, line protocol is up) -> ข้อความที่ยืนยันว่า Interface Active
# 3. (Last input\s+)([\w\d\:]+|never) -> Uptime (จับข้อความหลังคำว่า "Last input")
# เราใช้ re.MULTILINE เพื่อให้ ^ (เริ่มต้นบรรทัด) ทำงานกับทุกบรรทัด
# หมายเหตุ: 'show interfaces' แสดง uptime ได้หลายรูปแบบมาก regex นี้พยายามจับรูปแบบที่พบบ่อย
regex_pattern = re.compile(
    r"^([\w\/\.]+)\s+is\s+(up, line protocol is up).*"
    r"Last input\s+([\w\d\:]+|never),",
    re.MULTILINE
)


# --- 3. Main Script Logic ---
for device_data in routers_to_check:
    device_name = device_data['name']
    
    print(f"\n{'='*20} Processing {device_name} ({device_data['host']}) {'='*20}")

    try:
        # สร้าง Dictionary สำหรับการเชื่อมต่อ Netmiko
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
            
            # ส่งคำสั่ง 'show interfaces'
            print("... Fetching 'show interfaces' output ...")
            output = net_connect.send_command("show interfaces", read_timeout=60)
            
            # ใช้ Regex เพื่อค้นหาทุกส่วนที่ตรงกับ Pattern
            active_interfaces = regex_pattern.finditer(output)
            
            print(f"\n--- Active Interfaces on {device_name} ---")
            found = False
            for match in active_interfaces:
                found = True
                interface_name = match.group(1)
                status = match.group(2)
                uptime = match.group(3)
                
                print(f"  - Interface: {interface_name:<25} Uptime: {uptime}")
            
            if not found:
                print("  No active interfaces found matching the pattern.")

    except Exception as e:
        print(f"❌ ERROR: Failed to process {device_name}: {e}")

print(f"\n{'='*20} Script Finished {'='*20}")