# coding=UTF-8
import json
import logging
import os

import urllib.request as urllib_combined

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
RB_IP_VERSION = "IPVersion"
RB_IPV_IPV4 = "IPv4"
RB_IPV_IPV6 = "IPv6"

# Text Area
TA_SYNC_TOKEN = "Sync Token"
TA_CREATE_DATE = "Creation Date"
TA_IP_LIST = "IP List"

# Option Box
OB_SERVICE = "Service"
OB_REGION = "Region"

# Toggle Frame
TF_IP_VERSION = "IP Version"

# Panes
P_LEFT = "Left"
P_RIGHT = "Right"


# --- functions ---
# Function processes raw JSON data and places it in the appropriate data variable
def process_data():
    global _raw_json, _ipv4_addresses, _ipv6_addresses

    processed_json = json.loads(_raw_json)
    _ipv4_addresses = processed_json['prefixes']
    _ipv6_addresses = processed_json['ipv6_prefixes']

    for ndx, _ in enumerate(_ipv4_addresses):
        _ipv4_addresses[ndx]['ip_prefix'] = IPNetwork(_ipv4_addresses[ndx]['ip_prefix'])

    for ndx, _ in enumerate(_ipv6_addresses):
        _ipv6_addresses[ndx]['ipv6_prefix'] = IPNetwork(_ipv6_addresses[ndx]['ipv6_prefix'])


# Function updates the service list from data stored
def update_service_list():
    global _ipv4_addresses, _ipv6_addresses
    environment_list = {}
    ip_version = app.getRadioButton(RB_IP_VERSION)

    if ip_version == RB_IPV_IPV4:
        for Address in _ipv4_addresses:
            environment_list[Address['service']] = str(Address['service'])

    if ip_version == RB_IPV_IPV6:
        for Address in _ipv6_addresses:
            environment_list[Address['service']] = Address['service']

    app.changeOptionBox(OB_SERVICE, sorted(environment_list, key=environment_list.__getitem__), callFunction=False)


# Function updates region list from data stored
def update_region_list():
    global _ipv4_addresses, _ipv6_addresses
    region_list = {}
    ip_version = app.getRadioButton(RB_IP_VERSION)
    service = app.getOptionBox(OB_SERVICE)

    if ip_version == RB_IPV_IPV4:
        for Address in _ipv4_addresses:
            if Address['service'] == service:
                region_list[Address['region']] = Address['region']

    if ip_version == RB_IPV_IPV6:
        for Address in _ipv6_addresses:
            if Address['service'] == service:
                region_list[Address['region']] = Address['region']

    app.changeOptionBox(OB_REGION, sorted(region_list, key=region_list.__getitem__), callFunction=False)


# Function updates IP list from data stored
def update_ip_list():
    global _ipv4_addresses, _ipv6_addresses
    ip_list = IPSet()

    app.clearTextArea(TA_IP_LIST, callFunction=False)

    ip_version = app.getRadioButton(RB_IP_VERSION)
    service = app.getOptionBox(OB_SERVICE)
    region = app.getOptionBox(OB_REGION)

    if ip_version == RB_IPV_IPV4:
        for Address in _ipv4_addresses:
            if Address['service'] == service and Address['region'] == region:
                ip_list.add(Address['ip_prefix'])

    if ip_version == RB_IPV_IPV6:
        for Address in _ipv6_addresses:
            if Address['service'] == service and Address['region'] == region:
                ip_list.add(Address['ipv6_prefix'])

    app.setTextArea(TA_IP_LIST, format_cidr_list(ip_list.iter_cidrs()), callFunction=False)


# Function used to format a list of networks from an iterated list of CIDRS
def format_cidr_list(cidr_list):
    formatted_list = []
    for item in cidr_list:
        formatted_list.append(str(item).split("/32")[0])

    return os.linesep.join(formatted_list)


# Downloads and stores data from AWS
def refresh_data():
    global _raw_json

    try:
        response = urllib_combined.urlopen(IP_DATA_URL)
    except BaseException as err:
        logging.warning("Unable to load URL: " + str(err))
        return

    _raw_json = response.read().decode('utf-8')

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
    if name == RB_IP_VERSION:
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
        app.addScrolledTextArea(TA_IP_LIST)

        with app.toggleFrame(TF_IP_VERSION):
            app.addRadioButton(RB_IP_VERSION, RB_IPV_IPV4)
            app.addRadioButton(RB_IP_VERSION, RB_IPV_IPV6, row=0, column=1)
            app.setRadioButtonChangeFunction(RB_IP_VERSION, radio_button__change)

    refresh_data()
