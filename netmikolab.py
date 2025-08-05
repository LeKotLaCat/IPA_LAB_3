import netmiko
from pathlib import Path

# --- 1. Define Devices and Key Path ---
s1_ip = '172.31.21.3' # Management IP for S1
r1_ip = '172.31.21.4' # Management IP for R1
r2_ip = '172.31.21.5' # Management IP for R2
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
        pubkeys=["rsa-sha2-256", "rsa-sha2-512"],
        kex=[
            "diffie-hellman-group1-sha1", "diffie-hellman-group14-sha256",
            "diffie-hellman-group16-sha512", "diffie-hellman-group18-sha512",
            "diffie-hellman-group-exchange-sha256", "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384", "ecdh-sha2-nistp521",
            "curve25519-sha256@libssh.org", "curve25519-sha256",
        ],
        hostkeys=[
            "ssh-ed25519", "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384", "ecdsa-sha2-nistp521"
        ],
    ),
}

s1_device = {**base_device_settings, 'host': s1_ip}
r1_device = {**base_device_settings, 'host': r1_ip}
r2_device = {**base_device_settings, 'host': r2_ip}

# --- 2. Define Configuration Commands based on Topology ---

# S1 Config
s1_vlan_config = ['vlan 101', 'name CONTROL_DATA_PLANE']

# R1 Config: เพิ่มการตั้งค่า IP และ no shutdown
r1_full_config = [
    # Basic Interface Config
    'interface Loopback0',
    'ip address 1.1.1.1 255.255.255.255',
    'exit',
    'interface GigabitEthernet0/1',
    'ip address 192.21.1.1 255.255.255.0',
    'no shutdown',
    'exit',
    'interface GigabitEthernet0/2',
    'ip address 192.21.2.1 255.255.255.0',
    'no shutdown',
    'exit',
    # OSPF Config
    'router ospf 1',
    'network 192.21.1.0 0.0.0.255 area 0',
    'network 192.21.2.0 0.0.0.255 area 0',
    'network 1.1.1.1 0.0.0.0 area 0',
]

# R2 Config: เพิ่มการตั้งค่า IP และ no shutdown
r2_full_config = [
    # Basic Interface Config
    'interface Loopback0',
    'ip address 2.2.2.2 255.255.255.255',
    'exit',
    'interface GigabitEthernet0/1',
    'ip address 192.21.2.2 255.255.255.0',
    'ip nat inside',
    'no shutdown',
    'exit',
    'interface GigabitEthernet0/2',
    'ip address 172.31.21.6 255.255.255.240',
    'ip nat inside',
    'no shutdown',
    'exit',
    'interface GigabitEthernet0/3',
    'ip address dhcp',
    'ip nat outside',
    'no shutdown',
    'exit',
    # OSPF Config
    'router ospf 1',
    'passive-interface GigabitEthernet0/3',
    'network 192.21.2.0 0.0.0.255 area 0',
    'network 172.31.21.0 0.0.0.15 area 0', # แก้ไข network statement ให้ตรง
    'network 2.2.2.2 0.0.0.0 area 0',
    'default-information originate',
    'exit',
    # NAT/PAT Config
    'no access-list 1',
    'access-list 1 permit any',
    'ip nat inside source list 1 interface GigabitEthernet0/3 overload',
]

# VTY Config
vty_acl_config = [
    'ip access-list standard VTY_ACCESS',
    'permit 172.31.21.0 0.0.0.15',
    'permit 10.30.6.0 0.0.0.255',
    'exit',
    'line vty 0 15',
    'access-class VTY_ACCESS in',
    'transport input ssh telnet',
]

# --- 3. Main Script Logic ---
all_devices_to_configure = [
    ("S1", s1_device),
    ("R1", r1_device),
    ("R2", r2_device)
]

for device_name, device_details in all_devices_to_configure:
    print(f"\n{'='*20} Connecting to {device_name} ({device_details['host']}) {'='*20}")
    
    try:
        with netmiko.ConnectHandler(**device_details) as net_connect:
            print(f"✅ Connected to {device_name} in privileged mode using SSH Key.")
            
            if device_name == 'S1':
                output = net_connect.send_config_set(s1_vlan_config)
            elif device_name == 'R1':
                output = net_connect.send_config_set(r1_full_config) # ใช้คอนฟิกตัวเต็ม
            elif device_name == 'R2':
                output = net_connect.send_config_set(r2_full_config) # ใช้คอนฟิกตัวเต็ม
            print(output)
                
            print(f"--- Applying common VTY Access-List on {device_name} ---")
            output = net_connect.send_config_set(vty_acl_config)
            print(output)
            
            print(f"--- Saving configuration on {device_name} ---")
            output = net_connect.save_config()
            print(output)

    except Exception as e:
        print(f"❌ ERROR configuring {device_name}: {e}")

print(f"\n{'='*20} Script Finished {'='*20}")