#! /bin/bash

# the IP of the iperf3 server, which needs to be on
IPERF_SERVER=10.10.1.1

# network transfer time interval, in seconds
TRANSFER_INTERVAL=10

# number of trials for the experiment
NUM_TRIALS=10

for ((i=0; i<$NUM_TRIALS; i++)) ;
do
	echo "trial #$i"

	# start collecting data using tcpdump
	tcpdump host $IPERF_SERVER -w dumpfile.pcap -s 80 &

	# start the iperf3 client
	iperf3 -c $IPERF_SERVER -i 1 -t $TRANSFER_INTERVAL --json --logfile trial_${i}_iperf.data

	# stop the tcpdump process, send SIGINT
	pkill -2 tcpdump

	# run the tshark analysis
	time tshark -r dumpfile.pcap -Y "tcp.analysis.ack_rtt and ip.dst==$IPERF_SERVER/24" -e tcp.analysis.ack_rtt -T fields -E separator=,  > trial_${i}_rtt.data
done


