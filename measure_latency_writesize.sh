#! /bin/bash

# the IP of the iperf3 server, which needs to be on
IPERF_SERVER=172.30.0.41

# network transfer time interval, in seconds
TRANSFER_INTERVAL=10

# time to rest between tests: assume sending 10gbs for 10s, recharge at 1gbps
REST_TIME=`expr 10 \* 10`

# number of trials for the experiment
NUM_TRIALS=100

# write size increment
BASE_WRITESIZE=1460

for ((i=1; i<$NUM_TRIALS; i++)) ;
do
	WRITESIZE=`expr $i \* $BASE_WRITESIZE`
	echo "trial #$i ($WRITESIZE)"

	# start collecting data using tcpdump
	tcpdump host $IPERF_SERVER -w dumpfile.pcap -s 80 &

	# start the iperf3 client
	iperf3 -c $IPERF_SERVER -l $WRITESIZE -i 1 -t $TRANSFER_INTERVAL --json --logfile trial_${i}_iperf.data

	# stop the tcpdump process, send SIGINT
	pkill -2 tcpdump

	# run the tshark analysis
	time tshark -r dumpfile.pcap -Y "tcp.analysis.ack_rtt and ip.dst==$IPERF_SERVER/24" -e tcp.analysis.ack_rtt -T fields -E separator=,  > trial_${i}_rtt.data

	sleep $REST_TIME
done


