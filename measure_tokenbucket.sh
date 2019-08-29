#!/bin/bash

# the IP of the iperf3 server, which needs to be on
IPERF_SERVER=172.30.0.176

# network transfer time interval, in seconds
TRANSFER_INTERVAL=1200
#TRANSFER_INTERVAL=5

# number of trials for the experiment
NUM_TRIALS=20

# sleep interval (gets longer for each trial)
SLEEP=30
#SLEEP=1

# rest interval between trials
REST=3600
#REST=10

for ((i=0; i<$NUM_TRIALS; i++)) ;
do
	NOW=`date`
	echo "Resting for $REST (starting $NOW)"
	sleep $REST


	DATE=`date +%s`
	echo "trial #$i ($DATE)"

	echo "    iperf start"
	# start the iperf3 client
	iperf3 -c $IPERF_SERVER -i 1 -t $TRANSFER_INTERVAL --json --logfile trial_${i}_first_${DATE}_iperf.data
	echo "    iperf stop"

	SLEEPTIME=`expr $i \* $SLEEP`
	echo "sleeping for $SLEEPTIME"
	sleep $SLEEPTIME

	DATE=`date +%s`
	echo "    iperf start"
	iperf3 -c $IPERF_SERVER -i 1 -t $TRANSFER_INTERVAL --json --logfile trial_${i}_second_${DATE}_iperf.data
	echo "    iperf stop"

done


