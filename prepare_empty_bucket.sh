#! /bin/bash

# this is a script to prepare the token bucket emptying script

# apt may not know about the iperf3 package unless updated first
sudo apt update --force-yes

# install iperf3
sudo apt install iperf3 --force-yes

# install python3 dependencies for the token measuring tool
pip3 install psutil
pip3 install numpy
