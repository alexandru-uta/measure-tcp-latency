import time
import psutil
import os
import subprocess
import math
import numpy as np
import signal
import sys

outfile_bucket = "token_bucket.txt"
outfile_data = "traffic_data.txt"
TIMEOUT = 7200

def main(SERVER_IP):
    # fork to start an iperf on the
    pid = os.fork()
    if (pid > 0):
        # parent monitors bw
        monitor_bw(pid)
    else:
        print("child")
        # child starts an iperf3 client
        subprocess.call(["iperf3", "-i", "1", "-t", str(TIMEOUT), "-c", SERVER_IP])
          
def to_gbit(value):
    return (8 * value) / (1000 * 1000 * 1000)

def check_bucket(bw_values):
    n = len(bw_values)
    min1 = np.min(bw_values[:10])
    max2 = np.max(bw_values[-10:])
    # this parameter (3) here may need to be changed in case the low
    # bandwidth of the token bucket does not fit the formula
    if min1 * 0.75 > max2:
        return True
    return False

def monitor_bw(iperf_pid):
    # get initial value
    old_value = psutil.net_io_counters().bytes_sent
    time.sleep(1)
    # store bw values
    bw_values = []
    # monitor crnt bw
    count = 0
    f2 = open(outfile_data, "w")
    while True:
        # get bw
        new_value = psutil.net_io_counters().bytes_sent
        # print it
        print_stat(f2, new_value - old_value)
        # add bw_value to bw array
        bw_values.append(to_gbit(new_value - old_value))
        # check if we got a drop in performance
        if (check_bucket(bw_values)):
            # we have identified a bucket
            print("it took %0.3f seconds to empty the bucket" % len(bw_values))
            print("big bw_value = %0.3f, small bw_value = %0.3f" % (bw_values[2], bw_values[len(bw_values) - 2]))
            f = open(outfile_bucket, "w")
            f.write("%0.3f,%0.3f,%0.3f\n" % (len(bw_values), bw_values[2], bw_values[len(bw_values) - 2]))
            f.close()
            f2.close()
            os.kill(iperf_pid, signal.SIGINT)
            exit(0)

        old_value = new_value
        time.sleep(1)
        count += 1
        if (count > TIMEOUT):
            f = open(outfile_bucket, "w")
            f.write("no bucket identified")
            f.close()
            f2.close()
            break

def print_stat(f, value):
    f.write("crnt bw = %0.3f\n" % to_gbit(value))

# you need to pass the IP of the server as the argument
main(sys.argv[1])


