# measure-tcp-latency

This is a set of scripts for measuring the latency seen during TCP transfers between two machines.

The scripts are designed for Ubuntu 18.04 machines in which the user has root access.

Usage:
1) Run the ./install_dependencies.sh script on both machines and follow the extra instructions.
2) On the server machine, run iperf3 as a server: iperf3 -s .
3) On the client machine, edit the measure_latency.sh script to match the IP of the server machine and the other parameters that are of interest (the measurement interval, how many measurements etc.).
4) Run ./measure_latency.sh .
5) Analyze the contents of the result files.


