import psutil
import subprocess
import time

def is_interface_active(interface_name):
    interface_stats = psutil.net_if_stats().get(interface_name)
    return interface_stats is not None and interface_stats.isup

def enable_interface(interface_name):
    subprocess.run(["netsh", "interface", "set", "interface", interface_name, "admin=enable"])
    log_entry = f"Enabled {interface_name}\n"
    log_file.write(log_entry)
    print(log_entry, end="")

def disable_interface(interface_name):
    subprocess.run(["netsh", "interface", "set", "interface", interface_name, "admin=disable"])
    log_entry = f"Disabled {interface_name}\n"
    log_file.write(log_entry)
    print(log_entry, end="")

def is_ping_successful(host):
    try:
        subprocess.run(["ping", "-n", "1", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_active_interface():
    for interface, stats in psutil.net_if_stats().items():
        if stats.isup:
            return interface
    return None

def switch_ethernet(interface_to_enable, interface_to_disable):
    log_entry = f"Switching from {interface_to_disable} to {interface_to_enable}\n"
    log_file.write(log_entry)
    print(log_entry, end="")

    active_network = get_active_interface()

    if is_interface_active(interface_to_enable):
        log_entry = f"{interface_to_enable} is already active.\n"
        log_file.write(log_entry)
        print(log_entry, end="")
    elif not is_interface_active(active_network):
        # If the currently active network is down, check the other active network before switching
        other_interface = "Ethernet" if interface_to_enable == "Ethernet 2" else "Ethernet 2"
        other_ping_result = is_ping_successful("8.8.8.8")  # Ping the other active network's gateway or a reliable IP

        log_entry = f"{active_network} is down. Pinging {other_interface}... {'Successful' if other_ping_result else 'Failed'}\n"
        log_file.write(log_entry)
        print(log_entry, end="")

        if other_ping_result:
            disable_interface(interface_to_disable)
            enable_interface(interface_to_enable)
        else:
            log_entry = f"Both networks are unreachable. Waiting for the next check.\n"
            log_file.write(log_entry)
            print(log_entry, end="")
    else:
        disable_interface(interface_to_disable)
        enable_interface(interface_to_enable)

if __name__ == "__main__":
    log_file_path = "network_log.txt"

    with open(log_file_path, "a") as log_file:
        while True:
            # Display currently active network
            active_network = get_active_interface()
            
            log_entry = f"Currently active network: {active_network}\n" if active_network else "No active network\n"
            log_file.write(log_entry)
            print(log_entry, end="")

            # Check if any of the interfaces is already active
            if active_network:
                log_entry = f"{active_network} is already active.\n"
                log_file.write(log_entry)
                print(log_entry, end="")
            #else:
                # Still ping
                ping_result1 = is_ping_successful("8.8.8.8")  # Adjust the IP address or host as needed
                ping_result2 = is_ping_successful("8.8.4.4")  # Another example IP address

                log_entry = f"Ping to 8.8.8.8: {'Successful' if ping_result1 else 'Failed'}\n"
                log_file.write(log_entry)
                print(log_entry, end="")
                
                log_entry = f"Ping to 8.8.4.4: {'Successful' if ping_result2 else 'Failed'}\n"
                log_file.write(log_entry)
                print(log_entry, end="")

                # # if ping_result1 or ping_result2:
                # #     # At least one of the ping tests is successful, switch to the first interface
                # #     switch_ethernet("Ethernet", "Ethernet 2")
                # else:
                #     log_entry = "No active network and both networks are unreachable. Waiting for the next check.\n"
                #     log_file.write(log_entry)
                #     print(log_entry, end="")

            # Display currently active network after switching
            active_network_after_switch = get_active_interface()
            log_entry = f"After switching, currently active network: {active_network_after_switch}\n" if active_network_after_switch else "No active network\n"
            log_file.write(log_entry)
            print(log_entry, end="")

            log_file.write('\n')

            print('\n')
            # Sleep for a specific duration before
            time.sleep(3)