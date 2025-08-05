# test_textfsmlab.py
import pytest
from textfsmlab import generate_description_configs

# นี่คือ "ข้อมูลจำลอง" ที่เราจะใช้ทดสอบฟังก์ชันของเรา
# ไม่ต้องเชื่อมต่อกับอุปกรณ์จริง
mock_cdp_data = [
    {'destination_host': 'R2', 'local_port': 'Gig 0/2', 'remote_port': 'Gig 0/1'},
    {'destination_host': 'S0', 'local_port': 'Gig 0/0', 'remote_port': 'Gig 0/1'}
]

mock_interfaces_data = [
    {'intf': 'GigabitEthernet0/0', 'status': 'up', 'protocol': 'up'},
    {'intf': 'GigabitEthernet0/1', 'status': 'up', 'protocol': 'up'}, # Connected to PC
    {'intf': 'GigabitEthernet0/2', 'status': 'up', 'protocol': 'up'},
    {'intf': 'Loopback0', 'status': 'up', 'protocol': 'up'},
]

def test_generate_description_for_r1():
    """
    Test case for R1:
    - G0/2 connects to R2's G0/1.
    - G0/1 connects to a PC.
    - G0/0 connects to S0's G0/1.
    """
    hostname = "R1"
    # เรียกใช้ฟังก์ชันที่เรากำลังจะสร้าง
    config_commands = generate_description_configs(hostname, mock_cdp_data, mock_interfaces_data)
    
    # ตรวจสอบผลลัพธ์ที่คาดหวัง
    assert 'interface GigabitEthernet0/2' in config_commands
    assert ' description Connect to Gig 0/1 of R2' in config_commands
    
    assert 'interface GigabitEthernet0/1' in config_commands
    assert ' description Connect to PC' in config_commands
    
    assert 'interface GigabitEthernet0/0' in config_commands
    assert ' description Connect to Gig 0/1 of S0' in config_commands

def test_generate_description_for_r2_wan_port():
    """
    Test case for R2's special WAN port G0/3.
    """
    hostname = "R2"
    # ไม่ต้องมี CDP data เพราะ G0/3 ไม่ได้ต่อกับอุปกรณ์ Cisco
    cdp_data = [] 
    interfaces_data = [
        {'intf': 'GigabitEthernet0/3', 'status': 'up', 'protocol': 'up'}
    ]
    
    config_commands = generate_description_configs(hostname, cdp_data, interfaces_data)
    
    assert 'interface GigabitEthernet0/3' in config_commands
    assert ' description Connect to WAN' in config_commands