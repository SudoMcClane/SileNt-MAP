# NMAP LAUNCHER

Launch multiple port scans on multiple IP ranges one after another
Script also allows to launch scans in threads from multiple IP and
MAC source addresses for smaller network footprint.

## Purpose

We needed to launch scans for open ports on multiple IP ranges without
multithreading. To do so we first scanned most common ports on every IP range
and then increased the ports list.

Now the project has evolved to add multiple source addresses for scans to
prevent network detection when performing Red Teaming for example.

## Prerequisites

* [python3](https://www.python.org/downloads/)
* [termcolor](https://pypi.org/project/termcolor/)
* [netifaces](https://pypi.org/project/netifaces/)

## Help

```
usage: nmap_launcher.py [-h] [-i FILENAME] [-p FILENAME] [-n NUMBER]
                        [-d DELAY] [-v] [-f STRING] [-o DIRECTORY] [--random]
                        [--simulate] [-e DEVICE] [--spoof-ip FILENAME]
                        [--spoof-mac FILENAME]
                        {oX,oN,oA,oS,oG} ...

Launch multiple port scans on multiple IP ranges one after another

positional arguments:
  {oX,oN,oA,oS,oG}      Output type (See Nmap manpage)
  additional            Additional arguments for nmap

optional arguments:
  -h, --help            show this help message and exit
  -i FILENAME, --ips FILENAME
                        File with IPs/IP ranges to scan (one per line)
  -p FILENAME, --ports FILENAME
                        File with port list to scan (one per line: '80',
                        'T:443' or '8000-8010')
  -n NUMBER, --number NUMBER
                        Number of Ports/Port ranges to scan at the same time
  -d DELAY, --delay DELAY
                        Pause between two scans (in seconds)
  -v, --verbose         Show additional messages
  -f STRING, --format STRING
                        Output filenames format (STRING °/. (ip, port))
  -o DIRECTORY, --output DIRECTORY
                        Directory name for scan results
  --random              Perform scans in a random order
  --simulate            Do not actually scan
  -e DEVICE, --dev DEVICE
                        Network interface to use
  --spoof-ip FILENAME   File containing IP addresses used as source for Nmap
                        (one per line). Retrieved using DHCP if empty
  --spoof-mac FILENAME  File containing MAC addresses used as source for Nmap
                        (one per line)
```

# Examples

## Basic usage

Launch nmap scans with -T4 and -sS options and XML output in the default folder

`sudo ./nmap_launcher.py -v -i ipranges.txt -p portranges.txt oX -sS -t4`

Simulate nmap scans in a random order with -Pn option and all output types in the default folder. Useful to test what commands will be launched.

`sudo ./nmap_launcher.py -v -i ipranges.txt -p portranges.txt -d 1 --random --simulate oA -Pn`

## Multithreaded scans

Simulate nmap scans in a random order with -vv option, a 5 seconds delay between scans on a single thread and all output types in the default folder. Useful to test what commands will be launched.

`sudo ./nmap_launcher.py -v -i ipranges.txt -p portranges.txt --spoof-ip iplist.txt --spoof-mac maclist.txt -e lo -d 5 --random --simulate oA -vv`

Launch nmap scans using DHCP to associate IPs to specified MACs with -vvv option and XML output in the default folder.

`sudo ./nmap_launcher.py -v -i ipranges.txt -p portranges.txt --spoof-ip non_existing_file.txt --spoof-mac maclist.txt -e eth0 oX -vvv`

## Files

### ipranges.txt

```
10.0.0.42
10.0.0.100/30
10.0.42.42
```

### portranges.txt

```
80
T:443
8080-8090
```

### iplist.txt

```
10.0.0.50
10.0.0.51
10.0.0.52
```

### maclist.txt

```
00:20:91:42:42:A1
00:20:91:42:42:A2
00:20:91:42:42:A3
```

## Known issues

### -Pn and multithreaded scan

From Nmap manual:
```
For machines on a local ethernet network, ARP scanning will still be performed (unless --disable-arp-ping or --send-ip is specified) because Nmap needs MAC addresses to further scan target hosts.
```

Using Nmap with `--spoof-mac` option implies creating OSI level 2 frame. Thus Nmap has to know the destination MAC address. To do so Nmap uses ARP ping. If the `--disable-arp-ping` option is specified, will not be able to determine the destination MAC and will fail. A quick and dirty fix implemented is to not spoof the source MAC when `-Pn` is specified.
