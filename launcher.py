#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from termcolor import colored
import netifaces
import os
import queue
from random import shuffle
import subprocess
import sys
import threading
import time


def printBanner():
    """Print the program banner in the standard output
    """
    banner = ('  ██████  ██▓ ██▓    ▓█████  ███▄    █ ▄▄▄█████▓    ███▄ ▄███▓ '
              '▄▄▄       ██▓███  ' + os.linesep +
              '▒██    ▒ ▓██▒▓██▒    ▓█   ▀  ██ ▀█   █ ▓  ██▒ ▓▒   ▓██▒▀█▀ ██▒▒'
              '████▄    ▓██░  ██▒' + os.linesep +
              '░ ▓██▄   ▒██▒▒██░    ▒███   ▓██  ▀█ ██▒▒ ▓██░ ▒░   ▓██    ▓██░▒'
              '██  ▀█▄  ▓██░ ██▓▒' + os.linesep +
              '  ▒   ██▒░██░▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒░ ▓██▓ ░    ▒██    ▒██ ░'
              '██▄▄▄▄██ ▒██▄█▓▒ ▒' + os.linesep +
              '▒██████▒▒░██░░██████▒░▒████▒▒██░   ▓██░  ▒██▒ ░    ▒██▒   ░██▒ '
              '▓█   ▓██▒▒██▒ ░  ░' + os.linesep +
              '▒ ▒▓▒ ▒ ░░▓  ░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒   ▒ ░░      ░ ▒░   ░  ░ '
              '▒▒   ▓▒█░▒▓▒░ ░  ░' + os.linesep +
              '░ ░▒  ░ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░    ░       ░  ░      ░ '
              ' ▒   ▒▒ ░░▒ ░     ' + os.linesep +
              '░  ░  ░   ▒ ░  ░ ░      ░      ░   ░ ░   ░         ░      ░    '
              ' ░   ▒   ░░       ' + os.linesep +
              '      ░   ░      ░  ░   ░  ░         ░                    ░    '
              '     ░  ░         ' + os.linesep)
    print("{0}{1}{0}".format(os.linesep, colored(banner, "green")))


def ParseArgs():
    """Convert argument strings to objects and assign them as attributes of the
    namespace. Return the populated namespace.

    Returns
    -------
    namespace
        Namespace populated with argument string object.
    """

    parser = argparse.ArgumentParser(prog="launcher.py",
                                     description="Launch multiple port scans \
                                     on multiple IP ranges one after another")

    parser.add_argument("-i", "--ips", metavar="FILENAME", help="File with \
                        IPs/IP ranges to scan (one per line)")
    parser.add_argument("-p", "--ports", metavar="FILENAME", help="File with \
                        port list to scan (one per line: '80', 'T:443' or \
                        '8000-8010')")
    parser.add_argument("-d", "--delay", default=0, type=int,
                        help="Pause between two scans (in seconds)")
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
                        help="Show additional messages")
    parser.add_argument("type", choices={'oN', 'oX', 'oS', 'oG', 'oA'},
                        default='oA', help="Output type (See Nmap manpage)")
    parser.add_argument("-f", "--format", metavar="STRING", default="%s-p%s",
                        help="Output filenames format (STRING %% (ip, port))")
    parser.add_argument("-o", "--output", metavar="DIRECTORY",
                        default="nmap_results",
                        help="Directory name for scan results")
    parser.add_argument("--random", default=False, action="store_true",
                        help="Perform scans in a random order")
    parser.add_argument("--simulate", default=False, action="store_true",
                        help="Do not actually scan")
    parser.add_argument("-e", "--dev", metavar="DEVICE", default="eth0",
                        help="Network interface to use")
    parser.add_argument("--spoof-ip", metavar="FILENAME", help="File \
                        containing IP addresses used as source for Nmap (one \
                        per line). Retrieved using DHCP if empty")
    parser.add_argument("--spoof-mac", metavar="FILENAME", help="File \
                        containing MAC addresses used as source for Nmap (one \
                        per line)")
    parser.add_argument("additional", nargs=argparse.REMAINDER,
                        help="Additional arguments for Nmap")

    args = parser.parse_args()

    # Check that spoof-ip and spoof-file are specified or None
    if (args.spoof_ip is None) != (args.spoof_mac is None):
        print(colored("[-] Fatal error: --spoof-ip and --spoof-mac options \
                      must be used together", 'red'))
        parser.print_usage()
        exit(1)

    # Check that IPs and Ports lists exist and ask for the filenames if needed
    while args.ips is None or not os.path.exists(args.ips):
        args.ips = input("Enter the path of the file with IPs/IP ranges to \
                         scan: ")

    while args.ports is None or not os.path.exists(args.ports):
        args.ports = input("Enter the path of the file with Ports/Port ranges \
                           to scan: ")

    return args


