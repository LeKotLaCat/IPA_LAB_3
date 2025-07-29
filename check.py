"""
Connects to multiple devices, backs up their running configuration
to a single timestamped file, and also shows the IP interface status.
"""

import time
import paramiko
import os
import socket
from pathlib import Path
from datetime import datetime ### NEW ###

# --- Configuration ---
USERNAME = "admin"
PASSWORD = "cisco"  # Enable password
#DEVICE_IPS = ["10.30.6.27"]
DEVICE_IPS = ["10.30.6.42", "172.31.21.2", "172.31.21.3", "172.31.21.4", "172.31.21.5"]
OUTPUT_FILENAME = "copy-running-config.txt" ### NEW: Define the output filename ###

# --- Load SSH Private Key ---
try:
    KEY_PATH = str(Path.home() / ".ssh" / "id_rsa")
    PRIVATE_KEY = paramiko.RSAKey.from_private_key_file(KEY_PATH)
    print(f"Successfully loaded SSH key from: {KEY_PATH}")
except (FileNotFoundError, paramiko.ssh_exception.PasswordRequiredException) as e:
    print(f"Error loading SSH key: {e}")
    print("Script will terminate. Please ensure your key exists and is not password-protected.")
    exit()

# ### NEW: Open the file before the loop starts ###
# 'w' mode overwrites the file if it exists, creating a fresh backup.
# 'encoding='utf-8'' handles all characters properly.
with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as backup_file:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    backup_file.write(f"--- Network Device Configuration Backup taken at {timestamp} ---\n\n")
    print(f"✅ Backup file created: {OUTPUT_FILENAME}")

    # --- Script Execution ---
    for ip in DEVICE_IPS:
        print(f"\n{'='*20} [Processing {ip}] {'='*20}")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Using the connection parameters that work for you
            client.connect(
                hostname=ip,
                username=USERNAME,
                pkey=PRIVATE_KEY,
                look_for_keys=False,
                allow_agent=False,
                timeout=15,
                disabled_algorithms=dict(
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
            )
            print(f"✅ Successfully connected to {ip}")

            with client.invoke_shell() as ssh:
                ssh.send("terminal length 0\n")
                time.sleep(1)
                ssh.recv(65535)

                ssh.send("wr\n")
                time.sleep(1)
                print("✅ Write Out successfully.")

        except Exception as e:
            print(f"❌ An error occurred for {ip}: {e}")
        finally:
            if client.get_transport() and client.get_transport().is_active():
                client.close()
                print(f"✅ Connection to {ip} closed.")

print(f"\n--- SCRIPT COMPLETE ---")