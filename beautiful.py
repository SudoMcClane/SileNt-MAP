#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silent Map extension for beautiful output.

Author: Clément Gatefait
Date: 06/11/2019
"""

from termcolor import colored
import os
import re
import threading
import time


class Data:
    '''Data object for printing
    '''

    def __init__(self, IPs=[], ports=[]):
        '''Initialize the Data object

        Parameters
        ----------
        IPs     : [string]
            IP ranges
        ports   : [string]
            Port ranges

        Returns
        -------
        beautiful.Data
            The initialized Data object
        '''
        self.IPs = []       # initialize the IPs structure
        self.output = ""    # initialize the verbose output
        self.initLists(IPs, ports)

    def initLists(self, IPs, ports):
        '''Create the IPs structure.

        Parameters
        ----------
        IPs     : [string]
            IP ranges
        ports   : [string]
            Port ranges
        '''
        # IPs structure examle:
        #   [
        #       {
        #           "ip"    : "127.0.0.1",
        #           "ports" :
        #               [
        #                   {
        #                       "port"  : 80,
        #                       "status": 0
        #                   }
        #               ]
        #       }
        #   ]
        for ip in IPs:  # foreach IP
            portlist = []   # initialize the "ports" sub list
            for port in ports:  # foreach port
                portlist.append({
                    "port":     port,
                    "status":   0
                })
            self.IPs.append({
                "ip":       ip,
                "ports":    portlist
            })

    def doPort(self, ip, port, status):
        '''Change the status of a port

        Parameters
        ----------
        ip      : string
            The concerned IP address/range
        port    : sting
            The concerned port number/range
        status  : integer
            The new port status (0: TODO, 1: IN PROGRESS, 2: DONE)
        '''
        for ip_ in self.IPs:    # foreach IP
            if ip_['ip'] == ip:     # if the IP matches
                for port_ in ip_['ports']:  # foreach port
                    if port_['port'] == port:   # if the port matches
                        port_['status'] = status    # change the port status
                        return                      # job is done: exit loops

    def addComment(self, comment):
        '''Add a comment for the verbose output

        Parameters
        ----------
        comment : string
            The comment to be added
        '''
        self.output += comment + os.linesep     # Append the new comment


def trueLen(text):
    '''Returns a text length without ANSI escape sequences

    Parameters
    ----------
    text    : string
        The text on which length must be calculated

    Returns
    -------
    integer
        The length of the text
    '''
    # regex for ANSI escape sequences
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    # return length of text with ANSI escape sequences removed
    return len(ansi_escape.sub('', text))


def printBanner(width):
    """Print the program banner in the standard output

    Parameters
    ----------
    width   : string
        The width of the terminal printable space (as string)

    Returns
    -------
    integer
        The number of lines printed
    """
    prefix = "{:^" + width + "}"    # Prefix for centered text
    # large banner
    if int(width) > 90:
        banner = ['  ██████  ██▓ ██▓    ▓█████  ███▄    █ ▄▄▄█████▓   '
                  ' ███▄ ▄███▓ ▄▄▄       ██▓███  ',
                  '▒██    ▒ ▓██▒▓██▒    ▓█   ▀  ██ ▀█   █ ▓  ██▒ ▓▒   '
                  '▓██▒▀█▀ ██▒▒████▄    ▓██░  ██▒',
                  '░ ▓██▄   ▒██▒▒██░    ▒███   ▓██  ▀█ ██▒▒ ▓██░ ▒░   '
                  '▓██    ▓██░▒██  ▀█▄  ▓██░ ██▓▒',
                  '  ▒   ██▒░██░▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒░ ▓██▓ ░    '
                  '▒██    ▒██ ░██▄▄▄▄██ ▒██▄█▓▒ ▒',
                  '▒██████▒▒░██░░██████▒░▒████▒▒██░   ▓██░  ▒██▒ ░    '
                  '▒██▒   ░██▒ ▓█   ▓██▒▒██▒ ░  ░',
                  '▒ ▒▓▒ ▒ ░░▓  ░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒   ▒ ░░      '
                  '░ ▒░   ░  ░ ▒▒   ▓▒█░▒▓▒░ ░  ░',
                  '░ ░▒  ░ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░    ░       '
                  '░  ░      ░  ▒   ▒▒ ░░▒ ░     ',
                  '░  ░  ░   ▒ ░  ░ ░      ░      ░   ░ ░   ░         '
                  '░      ░     ░   ▒   ░░       ',
                  '      ░   ░      ░  ░   ░  ░         ░             '
                  '       ░         ░  ░         ']
    # medium banner
    elif int(width) > 50:
        banner = [' _____ _ _     _____ _      _____ _____ _____ ',
                  '|   __|_| |___|   | | |_   |     |  _  |  _  |',
                  '|__   | | | -_| | | |  _|  | | | |     |   __|',
                  '|_____|_|_|___|_|___|_|    |_|_|_|__|__|__|   ']
    # small banner
    else:
        banner = ['SileNt MAP']
    fullBanner = ""     # initialize banner to print
    for line in banner:     # foreach line of the banner
        fullBanner += prefix.format(line) + os.linesep  # centered line + \n
    print(colored(fullBanner, 'green'))     # print the green banner
    return len(banner) + 2  # return the number of lines printed


def cropLine(line, width, columnIndent=0):
    '''Crop an IP line to fit the terminal

    Parameters
    ----------
    line            : string
        The line to crop
    width           : integer
        Width of the terminal
    columnIndent    : integer
        Horizontal indentation for scrolling (default=0)

    Returns
    -------
    string
        The line croped
    '''
    elements = line.split(" ")      # split line at spaces
    # First element should be the IP range, so just ignore it
    res = elements.pop(0) + " "     # initialize the result line
    resLen = trueLen(res)           # store the length of the final string
    lineLen = trueLen(line)         # calculate the length of the original line

    # crop head
    while lineLen > width:  # equivalent to: if lineLen > width: while True:
        port = elements.pop(0)  # process first port
        portLen = trueLen(port) + 1     # calculate length of the port + " "
        if portLen > columnIndent:      # if port is the first one displayed
            # example: port = "!033[91m!033[92mT:80!033[00m"
            decomp = port.split("m")    # split the port by ANSI esc seqs ends
            # example: decomp = ["!033[91", "!033[92", "T:80!033[00", ""]
            decomp[2] = decomp[2][columnIndent:]    # remove first caracters
            # example: decomp[2] = "T:80!033[00"[2:] -> "80!033[00"
            port = 'm'.join(decomp)     # rebuild the string
            # example: port = "!033[91m!033[92m80!033[00m"
            elements.insert(0, port)    # insert the port back in the list
            break   # head croped
        else:   # port is on the left of the indentation
            columnIndent -= portLen     # ignore port and process the next one

    # crop tail
    while lineLen > width:  # equivalent to: if lineLen > width: while True:
        port = elements.pop(0)  # process first port
        portLen = trueLen(port) + 1     # calculate length of the port + " "
        if resLen + portLen > width:    # if port is the last one displayed
            # example: port = "!033[91m!033[92mT:80!033[00m"
            decomp = port.split("m")    # split the port by ANSI esc seqs ends
            # example: decomp = ["!033[91", "!033[92", "T:80!033[00", ""]
            # remove last caracters
            decomp[2] = decomp[2][:width - resLen] + decomp[2][portLen - 2:]
            # example: decomp[2] = "T:80!033[00"[:80-78] + "T:80!033[00"[:5-2]
            #          decomp[2] = "T:!033[00"
            port = 'm'.join(decomp)
            # example: port = "!033[91m!033[92mT:!033[00m"
            res += port     # append the port to the line
            return res      # tail croped, return the result
        else:   # the port is fully displayed
            res += port + " "   # append port to the result
            resLen += portLen   # update the result length

    # if the line can be fully printed
    return line


def printIP(IP, width, columnIndent=0):
    '''Print an IP line

    Parameters
    ----------
    IP              : dictionary
        The IP to print (ex:{"ip":"10.0.0.1","ports":[{"port":80,"status":0}]})
    width           : integer
        Width of the terminal
    columnIndent    : integer
        Horizontal indentation for scrolling (default=0)

    Returns
    -------
    integer
        The number of lines printed
    '''
    line = IP["ip"] + ":"   # initialize the line with the IP address/range
    for port in IP["ports"]:    # foreach port
        if port["status"] == 1:     # if port status is IN PROGRESS
            line += ' ' + colored(port["port"], "white", "on_blue")
        elif port["status"] == 2:   # if port status is DONE
            line += ' ' + colored(port["port"], "white", "on_green")
        else:                       # if port status is TODO
            line += ' ' + colored(port["port"], "white", "on_grey")

        if trueLen(line) > width + columnIndent:    # if line is long enough
            break   # stop appending useless ports not displayed

    if trueLen(line) > width:   # if scrolling implies looping to first ports
        for port in IP["ports"]:    # foreach port
            if port["status"] == 1:     # if port status is IN PROGRESS
                line += ' ' + colored(port["port"], "white", "on_blue")
            elif port["status"] == 2:   # if port status is DONE
                line += ' ' + colored(port["port"], "white", "on_green")
            else:                       # if port status is TODO
                line += ' ' + colored(port["port"], "white", "on_grey")

            if trueLen(line) > width + columnIndent:  # if line is long enough
                break   # stop appending useless ports not displayed

    print(cropLine(line, width, columnIndent))  # crop the line if scrolling
    return 1    # return the number of line printed


def printOutput(output, height, width):
    '''Print the comments of the verbose output

    Parameters
    ----------
    output  : string
        Verbose output to print
    height  : integer
        Terminal height
    width   : integer
        Terminal width

    Returns
    -------
    integer
        Number of lines printed
    '''
    res = []    # initialize the result
    lines = output.split(os.linesep)    # split lines
    lines = lines[:len(lines) - 1]      # remove last item: a useless ""
    for line in lines:  # foreach line
        while trueLen(line) > width:    # while line is larger than terminal
            res.append(line[:width])    # append first part to the result
            line = line[width:]         # cut the processed part of the line
        res.append(line)    # append the line to the result

    if len(res) > height:   # if too much comments to display everything
        for line in res[len(res) - height:]:    # for the last lines
            print(line)
        return height   # return the number of lines printed
    else:                   # if enough space to display every comment
        for line in res:    # foreach line
            print(line)
        return len(res)     # return the number of lines printed


def printScreen(data, lineIndent=0, columnIndent=0):
    '''Print a beautifull screen

    Parameters
    ----------
    data            : beautiful.Data
        The Data object to print
    lineIndent      : integer
        Vertical indentation for scrolling (default=0)
    columnIndent    : integer
        Horizontal indentation for scrolling (default=0)
    '''
    # Calculate terminal size
    rows, columns = os.popen('stty size', 'r').read().split()
    height = int(rows) - 1      # last line and column
    width = int(columns) - 1    # cannot be used

    # clear screen
    print("\033[F" * (height) + " " * ((height) * width)
          + "\033[F" * (height))

    # Print the banner
    height -= printBanner(columns)

    # Print IP / Ports section
    if height < len(data.IPs) + 5:  # if too much IPs to print on screen
        # beginning = current cursor
        beg = lineIndent
        # end = (current cursor + available display lines) % number of IPs
        # example: (   8        +        10 - 5          ) %      10
        #   -> end = 3
        #   -> IPs printed: IPs[8], IPs[9], IPs[0], IPs[1], IPs[2], IPs[3]
        end = (lineIndent + height - 5) % len(data.IPs)
    else:                           # else print every IP line
        beg = 0
        end = len(data.IPs) - 1

    while beg != end:   # while not all IP to print printed
        height -= printIP(data.IPs[beg], width, columnIndent)   # print a line
        beg = (beg + 1) % len(data.IPs)  # next IP (loop to 1st after end)
    height -= printIP(data.IPs[beg], width, columnIndent)   # print last line

    print()     # add an empty line
    height -= 1

    height -= printOutput(data.output, height, width)   # print verbose output

    # complete the screen with empty lines
    while height > 0:
        print()
        height -= 1


class Printer(threading.Thread):
    '''Printer's thread
    It has to be in a separate thread so that probes' threads do not try to
    print the screen at the same time and produce an unreadable output
    '''

    def __init__(self, data):
        '''Initialize the Printer's thread

        Parameters
        ----------
        data : beautuful.Data
            The Data structure to print

        Returns
        -------
        beautiful.Printer
            The Printer object created
        '''
        threading.Thread.__init__(self)     # initialize the inherited class
        self.data = data                    # Data object to print
        self.running = True                 # Flag to raise ro end the thread

    def run(self):
        '''Start the printer's thread
        '''
        lineIndent = 0      # current indentation for vertical scrolling
        columnIndent = 0    # ----------------------- horizontal scrolling
        portListWidth = 1   # width of a line with port ranges (without IPs)

        while self.running:     # while the flag has not been raised
            if portListWidth == 1 and len(self.data.IPs):  # data initialized
                # calculate port ranges width
                for portObj in self.data.IPs[0]["ports"]:
                    portListWidth += len(portObj["port"]) + 1

            printScreen(self.data, lineIndent, columnIndent)    # print Screen
            time.sleep(.1)  # sleep a little: 10fps is enough
            lineIndent = (lineIndent + 1) % len(self.data.IPs)  # scroll vert.
            columnIndent = (columnIndent + 1) % portListWidth   # scroll horiz.

    def stop(self):
        '''Raise the stopping flag to stop the printer
        '''
        # Sleep a little bit to allow last data to be printed.
        time.sleep(.2)
        self.running = False
