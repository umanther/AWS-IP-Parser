# coding=UTF-8
import json
import os
import urllib

from appJar import gui
from netaddr import *

# --- globals ---
_raw_json = str()
_ipv4_addresses = []
_ipv6_addresses = []

# --- constants ---
# Data
IP_DATA_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"

# App Windows
GUI_MAIN = "AWS IP Parser"

# Labels
L_SERVICE = "Service:"
L_REGION = "Region:"

# Buttons
BT_REFRESH = "Refresh IP List"

#  Radio Buttons
RB_IPVERSION = "IPVersion"
RB_IPV_IPV4 = "IPv4"
RB_IPV_IPV6 = "IPv6"

# Text Area
TA_SYNCTOKEN = "Sync Token"
TA_CREATEDATE = "Creation Date"
TA_IPLIST = "IP List"

# Option Box
OB_SERVICE = "Service"
OB_REGION = "Region"

# Toggle Frame
TF_IPVERSION = "IP Version"

# Panes
P_LEFT = "Left"
P_RIGHT = "Right"


# --- functions ---
# Function processes raw JSON data and places it in the appropriate data variable
def process_data():
    global _raw_json, _ipv4_addresses, _ipv6_addresses

    Processed_JSON = json.loads(_raw_json)
    _ipv4_addresses = Processed_JSON['prefixes']
    _ipv6_addresses = Processed_JSON['ipv6_prefixes']

    for ndx, _ in enumerate(_ipv4_addresses):
        _ipv4_addresses[ndx]['ip_prefix'] = IPNetwork(_ipv4_addresses[ndx]['ip_prefix'])

    for ndx, _ in enumerate(_ipv6_addresses):
        _ipv6_addresses[ndx]['ipv6_prefix'] = IPNetwork(_ipv6_addresses[ndx]['ipv6_prefix'])


# Function updates the service list from data stored
def update_service_list():
    global _ipv4_addresses, _ipv6_addresses
    EnvironmentList = {}
    IPVersion = app.getRadioButton(RB_IPVERSION)

    if IPVersion == RB_IPV_IPV4:
        for Address in _ipv4_addresses:
            EnvironmentList[Address['service']] = Address['service']

    if IPVersion == RB_IPV_IPV6:
        for Address in _ipv6_addresses:
            EnvironmentList[Address['service']] = Address['service']

    app.changeOptionBox(OB_SERVICE, EnvironmentList, callFunction=False)


# Function updates region list from data stored
def update_region_list():
    global _ipv4_addresses, _ipv6_addresses
    RegionList = {}
    IPVersion = app.getRadioButton(RB_IPVERSION)
    Service = app.getOptionBox(OB_SERVICE)

    if IPVersion == RB_IPV_IPV4:
        for Address in _ipv4_addresses:
            if Address['service'] == Service:
                RegionList[Address['region']] = Address['region']

    if IPVersion == RB_IPV_IPV6:
        for Address in _ipv6_addresses:
            if Address['service'] == Service:
                RegionList[Address['region']] = Address['region']

    app.changeOptionBox(OB_REGION, RegionList, callFunction=False)


# Function updates IP list from data stored
def update_ip_list():
    global _ipv4_addresses, _ipv6_addresses
    IPList = IPSet()

    app.clearTextArea(TA_IPLIST, callFunction=False)

    IPVersion = app.getRadioButton(RB_IPVERSION)
    Service = app.getOptionBox(OB_SERVICE)
    Region = app.getOptionBox(OB_REGION)

    if IPVersion == RB_IPV_IPV4:
        for Address in _ipv4_addresses:
            if Address['service'] == Service and Address['region'] == Region:
                IPList.add(Address['ip_prefix'])

    if IPVersion == RB_IPV_IPV6:
        for Address in _ipv6_addresses:
            if Address['service'] == Service and Address['region'] == Region:
                IPList.add(Address['ipv6_prefix'])

    app.setTextArea(TA_IPLIST, format_cidr_list(IPList.iter_cidrs()), callFunction=False)


# Function used to format a list of networks from an iterated list of CIDRS
def format_cidr_list(list):
    formattedList = []
    for item in list:
        formattedList.append(str(item).split("/32")[0])

    return os.linesep.join(formattedList)


# Downloads and stores data from AWS
def refresh_data():
    global _raw_json
    try:
        response = urllib.urlopen(IP_DATA_URL)
        _raw_json = response.read()
    except:
        return

    process_data()
    update_service_list()
    update_region_list()
    update_ip_list()


# --- event handlers ---
# Process button clicks
def button__click(name):
    if name == BT_REFRESH:
        refresh_data()


# Process radio button changes
def radio_button__change(name):
    if name == RB_IPVERSION:
        update_service_list()
        update_region_list()
        update_ip_list()


# Process option box changes
def option_box__change(name):
    if name == OB_SERVICE:
        update_region_list()

    update_ip_list()


# --- gui builder ---
# - Main GUI
with gui(GUI_MAIN) as app:
    app.setResizable(False)

    app.setFont(17)
    app.setButtonFont(15)

    with app.frame(P_LEFT):
        app.setStretch("column")
        app.addButton(BT_REFRESH, refresh_data)

        app.addLabel(L_SERVICE, L_SERVICE)
        app.setLabelAlign(L_SERVICE, "left")
        app.addOptionBox(OB_SERVICE, ["AMAZON"])
        app.setOptionBoxChangeFunction(OB_SERVICE, option_box__change)
        app.setOptionBoxWidth(OB_SERVICE, 25)

        app.addLabel(L_REGION, L_REGION)
        app.setLabelAlign(L_REGION, "left")
        app.addOptionBox(OB_REGION, ["GLOBAL"])
        app.setOptionBoxChangeFunction(OB_REGION, option_box__change)
        app.setOptionBoxWidth(OB_REGION, 25)

    with app.frame(P_RIGHT, row=0, column=1):
        app.addScrolledTextArea(TA_IPLIST)

        with app.toggleFrame(TF_IPVERSION):
            app.addRadioButton(RB_IPVERSION, RB_IPV_IPV4)
            app.addRadioButton(RB_IPVERSION, RB_IPV_IPV6, row=0, column=1)
            app.setRadioButtonChangeFunction(RB_IPVERSION, radio_button__change)

    refresh_data()