def GetIPs(devName, spoofMACFile, spoofIPFile, verbose=False):
    """Retrieves IPs either in the provided file, or using DHCP

    Parameters
    ----------
    devName : string
        Ethernet device name (ex.: "eth0")
    spoofMACFile : file
        File containing MAC addresses to spoof
    spoofIPFile : file
        File containing IP addresses to spoof
    verbose : bool
        Enable verbosity (default=False)

    Returns
    -------
    [[string, string]]
        MAC / IP addresses couples retrieved
    """

    ips = []

    prevIPs = []
    for line in spoofIPFile:
        prevIPs.append(line.rstrip(os.linesep))

    for macAddress in spoofMACFile:

        # Remove trailing cariage return
        macAddress = macAddress.rstrip(os.linesep)

        # Verbose output
        if verbose:
            print(colored("[i] MAC retrieved from file: %s", 'yellow')
                  % macAddress)

        if prevIPs:

            ip = prevIPs.pop(0).rstrip(os.linesep)

            # Verbose output
            if verbose:
                print(colored("[i] IP retrieved from file: %s", 'yellow') % ip)

        else:

            # Verbose output
            if verbose:
                print(colored("[i] Setting %s down", 'yellow') % devName)

            # ip link set down dev eth0
            subprocess.call(["ip", "link", "set", "down", "dev", devName])

            # Verbose output
            if verbose:
                print(colored("[i] Setting %s as MAC address", 'yellow')
                      % macAddress)

            # ip link set dev eth0 address AA:BB:CC:DD:EE:FF
            subprocess.call(["ip", "link", "set", "dev", devName, "address",
                             macAddress])

            # Verbose output
            if verbose:
                print(colored("[i] Setting %s up", 'yellow') % devName)

            # ip link set up dev eth0
            subprocess.call(["ip", "link", "set", "up", "dev", devName])

            # Verbose output
            if verbose:
                print(colored("[i] Performing DHCP request", 'yellow'))

            # dhclient eth0
            subprocess.call(["dhclient", devName])
            # Retrieving IP address
            ip = netifaces.ifaddresses(devName)[netifaces.AF_INET][0]['addr'] \
                + "/" + \
                netifaces.ifaddresses(devName)[netifaces.AF_INET][0]['netmask']

            # Save IPs in the file
            spoofIPFile.write(ip + os.linesep)

            # Verbose output
            if verbose:
                print(colored("[i] New IP retrieved: %s", 'yellow') % ip)

        # Verbose output
        if verbose:
            print(colored("[+] IP - MAC couple: %s - %s", 'green')
                  % (ip, macAddress))

        ips.append([macAddress, ip])

    return ips


# Nmap calling function
def CallNmap(iprange, portrange, type, outDir, outFormat, args, verbose=False,
             simulate=False, iface=None, ip=None, mac=None):
    """Call Nmap with arguments.

    Parameters
    ----------
    iprange : string
        IP range to scan (ex.: "192.168.0.1/24")
    portrange : string
        Ports to scan (ex.: "80,T:443,8080-8090")
    type : string
        Nmap output format ("oG", "oS", "oA", "oX" or "oN")
    outDir : string
        Directory name for scan results
    outFormat : string
        Output filenames format (STRING % (ip, port))
    args : [string]
        Additional arguments for Nmap
    verbose : bool
        Enable verbosity (default=False)
    verbose : bool
        Enable verbosity (default=False)
    verbose : bool
        Enable verbosity (default=False)
    verbose : bool
        Enable verbosity (default=False)
    verbose : bool
        Enable verbosity (default=False)
    verbose : bool
        Enable verbosity (default=False)

    Returns
    -------
    [[string, string]]
        MAC / IP addresses couples retrieved
    """

    # Output filename
    outFile = os.path.join(outDir,
                           outFormat
                           % (iprange.replace("/", "-"),
                              portrange.replace("-", "--").replace(",", "-")))

    # Call Nmap
    if iface is None or ip is None:
        command = ['nmap', iprange, '-p', portrange, "-" + type, outFile] \
                 + args
    elif mac is None:
        command = ['nmap', iprange, '-p', portrange, "-" + type, outFile,
                   "-e", iface, "-S", ip.split('/')[0]] \
                 + args
    else:
        command = ['nmap', iprange, '-p', portrange, "-" + type, outFile,
                   "-e", iface, "-S", ip.split('/')[0], "--spoof-mac", mac] \
                 + args

    # Verbose output
    if verbose:
        print(colored("[+] Starting scanning %s:%s", 'yellow')
              % (iprange, portrange))
        print(colored(' '.join(command), 'white', 'on_blue'))

    stdout = open(outFile + ".stdout", "wb")
    stderr = open(outFile + ".stderr", "wb")
    if not simulate:
        subprocess.call(command, stdout=stdout, stderr=stderr)
    stdout.close()
    stderr.close()

    # Verbose output
    if verbose:
        print(colored("[+] %s:%s scanned", 'green') % (iprange, portrange))


