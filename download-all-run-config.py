"""
This script uses Netmiko to connect to a list of network devices,
fetches their running configuration, and saves them all into a
single timestamped backup file.
It uses SSH key authentication and specific legacy algorithms
required by the target devices.
"""

import netmiko
from pathlib import Path
from datetime import datetime

# --- Configuration ---
OUTPUT_FILENAME = "all_devices_running_configs.txt"
USERNAME = "admin"

# A dictionary to hold device names and their management IPs
# Using the management IPs from your topology diagram
DEVICES_TO_BACKUP = {
    "R0": "10.30.6.27",
    "S0": "172.31.21.2",
    "S1": "172.31.21.3",
    "R1": "172.31.21.4",
    "R2": "172.31.21.5",
    
    # S1's IP from previous script
}

# --- SSH Key and Connection Parameters ---
try:
    key_file = str(Path.home() / ".ssh" / "id_rsa")
    if not Path(key_file).is_file():
        raise FileNotFoundError
    print(f"✅ Using SSH key file: {key_file}")
except FileNotFoundError:
    print(f"❌ ERROR: SSH private key not found at {key_file}. Please check the path.")
    exit()

# These are the crucial connection settings that work for your environment
base_device_settings = {
    'device_type': 'cisco_ios',
    'username': USERNAME,
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

# --- Main Script Logic ---
# Open the output file in 'write' mode to create a fresh backup
with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as backup_file:
    # Write a main header with the current time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    backup_file.write(f"--- Network Device Configuration Backup --- \n")
    backup_file.write(f"--- Timestamp: {timestamp} ---\n\n")
    print(f"✅ Backup file created: {OUTPUT_FILENAME}")

    # Loop through each device defined in the dictionary
    for device_name, device_ip in DEVICES_TO_BACKUP.items():
        print(f"\n{'='*20} Processing {device_name} ({device_ip}) {'='*20}")
        
        # Combine base settings with the specific host IP for this device
        device_details = {**base_device_settings, 'host': device_ip}
        
        try:
            # Establish the connection
            with netmiko.ConnectHandler(**device_details) as net_connect:
                print(f"✅ Connected to {device_name}.")
                
                # Fetch the running configuration
                print(f"... Fetching 'show running-config' ...")
                running_config = net_connect.send_command(
                    "show running-config",
                    read_timeout=60  # Increase timeout for long configs
                )
                
                # Write the header and config to the file
                header = f"\n{'#'*20} [ Configuration for {device_name} ({device_ip}) ] {'#'*20}\n\n"
                backup_file.write(header)
                backup_file.write(running_config)
                backup_file.write("\n\n") # Add extra newlines for readability
                
                print(f"✅ Configuration for {device_name} saved to file.")

        except Exception as e:
            # If any error occurs, log it to the screen and the file
            print(f"❌ FAILED to backup {device_name}: {e}")
            error_header = f"\n{'!'*20} [ FAILED to retrieve config from {device_name} ({device_ip}) ] {'!'*20}\n"
            backup_file.write(error_header)
            backup_file.write(f"Error: {e}\n\n")

print(f"\n--- SCRIPT COMPLETE ---")
print(f"All configurations have been backed up to '{OUTPUT_FILENAME}'.")