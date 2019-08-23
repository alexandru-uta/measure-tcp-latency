ens1f1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
#! /bin/bash

## this is a script that installs iperf3, tshark/wireshark on ubuntu 18.04 - based machines
## and then runs iperf3 between two machines, gathers TCP packet data using tcpdump,
## and subsequently analyzes the packet rtt data using wireshark

# install iperf3
sudo apt install iperf3

# install tshark/wireshark
sudo add-apt-repository ppa:wireshark-dev/stable
sudo apt update
sudo apt -y install wireshark
sudo apt -y install tshark

# configure tshark
sudo usermod -a -G wireshark $USER
sudo chgrp wireshark /usr/bin/dumpcap
sudo chmod 750 /usr/bin/dumpcap
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap

# configure tcpdump
sudo groupadd pcap
sudo usermod -a -G pcap $USER
sudo chgrp pcap /usr/sbin/tcpdump
sudo chmod 750 /usr/sbin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump

echo "You now need to log out and log back in, otherwise the wireshark settings won't apply to this session"

