import time
import psutil
import os
import subprocess
import math
import numpy as np
import signal
import sys

def main(SERVER_IP):
    # fork to start an iperf on the
    pid = os.fork()
    if (pid > 0):
        # parent monitors bw
        monitor_bw(pid)
    else:
        print("child")
        # child starts an iperf3 client
        subprocess.call(["iperf3", "-i", "1", "-t", "3600", "-c", SERVER_IP])
          
def to_gbit(value):
    return (8 * value) / (1000 * 1000 * 1000)

def check_bucket(bw_values):
    n = len(bw_values)
    median1 = np.median(bw_values[:10])
    median2 = np.median(bw_values[-10:])
    if median2 * 3 < median1:
        return True
    return False

def monitor_bw(iperf_pid):
    # get initial value
    old_value = psutil.net_io_counters().bytes_sent
    time.sleep(1)
    # store bw values
    bw_values = []
    # monitor crnt bw
    while True:
        # get bw
        new_value = psutil.net_io_counters().bytes_sent
        # print it
        print_stat(new_value - old_value)
        # add bw_value to bw array
        bw_values.append(to_gbit(new_value - old_value))
        # check if we got a drop in performance
        if (check_bucket(bw_values)):
            # we have identified a bucket
            print("it took %0.3f seconds to empty the bucket" % len(bw_values))
            print("big bw_value = %0.3f, small bw_value = %0.3f" % (bw_values[2], bw_values[len(bw_values) - 2]))
            os.kill(iperf_pid, signal.SIGINT)
            exit(0)

        old_value = new_value
        time.sleep(1)

def print_stat(value):
    print ("crnt bw = %0.3f" % to_gbit(value))

# you need to pass the IP of the server as the argument
main(sys.argv[1])


