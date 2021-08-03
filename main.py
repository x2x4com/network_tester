#!/usr/bin/env python3
# encoding: utf-8
# ===============================================================================
#
#         FILE:  
#
#        USAGE:    
#
#  DESCRIPTION:  
#
#      OPTIONS:  ---
# REQUIREMENTS:  ---
#         BUGS:  ---
#        NOTES:  ---
#       AUTHOR:  YOUR NAME (), 
#      COMPANY:  
#      VERSION:  1.0
#      CREATED:  
#     REVISION:  ---
# ===============================================================================

import subprocess
from prettytable import PrettyTable
import re

# data from http://ec2-reachability.amazonaws.com/
# (Vendor, Region, RegionId, Location, ip)
targets = [
    ("AWS", "US EAST", "us-east-1", "North Virginia", "44.192.0.0"),
    ("AWS", "US EAST", "us-east-1-bos-1", "Boston", "68.66.113.112"),
    ("AWS", "US EAST", "us-east-1-dfw-1", "Dallas", "15.181.192.183"),
    ("AWS", "US EAST", "us-east-1-iah-1", "Houston", "72.41.10.180"),
    ("AWS", "US EAST", "us-east-1-mia-1", "Miami", "64.187.131.1"),
    ("AWS", "US EAST", "us-east-1-phl-1", "Philadelphia", "15.181.144.146"),
    ("AWS", "US EAST", "us-east-2", "Ohio", "13.58.0.253"),
    ("AWS", "US WEST", "us-west-1", "North California", "50.18.56.1"),
    ("AWS", "US WEST", "us-west-2", "Oregon", "34.208.63.251"),
    ("AWS", "US WEST", "us-west-2-den-1", "Denver", "15.181.17.111"),
    ("AWS", "US WEST", "us-west-2-lax-1", "Los Angeles", "15.253.128.254"),
    ("AWS", "CANADA", "ca-central-1", "Central", "35.182.0.251"),
    ("AWS", "SOUTH AMERICA", "sa-east-1", "São Paulo", "52.67.255.254"),
    ("AWS", "EU", "eu-west-1", "Ireland", "34.248.60.213"),
    ("AWS", "EU", "eu-central-1", "Frankfurt", "52.29.63.252"),
    ("AWS", "EU", "eu-west-2", "London", "18.168.0.0"),
    ("AWS", "EU", "eu-south-1", "Milan", "15.161.0.254"),
    ("AWS", "EU", "eu-west-3", "Paris", "15.236.0.0"),
    ("AWS", "EU", "eu-north-1", "Stockholm", "13.53.128.254"),
    ("AWS", "AFRICA", "af-south-1", "Cape Town", "13.245.0.253"),
    ("AWS", "MIDDLE EAST", "me-south-1", "Bahrain", "157.175.10.11"),
    ("AWS", "ASIA PACIFIC", "ap-northeast-1", "Tokyo", "46.51.255.254"),
    ("AWS", "ASIA PACIFIC", "ap-northeast-2", "Seoul", "3.36.0.0"),
    ("AWS", "ASIA PACIFIC", "ap-southeast-1", "Singapore", "18.142.0.0"),
    ("AWS", "ASIA PACIFIC", "ap-northeast-3", "Osaka", "13.208.32.253"),
    ("AWS", "ASIA PACIFIC", "ap-southeast-2", "Sydney", "54.66.0.2"),
    ("AWS", "ASIA PACIFIC", "ap-south-1", "Mumbai", "15.206.0.0"),
    ("AWS", "ASIA PACIFIC", "ap-east-1", "Hong Kong", "18.166.0.253"),
    ("AWS", "CHINA", "cn-north-1", "Beijing", "140.179.0.253"),
    ("AWS", "CHINA", "cn-northwest-1", "Ningxia", "161.189.0.253")
]

# print('Start ping...')

jobs = list()

for t in targets:
    p = subprocess.Popen("LANG=C ping -c 10 {}".format(t[4]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    jobs.append({"info": t, "job": p})

# print("Wait for ping finish...")

for job in jobs:
    job["job"].wait()
    stdout = job["job"].stdout.read()
    stderr = job["job"].stderr.read()
    if type(stdout) == bytes:
        stdout = stdout.decode()
    if type(stderr) == bytes:
        stderr = stderr.decode()
    job.update({
        "code": job["job"].returncode,
        "stdout": stdout,
        "stderr": stderr,
    })
    del job["job"]

# print("Ping finished")

table = PrettyTable()
table.field_names = ('Vendor', 'Region', 'RegionId', 'Location', 'Ip', 'Send', 'Rec', 'Lost', 'Min', 'Max', 'Avg')

# mac '10 packets transmitted, 10 packets received, 0.0% packet loss',
# linux '3 packets transmitted, 3 received, 0% packet loss, time 2003ms'
find_lost = re.compile(
    r'^(?P<send>\d+) packets transmitted, (?P<rec>\d+) (?:packets )?received, (?P<lost>\d+(?:\.\d+)?%) packet loss.*'
)

# mac 'round-trip min/avg/max/stddev = 8.808/10.074/13.203/1.458 ms'
# linux 'rtt min/avg/max/mdev = 49.440/49.540/49.647/0.084 ms'

find_delay = re.compile(
    r'^(?:round-trip|rtt) min/avg/max/(?:stddev|mdev) = (?P<min>\d+(?:\.\d+)?)/(?P<avg>\d+(?:\.\d+)?)/(?P<max>\d+(?:\.\d+)?)/.*'
)

for job in jobs:
    rt = job['stdout'].split('\n')
    send = None
    rec = None
    lost = None
    p_min = None
    p_avg = None
    p_max = None
    for line in rt:
        t = find_lost.search(line)
        if t is not None:
            lost = t.groupdict()['lost']
            send = t.groupdict()['send']
            rec = t.groupdict()['rec']
            continue
        t = find_delay.search(line)
        if t is not None:
            p_min = t.groupdict()['min']
            p_avg = t.groupdict()['avg']
            p_max = t.groupdict()['max']
    table.add_row([job['info'][0], job['info'][1], job['info'][2], job['info'][3], job['info'][4], send, rec, lost, p_min, p_max, p_avg])

print(table)
