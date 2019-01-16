import time
import sys
import os
import getpass
import textfsm
import json
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoAuthenticationException
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException

def main():
    os.system('clear')

    # username = input('\nUsername: ') # Credentials needed to authenticate to device
    # password = getpass.getpass()

    # device = input('\nEnter device hostname: ').lower().strip()

    # while True: # Verify hostname looks correct
    #     choice = input('\nYou entered: {}. Would you like to continue? [Y|N]: '.format(device)).upper().strip()

    #     if choice == 'Y':
    #         break
    #     elif choice == 'N': # Gives the user the option to enter a different hostname.
    #         while True:
    #             device = input('\nEnter device hostname: ').lower().strip()
    #             if device == '': # Will continue asking for a hostname until a non-blank value is entered
    #                 continue
    #             else:
    #                 break
    #     else: # Will continually ask to confirm until Y|N is entered
    #         continue

    # # Defining dictionary needed to connect to device
    # device_dictionary = {}
    # device_dictionary['device_type'] = 'cisco_ios'
    # device_dictionary['timeout'] = 10
    # device_dictionary['username'] = username
    # device_dictionary['password'] = password
    # device_dictionary['ip'] = device

    # try:
    #     device_connector = ConnectHandler(**device_dictionary) # Connects to device
    #     print('\nDevice: {}, Status: authenticated'.format(device))
    # except (EOFError, SSHException, NetMikoTimeoutException, NetMikoAuthenticationException):
    #     print('\nDevice: {}, Status: authentication failure'.format(device))
    #     print('There appears to be an issue with authenticating onto: {}'.format(device))
    #     exit()
      
    # command = 'show vlan'
    # fsm = textfsm.TextFSM(open("./templates/show_vlan.template"))
    # print('Device: {}, Command: {}'.format(device, command))
    # vlan_results = fsm.ParseText(device_connector.send_command(command))

    # if len(vlan_results) < 1: # If the template did not return any vlans, quit the script
    #     print('\n  The script did not find any VLANs. Quitting script.')
    #     exit()

    # command = 'show interface status'
    # fsm = textfsm.TextFSM(open("./templates/show_interfaces_status.template"))
    # print('Device: {}, Command: {}'.format(device, command))
    # interface_results = fsm.ParseText(device_connector.send_command(command))

    # if len(interface_results) < 1: # If the template did not return any interfaces, quit the script
    #     print('\n  The script did not find any interfaces. Quitting script.')
    #     exit()

    # # print(json.dumps(vlan_results, sort_keys='True', indent=4))
    # # print(json.dumps(interface_results, sort_keys='True', indent=4))

    # # Filter out interfaces that are not eligible to be changed
    # available_interfaces = [interface[0] # Only store the interface id 
    #                         for interface in interface_results 
    #                         if 'connected' not in interface[2].lower() # Filters out connected interfaces
    #                         if 'te' not in interface[0].lower() # Filters out TenG interfaces
    #                         if not interface[1]] # Filters out interfaces that have descriptions


    # if len(available_interfaces) < 1: # If no interfaces were returned from the filters above, quit the script
    #     print('\n  The script did not find any available interfaces. Quitting script.')
    #     exit()

    # vlan_dict = {int(vlan[0]): vlan[1] for vlan in vlan_results} # Restructuring data into a dictionary, making keys as integers for easier sorting

    # print('\nList of available VLANs:')
    # for vlan in sorted(vlan_dict.keys()): # Can directly sort the dictionary keys within Python3.X
    #     print(' - {:4}, {:}'.format(vlan, vlan_dict[vlan]))

    # while True:
    #     try:
    #         vlan_choice = int(input('\nEnter the VLAN ID that you would like to configure: ').strip())
    #     except ValueError:
    #         print('\n  Please enter an integer value')
    #         continue
    #     if vlan_choice in [1, 1002, 1003, 1004, 1005]:
    #         print('\n  Please choose a different VLAN ID')
    #         continue
    #     if vlan_dict.get(vlan_choice) is None:
    #         print('\n  Please enter a VLAN ID from the list.')
    #         continue
    #     else:
    #         break

    available_interfaces = ["Gi8/21","Gi8/22","Gi8/23","Gi8/24","Gi8/25","Gi8/27","Gi8/28","Gi8/29","Gi8/3","Gi8/30","Gi8/31","Gi8/34","Gi8/35","Gi8/36","Gi8/37","Gi8/38","Gi8/4","Gi8/40","Gi8/41","Gi8/43","Gi8/44","Gi8/45","Gi8/46","Gi8/47","Gi8/48","Gi8/5","Gi8/6","Gi9/10","Gi9/11","Gi9/12","Gi9/13","Gi9/14","Gi9/15","Gi9/16","Gi9/17","Gi9/18","Gi9/19","Gi9/2","Gi9/21","Gi9/22","Gi9/23","Gi9/24","Gi9/25","Gi9/26","Gi9/27","Gi9/28","Gi9/29","Gi9/3","Gi9/30","Gi9/31","Gi9/32","Gi9/34","Gi9/36","Gi9/4","Gi9/46","Gi9/47","Gi9/48","Gi9/5","Gi9/6"]

    print('\nList of available interfaces:')
    print_output(available_interfaces, 3)

    print('''\nEnter the integer values of the interfaces you would like this VLAN on.
Comma separated list and/or ranges are supported.\n''')

    while True:
        try:
            interfaces = input('Integer values: ').strip()

            if ',' in interfaces:
                interfaces = interfaces.split(',')

            for num in interfaces:
                if '-' in str(num):
                    # Identify lower and upper bounds of range, convert to int, add 1 to upper bound, 
                    # create list based on these and add to original list
                    interfaces.extend(list(range(int(num.split('-')[0]), int(num.split('-')[1]) + 1))) 
                    interfaces = list(map(str, interfaces))
                    interfaces.pop(interfaces.index(num))
            
            interfaces = sorted(map(int, interfaces))
            
            try:
                interface_selection = [available_interfaces[num - 1] for num in interfaces]
            except IndexError:
                print('\n  Looks like you made an invalid selection, please try again.\n')
                continue

            print(interface_selection)

        except ValueError:
            print('\n   Looks like there was an issue with the value you entered, please try again.\n')
            continue

def print_output(input_list, flag):
    """ """

    temp_list = []
    for n in input_list:
        if n != "":
            if n is not True:
                if n is not None:
                    temp_list.append(n)

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

            choice = raw_input("\nSelection (Integer value): ").strip()

            if choice == "":
                custom_errors(5)
                continue

            try:
                choice = int(choice)
            except ValueError:
                custom_errors(1)
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


if __name__ == '__main__':
    main()

# print(json.dumps(available_interfaces, sort_keys='True', indent=4))