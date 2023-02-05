# IPTracker
A program that checks the validity of DNS of an IP address using socket functions and returns the result. It supports both single IP and file of IPs as input, with options to save the valid IPs to an output file, switch for silent mode, display stats during the scan, and adjust concurrent threads and rate limit for dns requests.

IPTracker is a program that allows you to check the DNS of the IP and return whether it is valid or not. It provides the following features:

1. Accepts both a file of IPs and a single IP. To provide a list of IPs, use the `-l` switch, and for a single IP, use the `-p` switch.
2. Option to save valid IP addresses to an output file. Use the `-o` switch to specify the output file name.
3. A `-silent` switch for silent mode.
4. `-stats` switch to display the stats of the running scan, showing stats during the program's execution and not writing a new line for each show stats, but instead replacing it in one line.
5. If an IP is valid, it is immediately written to the output file if the `-o` switch is used, or it is printed. Valid IPs are not saved to a result list within the program.
6. `-t` switch for the number of concurrent threads to use (default 100).

## Usage

```
usage: iptracker.py [-h] [-l IP_LIST] [-p IP] [-o OUTPUT_FILE] [-silent] [-stats]
                    [-t THREADS]

optional arguments:
  -h, --help            show this help message and exit
  -l IP_LIST, --list IP_LIST
                        A file containing a list of IP addresses to validate.
  -p IP, --ip IP        A single IP address to validate.
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        The file to save the valid IP addresses.
  -silent, --silent     Run in silent mode, no output will be displayed.
  -stats, --stats       Display scan statistics.
  -t THREADS, --threads THREADS
                        The number of concurrent threads to use. Default is 100.
```

To use IPTracker, the following command is used:

```
python IPTracker.py [-h] [-p IP] [-l IP_FILE] [-o OUTPUT_FILE] [-silent] [-stats] [-t THREADS]
```



## Example

```
python iptracker.py -l ip_list.txt -o valid_ips.txt -silent -stats -t 50
```

To check the DNS of a single IP address, run the following command:

```
python IPTracker.py -p 192.168.0.1
```


To check the DNS of a list of IP addresses, run the following command:

```
python IPTracker.py -l ip_list.txt
```

To save the valid IP addresses to an output file, run the following command:

```
python IPTracker.py -l ip_list.txt -o valid_ips.txt
```


To run the program in silent mode and display stats of the running scan, run the following command:

```
python IPTracker.py -l ip_list.txt -t 200
```

## Requirements
- Python 3.x




