#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from termcolor import colored
import os
import subprocess
import time

# Parsing arguments
parser = argparse.ArgumentParser(prog="nmap_launcher.py",
        description="Launch multiple port scans on multiple IP ranges one after another")

parser.add_argument("-i", "--ips", metavar="FILENAME",
        help="File with IPs/IP ranges to scan (one per line)")
parser.add_argument("-p", "--ports", metavar="FILENAME",
        help="File with port list to scan (one per line: '80', 'T:443' or '8000-8010')")
parser.add_argument("-n", "--number", default=5, type=int,
        help="Number of Ports/Port ranges to scan at the same time")
parser.add_argument("-d", "--delay", default=0, type=int,
        help="Pause between two scans (in seconds)")
parser.add_argument("-v", "--verbose", default=False, action="store_true",
        help="Show additional messages")
parser.add_argument("type", choices={'oN', 'oX', 'oS', 'oG', 'oA'}, default='oA',
        help="Output type (See Nmap manpage)")
parser.add_argument("-f", "--format", metavar="STRING", default="%s-p%s",
        help='Output filenames format (STRING °/. (ip, port))')
parser.add_argument("-o", "--output", metavar="DIRECTORY", default="nmap_results",
        help="Directory name for scan results")
parser.add_argument("additional", nargs=argparse.REMAINDER,
        help="Additional arguments for nmap")

args = parser.parse_args()

# Check that IPs and Ports lists exist and ask for the filenames if needed
while args.ips is None or not os.path.exists(args.ips):
    args.ips = raw_input("Enter the path of the file with IPs/IP ranges to scan: ")

while args.ports is None or not os.path.exists(args.ports):
    args.ports = raw_input("Enter the path of the file with Ports/Port ranges to scan: ")

# Create the output directory
if not os.path.exists(args.output):
    if args.verbose:
        print(colored("[i] Creating %s directory", 'yellow') % args.output)
    os.makedirs(args.output)

portfile = open(args.ports, "r")

portrange = portfile.readline().replace(os.linesep, "")
while portrange != "":                      # Until the is no port left
    for i in range(1, int(args.number)):    # Concatenate ports ex: "80,443,8010-8020"
        line = portfile.readline()
        if line == "":
            break
        portrange += "," + line.replace(os.linesep, "")
    if args.verbose:
        print(colored("[i] Starting scanning ports %s", 'yellow') % portrange)

    ipfile = open(args.ips, "r")
    for iprange in ipfile:                  # Until every IP has been scanned
        iprange = iprange.replace(os.linesep, "")

        # Call Nmap
        command = ['nmap', iprange, '-p', portrange, "-" + args.type,
                os.path.join(args.output, args.format % (iprange.replace("/", "-"),
                    portrange.replace("-", "--").replace(",", "-")))] + args.additional
                
        if args.verbose:
            print(colored("[+] Starting scanning %s:%s", 'yellow') % (iprange, portrange))
            print(colored(' '.join(command), 'white', 'on_blue'))
        
        subprocess.call(command)

        if args.verbose:
            print(colored("[+] %s:%s scanned", 'green') % (iprange, portrange))

        time.sleep(int(args.delay))
    ipfile.close()

    portrange = portfile.readline().replace(os.linesep, "")

portfile.close()

if args.verbose:
    print(colored("[+] Scan finished", 'green'))
