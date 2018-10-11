#!/usr/bin/python
import argparse
import sys, subprocess
import time

params = {
    'GCI'  : 'gcloud compute instances',
    'ZONE' : 'us-west1-b',
    'INSTANCE_NAME' : 'myinstance',
    'TEMPLATE_NAME' : 'cpu-tiny',
  #  'DISK' : 'disk1'
}

cpu_types = {
    'cpu-tiny'  : 'f1-micro',      # $0.004, 1 cpu,  0.6 GB ram
    'cpu-small' : 'g1-small',      # $0.008, 1 cpu,  1.7 GB ram
    'cpu-mid'   : 'n1-standard-4', # $0.041, 4 cpu, 15.0 GB ram.
    'cpu-big'   : 'n1-standard-8', # $0.081, 8 cpu, 30.0 GB ram.

    'gpu-tiny'  : 'n1-standard-4', # $0.176, 4 cpu, 15.0 GB ram, 1 Nvidia K80
    'gpu-small' : 'n1-standard-4', # $0.257, 4 cpu, 15.0 GB ram, 1 Nvidia P4
    'gpu-mid'   : 'n1-standard-8', # $0.511, 4 cpu, 15.0 GB ram, 1 Nvidia P100
    'gpu-big'   : 'n1-standard-8', # $0.821, 4 cpu, 15.0 GB ram, 1 Nvidia V100
}

gpu_types = {
    'gpu-tiny'  : 'nvidia-tesla-k80',
    'gpu-small' : 'nvidia-tesla-p4',
    'gpu-mid'   : 'nvidia-tesla-p100',
    'gpu-big'   : 'nvidia-tesla-v100',
}

def start_func():
    create_func()
    ssh_func()
    delete_func()

def create_func(type='cpu-tiny'):
    cpu_type = cpu_types.get(type, "Invalid machine type")
    cpu_conf = '--machine-type={0} '.format(cpu_type)

    gpu_type = gpu_types.get(type);
    gpu_conf = '--accelerator=type={0},count=1 '.format(gpu_type) if gpu_type else ''

    disk_conf = '--disk=name={DISK},device-name={DISK},mode=rw,boot=no '.format(params.get('DISK')) \
                if  params.get('DISK') else ''

    cmd = '{GCI} create {INSTANCE_NAME} --preemptible --zone {ZONE} ' \
          '--image=c1-deeplearning-pytorch-0-4-cu92-20180925 --image-project=ml-images ' \
          '--boot-disk-size=30GB ' \
          ' '.format(**params)
    cmd = cmd + cpu_conf + gpu_conf + disk_conf
    return_code = subprocess.call( cmd, shell=True)

def delete_func():
    cmd ='{GCI} delete {INSTANCE_NAME} -q'.format( **params)
    return_code = subprocess.call(cmd, shell=True)
    list_func()

def list_func():
    cmd = '{GCI} list '.format( **params)
    return_code = subprocess.call(cmd, shell=True)

def ssh_func():
    cmd = 'gcloud compute ssh {INSTANCE_NAME} -- -L 8888:localhost:8888'.format( **params)
    return_code = subprocess.call(cmd, shell=True)

parser = argparse.ArgumentParser(description='gcloud compute instance.')
FUNCTION_MAP = {'start'  : start_func,
                'create' : create_func,
                'delete' : delete_func,
                'list'   : list_func,
                'ssh'    : ssh_func}

start = time.time()
parser.add_argument('command', choices=FUNCTION_MAP.keys())
args = parser.parse_args()
func = FUNCTION_MAP[args.command]
func()
print("Time taken = {0:.2f} Seconds ".format((time.time() - start)))





