# coding=UTF-8
import json
import os
import urllib

from appJar import gui
from netaddr import *

# globals
Raw_JSON = str()
IPv4_Addresses = []
IPv6_Addresses = []

# constants
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


# functions
def ProcessData():
    global Raw_JSON, IPv4_Addresses, IPv6_Addresses

    Processed_JSON = json.loads(Raw_JSON)
    IPv4_Addresses = Processed_JSON['prefixes']
    IPv6_Addresses = Processed_JSON['ipv6_prefixes']

    for ndx, _ in enumerate(IPv4_Addresses):
        IPv4_Addresses[ndx]['ip_prefix'] = IPNetwork(IPv4_Addresses[ndx]['ip_prefix'])

    for ndx, _ in enumerate(IPv6_Addresses):
        IPv6_Addresses[ndx]['ipv6_prefix'] = IPNetwork(IPv6_Addresses[ndx]['ipv6_prefix'])


def UpdateServiceList():
    global IPv4_Addresses, IPv6_Addresses
    EnvironmentList = {}
    IPVersion = app.getRadioButton(RB_IPVERSION)

    if IPVersion == RB_IPV_IPV4:
        for Address in IPv4_Addresses:
            EnvironmentList[Address['service']] = Address['service']

    if IPVersion == RB_IPV_IPV6:
        for Address in IPv6_Addresses:
            EnvironmentList[Address['service']] = Address['service']

    app.changeOptionBox(OB_SERVICE, EnvironmentList, callFunction=False)


def UpdateRegionList():
    global IPv4_Addresses, IPv6_Addresses
    RegionList = {}
    IPVersion = app.getRadioButton(RB_IPVERSION)
    Service = app.getOptionBox(OB_SERVICE)

    if IPVersion == RB_IPV_IPV4:
        for Address in IPv4_Addresses:
            if Address['service'] == Service:
                RegionList[Address['region']] = Address['region']

    if IPVersion == RB_IPV_IPV6:
        for Address in IPv6_Addresses:
            if Address['service'] == Service:
                RegionList[Address['region']] = Address['region']

    app.changeOptionBox(OB_REGION, RegionList, callFunction=False)


def UpdateIPList():
    global IPv4_Addresses, IPv6_Addresses, Raw_JSON
    IPList = IPSet()

    app.clearTextArea(TA_IPLIST, callFunction=False)

    IPVersion = app.getRadioButton(RB_IPVERSION)
    Service = app.getOptionBox(OB_SERVICE)
    Region = app.getOptionBox(OB_REGION)

    if IPVersion == RB_IPV_IPV4:
        for Address in IPv4_Addresses:
            if Address['service'] == Service and Address['region'] == Region:
                IPList.add(Address['ip_prefix'])

    if IPVersion == RB_IPV_IPV6:
        for Address in IPv6_Addresses:
            if Address['service'] == Service and Address['region'] == Region:
                IPList.add(Address['ipv6_prefix'])

    app.setTextArea(TA_IPLIST, format_cidr_list(IPList.iter_cidrs()), callFunction=False)


def format_cidr_list(list):
    formattedList = []
    for item in list:
        formattedList.append(str(item).split("/32")[0])

    return os.linesep.join(formattedList)


def RefreshData():
    global Raw_JSON
    try:
        response = urllib.urlopen(IP_DATA_URL)
        Raw_JSON = response.read()
    except:
        return

    ProcessData()
    UpdateServiceList()
    UpdateRegionList()
    UpdateIPList()


# Event Handlers
def Button_Click(name):
    if name == BT_REFRESH:
        RefreshData()


def RadioButton_Change(name):
    if name == RB_IPVERSION:
        UpdateServiceList()
        UpdateRegionList()
        UpdateIPList()


def OptionBox_Change(name):
    if name == OB_SERVICE:
        UpdateRegionList()

    UpdateIPList()


# gui Builder
# - Main GUI
with gui(GUI_MAIN) as app:
    app.setResizable(False)

    app.setFont(17)
    app.setButtonFont(15)

    with app.frame(P_LEFT):
        app.setStretch("column")
        app.addButton(BT_REFRESH, RefreshData)

        app.addLabel(L_SERVICE, L_SERVICE)
        app.setLabelAlign(L_SERVICE, "left")
        app.addOptionBox(OB_SERVICE, ["AMAZON"])
        app.setOptionBoxChangeFunction(OB_SERVICE, OptionBox_Change)
        app.setOptionBoxWidth(OB_SERVICE, 25)

        app.addLabel(L_REGION, L_REGION)
        app.setLabelAlign(L_REGION, "left")
        app.addOptionBox(OB_REGION, ["GLOBAL"])
        app.setOptionBoxChangeFunction(OB_REGION, OptionBox_Change)
        app.setOptionBoxWidth(OB_REGION, 25)

    with app.frame(P_RIGHT, row=0, column=1):
        app.addScrolledTextArea(TA_IPLIST)

        with app.toggleFrame(TF_IPVERSION):
            app.addRadioButton(RB_IPVERSION, RB_IPV_IPV4)
            app.addRadioButton(RB_IPVERSION, RB_IPV_IPV6, row=0, column=1)
            app.setRadioButtonChangeFunction(RB_IPVERSION, RadioButton_Change)

    RefreshData()
