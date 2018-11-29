# NMAP LAUNCHER

Launch multiple port scans on multiple IP ranges one after another

## Purpose

We needed to launch scans for open ports on multiple IP ranges without
multithreading. To do so we first scanned most common ports on every IP range
and then increased the ports list.

## Help

```
usage: nmap_launcher.py [-h] [-i FILENAME] [-p FILENAME] [-n NUMBER]
                        [-d DELAY] [-v] [-f STRING] [-o DIRECTORY]
                        {oX,oN,oG,oA,oS} ...

Launch multiple port scans on multiple IP ranges one after another

positional arguments:
  {oX,oN,oG,oA,oS}      Output type (See Nmap manpage)
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
```
