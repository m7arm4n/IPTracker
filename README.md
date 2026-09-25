# IPTracker

A high-performance, asynchronous DNS reverse lookup tool. IPTracker checks the validity of IP addresses by performing reverse DNS lookups, now rebuilt with `asyncio` to support thousands of concurrent requests with minimal resource consumption.

## Features

- **Asynchronous Engine:** Fast scanning capabilities using Python's `asyncio`.
- **CIDR Support:** Automatically expands and scans entire network ranges (e.g., `192.168.1.0/24`).
- **FCrDNS Validation:** Option to verify Forward-Confirmed reverse DNS to prevent spoofed/dangling records.
- **JSON Output:** Structured data output (`--json`) for easy integration with other security tools.
- **Rate Limiting:** Control the exact number of requests per second to avoid bans.
- **Retry Mechanism:** Built-in exponential backoff for failed lookups in noisy networks.
- **Pipeline Ready:** Seamlessly integrates with Unix pipelines (`stdin`/`stdout`) without broken pipe errors.

## Usage

    usage: iptracker.py [-h] [-l LIST] [-p IP] [-o OUTPUT] [-s] [-S] [-t THREADS] 
                        [-d] [-r RATE_LIMIT] [--retries RETRIES] [--fcrdns] [--json]

    optional arguments:
      -h, --help            show this help message and exit
      -l LIST, --list LIST  A file containing a list of IP addresses or CIDRs.
      -p IP, --ip IP        A single IP address or CIDR range.
      -o OUTPUT, --output OUTPUT
                            The file to save the valid IP addresses.
      -s, --silent          Run in silent mode (suppress stdout).
      -S, --stats           Display scan statistics (prints to stderr).
      -t THREADS, --threads THREADS
                            Concurrency limit. Default is 1000.
      -d, --description     Include hostname in standard output.
      -r RATE_LIMIT, --rate-limit RATE_LIMIT
                            Maximum requests per second.
      --retries RETRIES     Number of retries on network failure. Default is 1.
      --fcrdns              Enable Forward-Confirmed reverse DNS validation.
      --json                Output results in JSON format.

## Examples

**1. Basic Single IP/CIDR Scan**
Check a full subnet and display the hostnames:
```
    python iptracker.py -p 192.168.1.0/24 -d
```

**2. High-Speed File Scanning**
Scan a large list of IPs with 2000 concurrent connections, showing real-time stats:
```
    python iptracker.py -l ip_list.txt -t 2000 -S -o valid_ips.txt
```

**3. Advanced Security Scan (FCrDNS + JSON)**
Validate IPs using Forward-Confirmed reverse DNS and output the results as JSON:
```
    python iptracker.py -l ip_list.txt --fcrdns --json -o output.json
```

**4. Rate-Limited Piped Execution**
Read from standard input, limit to 50 requests per second, and save valid IPs quietly:
```
    cat ip_list.txt | python iptracker.py -r 50 > valid_ips.txt
```

## Requirements
- Python 3.7+
