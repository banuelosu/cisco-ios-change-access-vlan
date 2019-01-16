import time
import sys
import os
import getpass
import textfsm
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoAuthenticationException
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException

def main():
    os.system('clear')

    username = input('\nUsername: ') # Credentials needed to authenticate to device
    password = getpass.getpass()

    device = input('\nEnter device hostname: ').lower().strip()

    while True: # Verify hostname looks correct
        choice = input('\nYou entered: {}. Would you like to continue? [Y|N]: '.format(device)).upper().strip()

        if choice == 'Y':
            break
        elif choice == 'N': # Gives the user the option to enter a different hostname.
            while True:
                device = input('\nEnter device hostname: ').lower().strip()
                if device == '': # Will continue asking for a hostname until a non-blank value is entered
                    continue
                else:
                    break
        else: # Will continually ask to confirm until Y|N is entered
            continue

    # Defining dictionary needed to connect to device
    device_dictionary = {}
    device_dictionary['device_type'] = 'cisco_ios'
    device_dictionary['timeout'] = 10
    device_dictionary['username'] = username
    device_dictionary['password'] = password
    device_dictionary['ip'] = device

    try:
        device_connector = ConnectHandler(**device_dictionary) # Connects to device
        print('\nDevice: {}, Status: authenticated'.format(device))
    except (EOFError, SSHException, NetMikoTimeoutException, NetMikoAuthenticationException):
        print('\nDevice: {}, Status: authentication failure'.format(device))
        print('There appears to be an issue with authenticating onto: {}'.format(device))
        exit()
      
    command = 'show vlan'
    fsm = textfsm.TextFSM(open("./templates/show_vlan.template"))
    print('Device: {}, Command: {}'.format(device, command))
    vlan_results = fsm.ParseText(device_connector.send_command(command))

    if len(vlan_results) < 1: # If the template did not return any vlans, quit the script
        print('\n  The script did not find any VLANs. Quitting script.')
        exit()

    command = 'show interface status'
    fsm = textfsm.TextFSM(open("./templates/show_interfaces_status.template"))
    print('Device: {}, Command: {}'.format(device, command))
    interface_results = fsm.ParseText(device_connector.send_command(command))

    if len(interface_results) < 1: # If the template did not return any interfaces, quit the script
        print('\n  The script did not find any interfaces. Quitting script.')
        exit()

    # print(json.dumps(vlan_results, sort_keys='True', indent=4))
    # print(json.dumps(interface_results, sort_keys='True', indent=4))

    # Filter out interfaces that are not eligible to be changed
    available_interfaces = [interface[0] # Only store the interface id 
                            for interface in interface_results 
                            if 'connected' not in interface[2].lower() # Filters out connected interfaces
                            if 'te' not in interface[0].lower() # Filters out TenG interfaces
                            if not interface[1]] # Filters out interfaces that have descriptions


    if len(available_interfaces) < 1: # If no interfaces were returned from the filters above, quit the script
        print('\n  The script did not find any available interfaces. Quitting script.')
        exit()

    vlan_dict = {int(vlan[0]): vlan[1] for vlan in vlan_results} # Restructuring data into a dictionary, making keys as integers for easier sorting

    print('\nList of available VLANs:')
    for vlan in sorted(vlan_dict): # Can directly sort the dictionary keys within Python3.X
        print(' - {:4}, {:}'.format(vlan, vlan_dict[vlan]))

    while True:
        try:
            vlan_choice = int(input('\nEnter the VLAN ID that you would like to configure: ').strip())
        except ValueError:
            print('\n  Please enter an integer value')
            continue
        if vlan_choice in [1, 1002, 1003, 1004, 1005]:
            print('\n  Please choose a different VLAN ID')
            continue
        if vlan_dict.get(vlan_choice) is None:
            print('\n  Please enter a VLAN ID from the list.')
            continue
        else:
            break

    print('\nList of available interfaces:')
    print_output(available_interfaces, 3)

    print('''\nEnter the integer values of the interfaces you would like this VLAN on.
Comma separated list and/or ranges are supported.\n''')

    while True:
        try:
            interfaces = input('Integer values: ').strip()

            if ',' in interfaces: # Split user input on ',' and create a list
                interfaces = interfaces.split(',')
            elif '-' in interfaces: # Create a list if user only inputs a range (no csv)
                interfaces = list(range(int(interfaces.split('-')[0]), int(interfaces.split('-')[1])))

            for num in interfaces: # Check all values in list for '-'
                if '-' in str(num):
                    # Identify lower and upper bounds of range, convert to int, add 1 to upper bound, 
                    # create list based on these and add to original list
                    interfaces.extend(list(range(int(num.split('-')[0]), int(num.split('-')[1]) + 1))) 
                    interfaces = list(map(str, interfaces)) # Convert all values in list to strings - need for using 'in' expression
                    interfaces.pop(interfaces.index(num)) # Remove the old entry that has the '-'
            
            interfaces = sorted(set(map(int, interfaces))) # Convert all items to integers, unique, and sort
            
            try:
                interface_selection = [available_interfaces[num - 1] for num in interfaces]
            except IndexError:
                print('\n  Looks like you made an invalid selection, please try again.\n')
                continue

        except ValueError:
            print('\n   Looks like there was an issue with the value you entered, please try again.\n')
            continue
        else:
            break

    print('\nPlease confirm the information below:')
    print('\nAccess VLAN: {}'.format(vlan_choice))
    print('\nAccess ports: ')
    print_output(interface_selection, 3)

    # Loop through the interfaces and configure them as access ports

def print_output(input_list, flag):
    temp_list = [n 
                for n in input_list 
                if n != "" 
                if n is not True 
                if n is not None]

    input_list = sorted(list(set(temp_list)))

    if flag is 2:
        """Option 2 presents the user with the list as well as the ability to return to the main menu,
        or restart the script and returns the selection that was made"""

        input_list.append('Return to main menu')
        input_list.append('Quit')
        flag = 1

    if flag is 1:
        """Option 1 presents the user with the list and returns the selection that was made"""

        while True:
            for k, v in enumerate(input_list):
                k += 1
                print(' {}: {}'.format(k, v))

            try:
                choice = int(input("\nSelection (Integer value): ").strip())
            except ValueError:
                custom_errors(1)
                continue

            if choice == "":
                custom_errors(5)
                continue

            choice -= 1

            try:
                choice = input_list[choice]
            except IndexError:
                custom_errors(0)
                continue

            break

        if choice == "Return to main menu":
            restart_script()

        if choice == "Quit":
            custom_errors(2)
            exit()

        return choice

    elif flag is 3:
        """Option 3 presents the list to the user, but does not give the ability to make a selection.
        Does not return anything"""

        for k, v in enumerate(input_list):
            k += 1
            print(' {}: {}'.format(k, v))

        return

def restart_script():
    """ """

    custom_errors(3)
    time.sleep(1)
    os.execv(sys.executable, ['python'] + sys.argv)

    return

def custom_errors(num):
    """ """

    num = int(num)
    error_dict = {
        0: "Invalid selection. Please try again.",
        1: "You entered a non-numeric value. Check the value and try again.",
        2: "Quitting script.",
        3: "Restarting script.",
        5: "Do not enter blank values.",
        6: "Username cannot be blank.",
        7: "Maximum number of attempts exceeded.",
        10: "There was an error executing the script..."
    }

    print("\n{}".format(error_dict.get(num)))
    print(len(error_dict.get(num)) * '-')

    return

if __name__ == '__main__':
    main()

# print(json.dumps(available_interfaces, sort_keys='True', indent=4))