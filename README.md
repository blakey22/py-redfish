py-redfish
================

py-redfish is a Redfish client for next generation of BMC management.

### Requirements
    * gevent

### Usage
    * python main.py -H <IP> -U <USER_NAME> -P <PASSWORD> user create "test" "password" "Oem.Hp.LoginName=test"
    * python main.py -H <IP> -U <USER_NAME> -P <PASSWORD> raw list "/rest/v1"

### Note
    This project is still under development and only tested on HP server.
