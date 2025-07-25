"""
Example of using Paramiko on Windows to connect to multiple devices,
enter enable mode, and run multiple commands.
"""

import time
import paramiko
import os
import socket
from pathlib import Path

# --- Configuration ---
USERNAME = "admin"
PASSWORD = "cisco"  # This is the 'enable' password
DEVICE_IPS = ["10.30.6.27", "172.31.21.2", "172.31.21.3", "172.31.21.4", "172.31.21.5"]

# --- Load SSH Private Key ---
try:
    KEY_PATH = str(Path.home() / ".ssh" / "id_rsa")
    PRIVATE_KEY = paramiko.RSAKey.from_private_key_file(KEY_PATH)
    print(f"Successfully loaded SSH key from: {KEY_PATH}")
except (FileNotFoundError, paramiko.ssh_exception.PasswordRequiredException) as e:
    print(f"Error loading SSH key: {e}")
    print("Script will terminate. Please ensure your key exists and is not password-protected.")
    PRIVATE_KEY = None
    exit() # Exit if the key cannot be loaded

# --- Script Execution ---
for ip in DEVICE_IPS:
    print(f"\n{'='*20} [Connecting to {ip}] {'='*20}")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # The connection parameters from your working script
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
            # --- Setup terminal and enter enable mode ---
            ssh.send("terminal length 0\n")
            time.sleep(1)
            ssh.recv(65535) # Clear initial buffer

            # ssh.send("enable\n")
            # time.sleep(1)
            # ssh.recv(65535) # Clear buffer after 'enable'

            # ssh.send(f"{PASSWORD}\n")
            # time.sleep(1)
            # output = ssh.recv(65535).decode('utf-8', 'ignore')
            # if "#" not in output: # Check if we successfully entered enable mode
            #     print(f"❌ Failed to enter enable mode on {ip}. Check password.")
            #     continue # Skip to the next device

            # print("✅ Entered enable mode successfully.")

            # # --- Command 1: show ip interface brief ---
            # print("--- Running: show ip interface brief ---")
            # ssh.send("show ip interface brief\n")
            # time.sleep(2)
            # result_int_br = ssh.recv(65535).decode('utf-8', 'ignore')
            # print(result_int_br)

            # --- Command 2: show running-config ---
            # print("\n--- Running: show running-config ---")
            # ssh.send("show running-config\n")
            # time.sleep(4) # Give more time for this long command
            # result_run_config = ssh.recv(65535).decode('utf-8', 'ignore')
            # print(result_run_config)

    except paramiko.AuthenticationException:
        print(f"❌ Authentication failed for {ip}. Check username or SSH key.")
    except (socket.timeout, TimeoutError):
        print(f"❌ Connection timed out for {ip}. Device might be unreachable.")
    except Exception as e:
        print(f"❌ An unexpected error occurred for {ip}: {e}")
    finally:
        # Always close the connection
        if client.get_transport() and client.get_transport().is_active():
            client.close()
            print(f"✅ Connection to {ip} closed.")