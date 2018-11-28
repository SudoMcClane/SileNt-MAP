#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse 	import ArgumentParser
import os
import subprocess
import time

parser = ArgumentParser()

parser.add_argument("-i", "--ips", help="File with IPs/IP ranges to scan (one per line)")
parser.add_argument("-p", "--ports", help="File with port list to scan (one per line: '80', '443' or '8000-8010')")
parser.add_argument("-n", "--number", default=5, help="Number of Ports/Port ranges to scan at the same time")
parser.add_argument("-d", "--delay", default=0, help="Pause between two scans (in seconds)")
parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Show additional messages")
parser.add_argument("-o", "--output", default="nmap_results", help="Directory name for scan results")

args = parser.parse_args()

while args.ips is None or not os.path.exists(args.ips):
    args.ips = raw_input("Enter the path of the file with IPs/IP ranges to scan: ")

while args.ports is None or not os.path.exists(args.ports):
    args.ports = raw_input("Enter the path of the file with Ports/Port ranges to scan: ")

if not os.path.exists(args.output):
    if args.verbose:
        print("Creating %s directory" % args.output)
    os.makedirs(args.output)

portfile = open(args.ports, "r")

portrange = portfile.readline().replace(os.linesep, "")
while portrange != "":
    for i in range(1, int(args.number)):
        line = portfile.readline()
        if line == "":
            break
        portrange += "," + line.replace(os.linesep, "")
    if args.verbose:
        print("Starting scanning ports %s" % portrange)
    ipfile = open(args.ips, "r")
    for iprange in ipfile:
        iprange = iprange.replace(os.linesep, "")
        if args.verbose:
            print("Starting scanning %s" % iprange)

        subprocess.call(['nmap', '-v', '-Pn', '-sS', iprange, '-p', portrange, '-oA', os.path.join(args.output, iprange.replace("/", "-") + "-p" + portrange.replace("-", "--").replace(",", "-"))])

        if args.verbose:
            print("%s scanned" % iprange)

        time.sleep(int(args.delay))
    ipfile.close()

    portrange = portfile.readline().replace(os.linesep, "")

portfile.close()
