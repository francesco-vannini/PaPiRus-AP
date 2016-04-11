#!/usr/bin/python

import os
import sys
import re
import time
from commands import *
from papirus import PapirusText
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep
import RPi.GPIO as GPIO

user = os.getuid()
if user != 0:
    print "Please run script as root"
    sys.exit()

# Command line usage
# papirus-buttons

WHITE = 1
BLACK = 0

L_SIZE = 25
M_SIZE = 20
S_SIZE = 15

SW1 = 16
SW2 = 26
SW3 = 20
SW4 = 21

def GetInterfacesStats():
    ret = {}
    f = open("/proc/net/dev", "r");
    data = f.read()
    f.close()

    r = re.compile("[:\s]+")

    lines = re.split("[\r\n]+", data)
    for line in lines[2:]:
        columns = r.split(line)
        if len(columns) < 18:
            continue
        info                  = {}
        info["rx_bytes"]      = columns[2]
        info["tx_bytes"]      = columns[10]
        iface                 = columns[1]
        ret[iface] = info
    return ret

def BytesPerSecond(interface):
        bandwidth = {'tx_bytes_t1': 0, 'rx_bytes_t1': 0, 'tx_bytes_t2': 0, 'rx_bytes_t2': 0};
        interfaceStats_t1 = GetInterfacesStats()
        bandwidth['tx_bytes_t1'] = interfaceStats_t1[interface]['tx_bytes']
        bandwidth['rx_bytes_t1'] = interfaceStats_t1[interface]['rx_bytes']
        time.sleep(1)

        interfaceStats_t2 = GetInterfacesStats()
        
        bandwidth['tx_bytes_t2'] = interfaceStats_t2[interface]['tx_bytes']
        bandwidth['rx_bytes_t2'] = interfaceStats_t2[interface]['rx_bytes']

        return {'delta_tx' : int(bandwidth['tx_bytes_t2']) - int(bandwidth['tx_bytes_t1']), 'delta_rx' : int(bandwidth['rx_bytes_t2']) - int(bandwidth['rx_bytes_t1'])}

def APName():
        hostapConf = open("/etc/hostapd/hostapd.conf","r")
        lines = hostapConf.readlines()
        for line in lines:
                words = line.split('=')
                if len(words) > 1:
                        for word in words:
                                if word == 'ssid':
                                        apName = words[1]

        return apName

def IPAddress():
        interfacesInfo = getoutput("ip addr show br0")
        interfacesInfoSplit = interfacesInfo.split()
        for index in range(0,len(interfacesInfoSplit)):
                if interfacesInfoSplit[index] == 'inet':
                        return (interfacesInfoSplit[index+1].split('/'))[0]
def InterfaceInfo():
        interfacesConf = open("/etc/network/interfaces","r")
        br0Conf = " "
        addToBr0Conf = False
        lines = interfacesConf.readlines()
        for index in range(0,len(lines)):
                words = lines[index].split()
                for word in words:
                        if word == "Bridge":
                                addToBr0Conf = True
                        elif word == "dns-nameservers":
                                addToBr0Conf = False
                if addToBr0Conf:
                        br0Conf += lines[index+1].lstrip()
        return br0Conf


def main():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SW1, GPIO.IN)
    GPIO.setup(SW2, GPIO.IN)
    GPIO.setup(SW3, GPIO.IN)
    GPIO.setup(SW4, GPIO.IN)

    interface = 'wlan0'
    scaleSpeed = 262144
    
    text = PapirusText()

    text.write("-4---3---2---1------\r\nPress 1 for basic info\r\nPress 2 for stats\r\nPress 3 for detailed info", S_SIZE)

    while True:
        if GPIO.input(SW1) == False:
            text.write("AP= " + APName() + "\r\n" + "IP= " + IPAddress(), L_SIZE)

        if GPIO.input(SW2) == False:
            while GPIO.input(SW1) and GPIO.input(SW3) and GPIO.input(SW4):
                netstats = BytesPerSecond(interface)
                print netstats
                text.write("Long press 1,3,4 exit\r\nBandwidth:"
                 + "\r\ntx: " + str(netstats['delta_tx']/1024)
                 + " Kb/s\r\n"
                 + "=" + ">"*(netstats['delta_tx']/scaleSpeed)
                 + "\r\nrx: " + str(netstats['delta_rx']/1024)
                 + " Kb/s\r\n"
                 + "=" + "<"*(netstats['delta_rx']/scaleSpeed), M_SIZE)
                time.sleep(5)

        if GPIO.input(SW3) == False:
            text.write(InterfaceInfo(), S_SIZE)

        if GPIO.input(SW4) == False:
            text.write("Four", M_SIZE)

        sleep(0.1)

if __name__ == '__main__':
    main()
