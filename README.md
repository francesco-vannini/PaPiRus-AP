# AP-PaPiRus-Pi-PoE
This script APInfo.py provides information about the status and the configuration of the AP via the PaPiRus screen.

The two additional files (hostapd.conf and interfaces) are configuration templates

# Installation
start Rasbian.

sudo raspi-config
  Expand the filesystem via
  Enable SPI

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install hostapd

git clone https://github.com/francesco-vannini/PaPiRus-AP.git

edit the hostapd.conf template file
sudo nano PaPiRus-AP/hostapd.conf
and replace the values below with your own

`#` This is the name of the network
ssid=<your SSID>
`#` The network passphrase
wpa_passphrase=<your wpa password>
copy the file hostapd.conf to the right directory

sudo cp PaPiRus-AP/hostapd.conf /etc/hostapd

sudo nano /etc/default/hostapd
change it by adding

DAEMON_CONF="/etc/hostapd/hostapd.conf"

sudo systemctl start hostapd

Disable dhcpcd
sudo systemctl disable dhcpcd

Install bridge-utils
sudo apt-get install bridge-utils

sudo nano PaPiRus-AP/interfaces
and change it

address <your AP IP address>
netmask <your home/office network mask>
gateway <your home/office gateway IP address>
dns-search <your interna domain (delete this line if you don't have one)>
dns-nameservers <your home/office DNS server (typically it will be the same as your gateway)>

backup your existing file
sudo mv /etc/network/interfaces /etc/network/interfaces.bck
and copy the new one
sudo cp PaPiRus-AP/interfaces /etc/network/

curl -sSL https://goo.gl/8uLA7s | sudo bash
sudo papirus-set 2.7

Test
sudo papirus-clock

Run

sudo python PaPiRus-AP/APInfo.py &

#Usage
Switch 1 shows your IP and SSID
Switch 2 displays some bandwidth stuff
Switch 3 a detailed view of the AP networking setup.
