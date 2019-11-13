#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silent Map main file.

Author: Clément Gatefait
Date: 28/11/2018
"""


import argparse
from termcolor import colored
import netifaces
import os
import queue
from random import randint
from random import shuffle
import subprocess
import sys
import threading
import time
import beautiful


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
    parser.add_argument("-b", "--beautiful", default=False,
                        action="store_true", help="Use the beautiful ouput")
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


def GetIPs(devName, spoofMACFile, spoofIPFile, verbose=False, simulate=False,
           beauty=None):
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
        out = colored("[i] MAC retrieved from file: %s", 'yellow') % macAddress
        if beauty:
            beauty.addComment(out)
        if verbose:
            print(out)

        if prevIPs:

            ip = prevIPs.pop(0).rstrip(os.linesep)

            # Verbose output
            out = colored("[i] IP retrieved from file: %s", 'yellow') % ip
            if beauty:
                beauty.addComment(out)
            if verbose:
                print(out)

        else:

            # Verbose output
            out = colored("[i] Setting %s down", 'yellow') % devName
            if beauty:
                beauty.addComment(out)
            if verbose:
                print(out)

            if not simulate:
                # ip link set down dev eth0
                subprocess.call(["ip", "link", "set", "down", "dev", devName])

            # Verbose output
            out = (colored("[i] Setting %s as MAC address", 'yellow')
                   % macAddress)
            if beauty:
                beauty.addComment(out)
            if verbose:
                print(out)

            if not simulate:
                # ip link set dev eth0 address AA:BB:CC:DD:EE:FF
                subprocess.call(["ip", "link", "set", "dev", devName,
                                 "address", macAddress])

            # Verbose output
            out = colored("[i] Setting %s up", 'yellow') % devName
            if beauty:
                beauty.addComment(out)
            if verbose:
                print(out)

            if not simulate:
                # ip link set up dev eth0
                subprocess.call(["ip", "link", "set", "up", "dev", devName])

            # Verbose output
            out = colored("[i] Performing DHCP request", 'yellow')
            if beauty:
                beauty.addComment(out)
            if verbose:
                print(out)

            if not simulate:
                # dhclient eth0
                subprocess.call(["dhclient", devName])
            # Retrieving IP address
            ip = netifaces.ifaddresses(devName)[netifaces.AF_INET][0]['addr'] \
                + "/" + \
                netifaces.ifaddresses(devName)[netifaces.AF_INET][0]['netmask']

            if not simulate:
                # Save IPs in the file
                spoofIPFile.write(ip + os.linesep)

            # Verbose output
            out = colored("[i] New IP retrieved: %s", 'yellow') % ip
            if beauty:
                beauty.addComment(out)
            if verbose:
                print(out)

        # Verbose output
        out = (colored("[+] IP - MAC couple: %s - %s", 'green')
               % (ip, macAddress))
        if beauty:
            beauty.addComment(out)
        if verbose:
            print(out)

        ips.append([macAddress, ip])

    return ips


# Nmap calling function
def CallNmap(iprange, portrange, type, outDir, outFormat, args, verbose=False,
             simulate=False, iface=None, ip=None, mac=None, beauty=None):
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
    out = (colored("[+] Starting scanning %s:%s", 'yellow')
           % (iprange, portrange))
    out += os.linesep + colored(' '.join(command), 'white', 'on_blue')
    if beauty:
        beauty.addComment(out)
        for port in portrange.split(','):
            beauty.doPort(iprange, port, 1)
    if verbose:
        print(out)

    stdout = open(outFile + ".stdout", "wb")
    stderr = open(outFile + ".stderr", "wb")
    if not simulate:
        subprocess.call(command, stdout=stdout, stderr=stderr)
    else:
        rnd = randint(1, 10)
        time.sleep(rnd/10.0)
    stdout.close()
    stderr.close()

    # Verbose output
    out = colored("[+] %s:%s scanned", 'green') % (iprange, portrange)
    if beauty:
        beauty.addComment(out)
        for port in portrange.split(','):
            beauty.doPort(iprange, port, 2)
    if verbose:
        print(out)


# Class for multithreaded scans
class iFaceThread(threading.Thread):

    def __init__(self, id, ip, scanQueue, lock, type, outDir, outFormat, args,
                 verbose, iface, mac, delay, simulate, beauty):
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
        self.beauty = beauty

    def run(self):

        # Create interface
        dev = self.iface

        # Quick & Dirty fix for -Pn & --spoof-mac incompatibility
        if "-Pn" in self.args:
            self.mac = None

        # Verbose output
        out = colored("[i] Setting %s as MAC address", 'yellow') % self.mac
        if self.beauty:
            self.beauty.addComment(out)
        if self.verbose:
            print(out)

        if not self.simulate:
            # ip link set dev eth0 address AA:BB:CC:DD:EE:FF
            subprocess.call(["ip", "address", "add", self.ip, "dev", dev])

        while not self.scanQueue.empty():
            item = self.scanQueue.get()

            # Queue ends with "None"s
            if item is None:
                self.scanQueue.task_done()

                # Verbose output
                out = (colored("[i] Stopping thread for interface %s/%s",
                               'yellow')
                       % (self.ip, self.mac))
                if self.beauty:
                    self.beauty.addComment(out)
                if self.verbose:
                    print(out)

                break

            iprange = item[0]
            portrange = item[1]

            CallNmap(iprange, portrange, self.type, self.outDir,
                     self.outFormat, self.args, self.verbose, self.simulate,
                     dev, self.ip, self.mac, self.beauty)

            self.scanQueue.task_done()

            time.sleep(int(self.delay))


# Funcion creating ip/port couples to scan
def createScanQueue(ipFile, portFile, verbose, beauty):

    # create lists
    res = []
    ips = []
    ports = []

    # read files
    for ipRange in ipFile:
        ips.append(ipRange.strip(os.linesep))

    for portRange in portFile:

        # Remove \newline
        ports.append(portRange.strip(os.linesep))

    # Beautiful
    if beauty:
        beauty.initLists(ips, ports)

    # Verbose output
    out = colored("[i] Creating Scan Queue%s", 'yellow') % os.linesep
    if beauty:
        beauty.addComment(out)
    if verbose:
        print(out)

    for portRange in ports:
        for ipRange in ips:
            res += [[ipRange, portRange]]

            # Verbose output
            out = (colored("  Ip(s):\t%s%s  Port(s):\t%s%s", 'yellow')
                   % (ipRange, os.linesep, portRange, os.linesep))
            if beauty:
                beauty.addComment(out)
            elif verbose:
                print(out)

    # Verbose output
    out = colored("[i] Scan Queue created", 'yellow')
    if beauty:
        beauty.addComment(out)
    elif verbose:
        print(out)

    return res


# Create and launch Threads
def launchThreads(queueList, spoofIPFile, spoofMACFile, dev, type, delay,
                  outDir, outFormat, args, random, verbose, simulate, beauty):

    # Backup IP/MAC
    ipBack = netifaces.ifaddresses(dev)[netifaces.AF_INET][0]['addr'] + "/" \
            + netifaces.ifaddresses(dev)[netifaces.AF_INET][0]['netmask']
    macBack = netifaces.ifaddresses(dev)[netifaces.AF_LINK][0]['addr']

    # retrieve source IPs
    ips = GetIPs(dev, spoofMACFile, spoofIPFile, verbose, simulate, beauty)

    q = queue.Queue()
    for couple in queueList:
        q.put(couple)

    threads = []
    i = 0
    for couple in ips:
        # Add 'None' at the end of the queue to stop the thread
        q.put(None)
        t = iFaceThread(i, couple[1], q, None, type, outDir, outFormat, args,
                        verbose, dev, couple[0], delay, simulate, beauty)
        i = i + 1
        threads.append(t)
        t.start()

    # Wait for threads
    q.join()

    # Restore IP/MAC backup
    if not simulate:
        subprocess.call(["ip", "link", "set", "down", "dev", dev])
        subprocess.call(["ip", "link", "set", "dev", dev, "address", macBack])
        subprocess.call(["ip", "address", "add", ipBack, "dev", dev])
        subprocess.call(["ip", "link", "set", "up", "dev", dev])


# Main function
def Main():

    args = ParseArgs()

    if args.beautiful:
        verbose = False
        beauty = beautiful.Data()
        printer = beautiful.printer(beauty)
        printer.start()
    else:
        printBanner()
        verbose = args.verbose
        beauty = None

    # Create the output directory
    if not os.path.exists(args.output):

        # Verbose output
        out = colored("[i] Creating %s directory", 'yellow') % args.output
        if beauty:
            beauty.addComment(out)
        elif verbose:
            print(out)
        os.makedirs(args.output)

    portFile = open(args.ports, "r")        # already checked in ParseArgs()
    ipFile = open(args.ips, "r")

    queueList = createScanQueue(ipFile, portFile, verbose, beauty)

    # randomize
    if args.random:
        shuffle(queueList)

        # verbose output
        out = colored("[!] Scan queue randomized", "yellow")
        if args.beautiful:
            beauty.addComment(out)
        elif verbose:
            print(out)

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
                      args.additional, args.random, verbose,
                      args.simulate, beauty)

        # Cleaning
        spoofIPFile.close()
        spoofMacFile.close()

    # Case not threaded
    else:
        for couple in queueList:
            # Call Nmap
            CallNmap(couple[0], couple[1], args.type, args.output, args.format,
                     args.additional, verbose, args.simulate, beauty=beauty)

            time.sleep(int(args.delay))

    # Verbose output
    out = colored("[+] Scan finished", 'green')
    if args.beautiful:
        beauty.addComment(out)
        printer.stop()
    elif verbose:
        print(out)

    sys.exit(0)


Main()
