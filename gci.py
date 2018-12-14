#!/usr/bin/python
import argparse
import sys, subprocess
import time

params = {
    'GCI'           : 'gcloud compute instances',
    'ZONE'          : 'us-west1-b',
    'INSTANCE_NAME' : 'myinstance',

    #'IMAGE'         : 'ubuntu-1804-bionic-v20181120',
    #'IMAGE_PROJECT' : 'ubuntu-os-cloud',
    #'IMAGE_PROJECT': 'ubuntu-os-cloud --metadata=\'install-nvidia-driver=True\'',

    #'IMAGE'         : 'c1-deeplearning-pytorch-1-0-cu100-20181210',
    #'IMAGE_PROJECT' : 'ml-images',

    'IMAGE_FAMILY' : 'pytorch-latest-gpu',
    'IMAGE_PROJECT': 'deeplearning-platform-release --metadata=\'install-nvidia-driver=True\'',
}

cpu_types = {
    'cpu-tiny'  : 'f1-micro',      # $0.004, 1 cpu,  0.6 GB ram
    'cpu-small' : 'g1-small',      # $0.008, 1 cpu,  1.7 GB ram
    'cpu-mid'   : 'n1-standard-4', # $0.041, 4 cpu, 15.0 GB ram.
    'cpu-big'   : 'n1-standard-8', # $0.081, 8 cpu, 30.0 GB ram.

    'gpu-tiny'  : 'n1-highmem-2',  # $0.176, 4 cpu, 15.0 GB ram, 1 Nvidia K80
    'gpu-small' : 'n1-highmem-2',  # $0.257, 4 cpu, 15.0 GB ram, 1 Nvidia P4
    'gpu-mid'   : 'n1-standard-8', # $0.511, 8 cpu, 30.0 GB ram, 1 Nvidia P100
    'gpu-big'   : 'n1-standard-8', # $0.821, 8 cpu, 30.0 GB ram, 1 Nvidia V100
}

gpu_types = {
    'gpu-tiny'  : 'nvidia-tesla-k80',
    'gpu-small' : 'nvidia-tesla-p4',
    'gpu-mid'   : 'nvidia-tesla-p100',
    'gpu-big'   : 'nvidia-tesla-v100',
}

def getMachineType(type) :
    if type is None:
        type = 'cpu-tiny'
    cpu_type = cpu_types.get(type, "Invalid machine type")
    cpu_conf = '--machine-type={0} '.format(cpu_type)

    gpu_type = gpu_types.get(type);
    gpu_conf = '--accelerator=type={0},count=1 '.format(gpu_type) if gpu_type else ''

    return cpu_conf + gpu_conf

def start_func(args=None):
    if args is not None and args.instance :
        cmd = '{GCI} set-machine-type {INSTANCE_NAME} --zone {ZONE} '.format( **params)
        cmd = cmd + getMachineType(args.instance)
        subprocess.check_call(cmd, shell=True)

    cmd ='{GCI} start {INSTANCE_NAME} --zone {ZONE} '.format( **params)
    subprocess.check_call(cmd, shell=True)
    list_func()

def stop_func(args=None):
    cmd ='{GCI} stop {INSTANCE_NAME} --zone {ZONE} '.format( **params)
    subprocess.check_call(cmd, shell=True)
    list_func()

def restart_func(args=None):
    stop_func()
    start_func()

def create_func(args):
    cmd = '{GCI} create {INSTANCE_NAME} --preemptible --zone {ZONE} ' \
          '--image-family={IMAGE_FAMILY} --image-project={IMAGE_PROJECT} ' \
          '--boot-disk-size=50GB ' \
          ' '.format(**params)
    cmd = cmd + getMachineType(args.instance)
    subprocess.check_call( cmd, shell=True)

def delete_func(args=None):
    cmd ='{GCI} delete {INSTANCE_NAME} --zone {ZONE} '.format( **params)
    subprocess.check_call(cmd, shell=True)
    list_func()

def list_func(args=None):
    cmd = '{GCI} list '.format( **params)
    subprocess.check_call(cmd, shell=True)

def ssh_func(args=None):
    cmd = 'gcloud compute ssh {INSTANCE_NAME} --zone {ZONE} -- -L 8888:localhost:8888'.format( **params)
    subprocess.check_call(cmd, shell=True)

def scp_func(args):
    start = time.time()
    cmd = 'gcloud compute scp --recurse --compress {0} {1}'.format(args.src, args.dest)
    print('scp command {0}'.format(cmd))
    subprocess.check_call(cmd, shell=True)
    print("Time taken for scp = {0:.2f} Seconds ".format((time.time() - start)))

parser = argparse.ArgumentParser(description='gcloud compute instance utility')
subparsers = parser.add_subparsers()

# create parsers for each sub-command
sub_parser = subparsers.add_parser('start', help='start the instance')
sub_parser.add_argument('instance', choices=cpu_types.keys(), nargs='?')
sub_parser.set_defaults(func=start_func)

sub_parser = subparsers.add_parser('stop', help='stop instance')
sub_parser.set_defaults(func=stop_func)

sub_parser = subparsers.add_parser('restart', help='restart instance')
sub_parser.set_defaults(func=restart_func)

sub_parser = subparsers.add_parser('create', help='create an instance')
sub_parser.add_argument('instance', choices=cpu_types.keys(), nargs='?')
sub_parser.set_defaults(func=create_func)

sub_parser = subparsers.add_parser('delete', help='delete the instance')
sub_parser.set_defaults(func=delete_func)

sub_parser = subparsers.add_parser('list', help='list all instances')
sub_parser.set_defaults(func=list_func)

sub_parser = subparsers.add_parser('ssh', help='ssh to the instance')
sub_parser.set_defaults(func=ssh_func)

sub_parser = subparsers.add_parser('scp', help='scp to the instance')
sub_parser.add_argument('src',   nargs='?')
sub_parser.add_argument('dest',  nargs='?')
sub_parser.set_defaults(func=scp_func)

start = time.time()
args = parser.parse_args()
args.func(args)
print("Time taken = {0:.2f} Seconds ".format((time.time() - start)))





