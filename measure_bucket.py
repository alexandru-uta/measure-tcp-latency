import boto.ec2
import sys
import boto3
import paramiko
import time
import os

# AWS access and secret keys
auth = {"aws_access_key_id": "", 
		"aws_secret_access_key": ""}

# regions
regions = ["eu-north-1", "ap-south-1", "eu-west-3", "eu-west-2", "eu-west-1",
		   "ap-northeast-2", "ap-northeast-1", "sa-east-1", "ca-central-1", 
		   "ap-southeast-1", "ap-southeast-2", "eu-central-1", "us-east-1", 
		   "us-east-2", "us-west-1", "us-west-2"]

# private key info
key_path = ""
key_name = ""

# instance attributes
region = "us-west-1"
instance_type = "c5.xlarge" 
ami_id = "ami-08fd8ae3806f09a08" # this is an ubuntu ami from us-west-1


def create_VM(vmid):
	# connect to given region
	boto3.setup_default_session(region_name = region)
	ec2_resource = boto3.resource('ec2')
	ec2_client   = boto3.client('ec2')
	vm_id = ""
	if (vmid == None):
		vm = ec2_resource.create_instances(ImageId = ami_id, InstanceType = instance_type, KeyName = key_name, MaxCount = 1, MinCount = 1)
		print vm[0].id
		vm_id = vm[0].id
		# give the VM time to boot up
		time.sleep(3 * 60)
	else:
		vm_id = vmid
	
	# get VM data
	result = ec2_client.describe_instances(InstanceIds = [vm_id])
	# get 1st entry
	vm_details = result["Reservations"][0]["Instances"][0]
	vm_result = {}
	# get public DNS and private IP
	vm_result["id"] = vm_id
	vm_result["public_dns"] = vm_details["PublicDnsName"]
	vm_result["private_ip"] = vm_details["NetworkInterfaces"][0]["PrivateIpAddresses"][0]["PrivateIpAddress"]
	# return VM data
	return vm_result

def prepare_VM(vm_info):
	# create the SSH connection
	key = paramiko.RSAKey.from_private_key_file(key_path)
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(hostname = vm_info["public_dns"], username = "ubuntu", pkey = key)
	# download repo
	stdin, stdout, stderr = client.exec_command("git clone https://github.com/alexandru-uta/measure-tcp-latency.git")
	print stdout.read()
	# install the needed packages
	stdin, stdout, stderr = client.exec_command("cd measure-tcp-latency ; chmod +x prepare_empty_bucket.sh ; ./prepare_empty_bucket.sh")
	print stdout.read()
	return client

def run_iperf(vm_info):
	stdin, stdout, stderr = vm_info["ssh_conn"].exec_command("nohup iperf3 -s")
	#stdout.read()

def run_empty_bucket(client_vm, server_vm):
	# create the SSH connection
	key = paramiko.RSAKey.from_private_key_file(key_path)
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(hostname = client_vm["public_dns"], username = "ubuntu", pkey = key)
	stdin, stdout, stderr = client.exec_command(
		"nohup python3 measure-tcp-latency/empty_bucket.py " + server_vm["private_ip"] + " &> raw_data.txt")
	stdout.read()
	
def check_token_file(vm_info):
	stdin, stdout, stderr = vm_info["ssh_conn"].exec_command("cat token_bucket.txt")
	error = stderr.read()
	if "No such" in error:
		# file is not there
		return None
	else:
		return stdout.read()
		
def grab_all_outputs(vm_info):
	stdin, stdout, stderr = vm_info["ssh_conn"].exec_command("cat raw_data.txt")
	raw_data = stdout.read()
	stdin, stdout, stderr = vm_info["ssh_conn"].exec_command("cat traffic_data.txt")
	traffic_data = stdout.read()
	return raw_data, traffic_data
		
def terminate_VMs(vm_IDs):
	boto3.setup_default_session(region_name = region)
	ec2_client = boto3.client('ec2')
	ec2_client.terminate_instances(InstanceIds = vm_IDs)
	print("VMs were terminated")
					
# create the VMs	
server_vm = create_VM(None)
print server_vm
client_vm = create_VM(None)
print client_vm

# prepare the VMs
server_vm["ssh_conn"] = prepare_VM(server_vm)
client_vm["ssh_conn"] = prepare_VM(client_vm)

pid = os.fork()
# run iperf3 on the server
if (pid > 0):
	run_iperf(server_vm)
	# poll client from time to time to see whether the emptying bucket script finished
	count = 3800 # do this for slightly more than an hour
	while count > 0:
		time.sleep(30)
		output = check_token_file(client_vm)
		if (output != None):
			print("token bucket output file = " + output)
			raw, traffic = grab_all_outputs(client_vm)
			timestamp = int(time.time())
			# create files
			filename_raw = "{}-{}-{}.{}".format(instance_type, region, timestamp, "raw")
			filename_bw = "{}-{}-{}.{}".format(instance_type, region, timestamp, "bw")
			filename_token = "{}-{}-{}.{}".format(instance_type, region, timestamp, "tb")
			# write the raw data from the VM
			f = open(filename_raw, "w")
			f.write(raw)
			f.close()
			# write the bw measured data from the VM
			f = open(filename_bw, "w")
			f.write(traffic)
			f.close()
			# write the token bucket data
			f = open(filename_token, "w")
			f.write(output)
			f.close()
			
			break
		else:
			print("token bucket not emptied yet")
		count -= 1
	# terminate the VMs
	terminate_VMs([server_vm["id"], client_vm["id"]])
	
else:
	# run empty-bucket.sh on client
	time.sleep(5)
	run_empty_bucket(client_vm, server_vm)