# Class for multithreaded scans
class iFaceThread (threading.Thread):

    def __init__(self, id, ip, scanQueue, lock, type, outDir, outFormat, args,
                 verbose, iface, mac, delay, simulate):
        threading.Thread.__init__(self)
        self.id = id
        self.ip = ip
        self.scanQueue = scanQueue
        self.lock = lock
        self.type = type
        self.outDir = outDir
        self.outFormat = outFormat
        self.args = args
        self.verbose = verbose
        self.iface = iface
        self.mac = mac
        self.delay = delay
        self.simulate = simulate

    def run(self):

        # Create interface
        dev = self.iface

        # Quick & Dirty fix for -Pn & --spoof-mac incompatibility
        if "-Pn" in self.args:
            self.mac = None

        # Verbose output
        if self.verbose:
            print(colored("[i] Setting %s as MAC address", 'yellow')
                  % self.mac)

        # ip link set dev eth0 address AA:BB:CC:DD:EE:FF
        subprocess.call(["ip", "address", "add", self.ip, "dev", dev])

        while not self.scanQueue.empty():
            item = self.scanQueue.get()

            # Queue ends with "None"s
            if item is None:
                self.scanQueue.task_done()

                # Verbose output
                if self.verbose:
                    print(colored("[i] Stopping thread for interface %s/%s",
                                  'yellow')
                          % (self.ip, self.mac))

                break

            iprange = item[0]
            portrange = item[1]

            CallNmap(iprange, portrange, self.type, self.outDir,
                     self.outFormat, self.args, self.verbose, self.simulate,
                     dev, self.ip, self.mac)

            self.scanQueue.task_done()

            time.sleep(int(self.delay))


# Funcion creating ip/port couples to scan
def createScanQueue(ipFile, portFile, verbose):

    # Verbose output
    if verbose:
        print(colored("[i] Creating Scan Queue%s", 'yellow') % os.linesep)

    # create lists
    res = []
    ips = []

    # read files
    for ipRange in ipFile:
        ips.append(ipRange.strip(os.linesep))

    for portRange in portFile:

        # Remove \newline
        portRange = portRange.strip(os.linesep)

        for ipRange in ips:
            res += [[ipRange, portRange]]

            # Verbose output
            if verbose:
                print(colored("  Ip(s):\t%s%s  Port(s):\t%s%s", 'yellow')
                      % (ipRange, os.linesep, portRange, os.linesep))

    # Verbose output
    if verbose:
        print(colored("[i] Scan Queue created", 'yellow'))

    return res


# Create and launch Threads
def launchThreads(queueList, spoofIPFile, spoofMACFile, dev, type, delay,
                  outDir, outFormat, args, random, verbose, simulate):

    # Backup IP/MAC
    ipBack = netifaces.ifaddresses(dev)[netifaces.AF_INET][0]['addr'] + "/" \
            + netifaces.ifaddresses(dev)[netifaces.AF_INET][0]['netmask']
    macBack = netifaces.ifaddresses(dev)[netifaces.AF_LINK][0]['addr']

    # retrieve source IPs
    ips = GetIPs(dev, spoofMACFile, spoofIPFile, verbose)

    q = queue.Queue()
    for couple in queueList:
        q.put(couple)

    threads = []
    i = 0
    for couple in ips:
        t = iFaceThread(i, couple[1], q, None, type, outDir, outFormat, args,
                        verbose, dev, couple[0], delay, simulate)
        i = i + 1
        threads.append(t)
        t.start()
        # Add 'None' at the end of the queue to stop the thread
        q.put(None)

    # Wait for threads
    q.join()

    # Restore IP/MAC backup
    subprocess.call(["ip", "link", "set", "down", "dev", dev])
    subprocess.call(["ip", "link", "set", "dev", dev, "address", macBack])
    subprocess.call(["ip", "address", "add", ipBack, "dev", dev])
    subprocess.call(["ip", "link", "set", "up", "dev", dev])


# Main function
def Main():

    args = ParseArgs()

    printBanner()

    # Create the output directory
    if not os.path.exists(args.output):

        # Verbose output
        if args.verbose:
            print(colored("[i] Creating %s directory", 'yellow') % args.output)
        os.makedirs(args.output)

    portFile = open(args.ports, "r")        # already checked in ParseArgs()
    ipFile = open(args.ips, "r")

    queueList = createScanQueue(ipFile, portFile, args.verbose)

    # randomize
    if args.random:
        shuffle(queueList)

        # verbose output
        if args.verbose:
            print(colored("[!] Scan queue randomized", "yellow"))

    # cleaning
    portFile.close()
    ipFile.close()

    # Case multithread
    if args.spoof_ip:
        if not os.path.isfile(args.spoof_ip):
            os.mknod(args.spoof_ip)
        spoofIPFile = open(args.spoof_ip, "r+")
        spoofMacFile = open(args.spoof_mac, "r")

        launchThreads(queueList, spoofIPFile, spoofMacFile, args.dev,
                      args.type, args.delay,  args.output, args.format,
                      args.additional, args.random, args.verbose,
                      args.simulate)

        # Cleaning
        spoofIPFile.close()
        spoofMacFile.close()

    # Case not threaded
    else:
        for couple in queueList:
            # Call Nmap
            CallNmap(couple[0], couple[1], args.type, args.output, args.format,
                     args.additional, args.verbose, args.simulate)

            time.sleep(int(args.delay))

    # Verbose output
    if args.verbose:
        print(colored("[+] Scan finished", 'green'))

    sys.exit(0)


Main()
