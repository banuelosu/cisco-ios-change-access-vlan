# cisco-ios-change-access-vlan

### Prerequisites
```
python3
pip3 install netmiko
pip3 install getpass
pip3 intall textfsm
```

### Python Modules Used
 - sys
 - os
 - getpass
 - netmiko
 - time
 - textfsm
 
### How to run
```
python3 main.py
```
The script will ask the user to enter a device name (cisco-ios). The script will login and identify all the VLANs on the switch. After, a list of 'notconnected' interfaces with 'no description' excluding TenG interfaces will be presented to the user. The user will make their selection and the VLAN will be configured on the interfaces as an access VLAN.

Notes:
```
if Command "python setup.py egg_info" failed with error code 1
pip3 install --upgrade setuptools

if fatal error: openssl/opensslv.h
sudo apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev
```
