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


class Data:

    def __init__(self, IPs=[], ports=[]):
        self.IPs = []
        self.output = ""
        for ip in IPs:
            portlist = []
            for port in ports:
                portlist.append({
                    "port":     port,
                    "status":   0
                })
            self.IPs.append({
                "ip":       ip,
                "ports":    portlist
            })
        self.change = True

    def initLists(self, IPs, ports):
        for ip in IPs:
            portlist = []
            for port in ports:
                portlist.append({
                    "port":     port,
                    "status":   0
                })
            self.IPs.append({
                "ip":       ip,
                "ports":    portlist
            })
        self.change = True

    def doPort(self, ip, port, status):
        for ip_ in self.IPs:
            if ip_['ip'] == ip:
                for port_ in ip_['ports']:
                    if port_['port'] == port:
                        port_['status'] = status
                        self.change = True
                        return

    def addComment(self, comment):
        self.output += comment + os.linesep
        self.change = True


def trueLen(text):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return len(ansi_escape.sub('', text))


def printBanner(width):
    """Print the program banner in the standard output
    """
    prefix = "{:^" + width + "}"
    banner = ['  ██████  ██▓ ██▓    ▓█████  ███▄    █ ▄▄▄█████▓    ███▄ ▄███▓ '
              '▄▄▄       ██▓███  ',
              '▒██    ▒ ▓██▒▓██▒    ▓█   ▀  ██ ▀█   █ ▓  ██▒ ▓▒   ▓██▒▀█▀ ██▒▒'
              '████▄    ▓██░  ██▒',
              '░ ▓██▄   ▒██▒▒██░    ▒███   ▓██  ▀█ ██▒▒ ▓██░ ▒░   ▓██    ▓██░▒'
              '██  ▀█▄  ▓██░ ██▓▒',
              '  ▒   ██▒░██░▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒░ ▓██▓ ░    ▒██    ▒██ ░'
              '██▄▄▄▄██ ▒██▄█▓▒ ▒',
              '▒██████▒▒░██░░██████▒░▒████▒▒██░   ▓██░  ▒██▒ ░    ▒██▒   ░██▒ '
              '▓█   ▓██▒▒██▒ ░  ░',
              '▒ ▒▓▒ ▒ ░░▓  ░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒   ▒ ░░      ░ ▒░   ░  ░ '
              '▒▒   ▓▒█░▒▓▒░ ░  ░',
              '░ ░▒  ░ ░ ▒ ░░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░    ░       ░  ░      ░ '
              ' ▒   ▒▒ ░░▒ ░     ',
              '░  ░  ░   ▒ ░  ░ ░      ░      ░   ░ ░   ░         ░      ░    '
              ' ░   ▒   ░░       ',
              '      ░   ░      ░  ░   ░  ░         ░                    ░    '
              '     ░  ░         ']
    fullBanner = ""
    for line in banner:
        fullBanner += prefix.format(line) + os.linesep
    print(colored(fullBanner, 'green'))


def printIP(IP, width):
    height = 1
    line = IP["ip"] + ": "
    res = ""
    for port in IP["ports"]:
        addition = ' ' + port["port"]
        if port["status"] == 1:
            addition = ' ' + colored(port["port"], "white", "on_blue")
        elif port["status"] == 2:
            addition = ' ' + colored(port["port"], "white", "on_green")

        if trueLen(line) + trueLen(addition) > width:
            res += line
            line = os.linesep + "        " + addition
            height += 1
        else:
            line += addition
    res += line
    print(res)
    return height


def printOutput(output, height, width):
    res = []
    lines = output.split(os.linesep)
    lines = lines[:len(lines) - 1]
    for line in lines:
        while trueLen(line) > width:
            res.append(line[:width])
            line = line[width:]
        res.append(line)

    if len(res) > height:
        for line in res[len(res) - height:]:
            print(line)
        return height
    else:
        for line in res:
            print(line)
        return len(res)


def printScreen(data):
    rows, columns = os.popen('stty size', 'r').read().split()
    height = int(rows) - 1
    width = int(columns)

    # clear screen
    print("\033[F" * (height) + " " * ((height) * width)
          + "\033[F" * (height))

    printBanner(columns)
    height -= 11

    for ip in data.IPs:
        height -= printIP(ip, width)

    print()
    height -= 1

    height -= printOutput(data.output, height, width)

    while height > 0:
        print()
        height -= 1


class printer(threading.Thread):

    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data
        self.running = True

    def run(self):
        while self.running or self.data.change:
            if self.data.change:
                self.data.change = False
                printScreen(self.data)

    def stop(self):
        self.running = False
