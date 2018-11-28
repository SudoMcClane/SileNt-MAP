#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse 	import ArgumentParser
import os
import subprocess
import time

parser = ArgumentParser()

parser.add_argument("-f", "--file", help="File with IPs/IP ranges to scan (one per line)")
parser.add_argument("-d", "--delay", default=0, help="Pause between two scans (in seconds)")
parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Show additional messages")
parser.add_argument("-p", "--ports", default="80,443", help="Port list to scan (Nmap format: '80,443,8000-8010')")
parser.add_argument("-o", "--output", default="nmap_results", help="Directory name for scan results")

args = parser.parse_args()

while args.file is None or not os.path.exists(args.file):
    args.file = raw_input("Enter the path of the file with IPs/IP ranges to scan:")

if not os.path.exists(args.output):
    if args.verbose:
        print("Creating %s directory" % args.output)
    os.makedirs(args.output)

file = open(args.file, "r")

for range in file:
    range = range.replace(os.linesep, "")
    if args.verbose:
        print("Starting scanning %s" % range)

    subprocess.call(['nmap', '-v', '-Pn', '-sS', '-p', args.ports, range, '-oA', os.path.join(args.output, range.replace("/", "-") + "-p" + args.ports.replace("-", "--").replace(",", "-"))])

    if args.verbose:
        print("%s scanned" % range)

    time.sleep(int(args.delay))
