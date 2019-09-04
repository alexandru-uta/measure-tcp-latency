#! /bin/bash

# this is a script to prepare the token bucket emptying script

# apt may not know about the iperf3 package unless updated first
sudo apt-get -y update --allow-downgrades --allow-remove-essential --allow-change-held-packages

# install iperf3
sudo apt-get -y install iperf3 --allow-downgrades --allow-remove-essential --allow-change-held-packages

# install python3 dependencies for the token measuring tool
sudo apt-get -y install python3-pip --allow-downgrades --allow-remove-essential --allow-change-held-packages
pip3 install psutil
pip3 install numpy
