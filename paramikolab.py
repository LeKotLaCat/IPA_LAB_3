import time
import paramiko
import os

# --- การตั้งค่า ---
username = 'admin'
# ระบุตำแหน่งของไฟล์ Private Key ให้ถูกต้อง (ใช้ os.path.expanduser('~') เพื่อความสะดวก)
key_filename = os.path.expanduser('~/.ssh/id_rsa') 

# รายชื่อ IP ของอุปกรณ์ทั้งหมด
devices_ip = ["10.30.6.71","172.31.112.4", "172.31.112.5", "172.31.112.6"]
# devices_ip = ["10.30.6.71"] # <--- ใช้ IP จากตัวอย่างของคุณเพื่อทดสอบ

# --- โค้ดหลัก ---
for ip in devices_ip:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {ip}...")

        # *** จุดสำคัญ: เพิ่ม Option สำหรับอัลกอริทึมรุ่นเก่า ***
        # เราจะสร้าง Dictionary เพื่อเก็บค่าเหล่านี้แล้วส่งเข้าไป
        disabled_algorithms = {
            'kex': ['diffie-hellman-group1-sha1'], # บางครั้งต้องระบุค่า default ที่เก่ามากๆ ด้วย
            'mac': ['hmac-md5', 'hmac-sha1-96'],
            'key': ['ssh-rsa']
        }

        client.connect(
            hostname=ip,
            username=username,
            key_filename=key_filename,
            # เพิ่มพารามิเตอร์ disabled_algorithms เพื่อบอกให้ Paramiko ยอมใช้อัลกอริทึมเก่า
            # บางเวอร์ชันของ Paramiko อาจต้องใช้ชื่อพารามิเตอร์อื่น
            # แต่ปกติจะใช้การตั้งค่า Transport โดยตรงแบบนี้
            # เราจะสร้าง transport object เองเพื่อความแน่นอน
            transport_factory=lambda: create_transport_with_legacy_algos(ip)
        )

        with client.invoke_shell() as ssh:
            print(f"SUCCESS: Connected to {ip}")
            
            # ส่งคำสั่งต่างๆ
            ssh.send("terminal length 0\n")
            time.sleep(1)
            result = ssh.recv(2000).decode('ascii')
            print(result)

            ssh.send("sh ip int br\n")
            time.sleep(2)
            result = ssh.recv(2000).decode('ascii')
            print(result)

    except paramiko.AuthenticationException:
        print(f"FAILED: Authentication failed for {ip}. Check username or SSH key.")
    except paramiko.SSHException as e:
        print(f"FAILED: SSH negotiation failed for {ip}. Error: {e}")
    except Exception as e:
        print(f"FAILED: An unexpected error occurred for {ip}. Error: {e}")
    finally:
        if client:
            client.close()

# Helper function to create a transport with specific algorithms
def create_transport_with_legacy_algos(ip, port=22):
    """
    Creates a Paramiko transport object and manually enables legacy algorithms.
    """
    transport = paramiko.Transport((ip, port))
    
    # Kex (Key Exchange)
    transport.get_security_options().kex = ('diffie-hellman-group14-sha1', 'diffie-hellman-group-exchange-sha1')
    
    # HostKey
    transport.get_security_options().key_types = ('ssh-rsa',)

    # MACs
    transport.get_security_options().macs = ('hmac-sha1', 'hmac-sha1-96')
    
    # Ciphers (ถ้าจำเป็น)
    # transport.get_security_options().ciphers = ('aes128-cbc', '3des-cbc')
    
    return transport


print("\n--- Script finished ---")