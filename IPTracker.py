import socket
import argparse
import time
import concurrent.futures

def check_dns(ip):
    try:
        hostname, aliaslist, addresslist = socket.gethostbyaddr(ip)
        return True, hostname
    except socket.herror:
        return False, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", help="IP list file")
    parser.add_argument("-p", "--ip", help="Single IP address")
    parser.add_argument("-o", "--output", help="Output file to save valid IPs")
    parser.add_argument("-silent", "--silent", help="Silent mode", action="store_true")
    parser.add_argument("-stats", "--stats", help="Display stats during the running scan", action="store_true")
    parser.add_argument("-t", "--threads", help="Number of concurrent threads to use (default 100)", type=int, default=100)
    args = parser.parse_args()
    
    ip_list = []
    if args.list:
        with open(args.list, "r") as f:
            ip_list = [line.strip() for line in f]
    elif args.ip:
        ip_list = [args.ip]
    else:
        print("Please provide either a list of IPs or a single IP using the -l or -p switch")
        exit(1)
        
    start_time = time.time()
    valid_ips = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_ip = {executor.submit(check_dns, ip): ip for ip in ip_list}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            is_valid, hostname = future.result()
            if is_valid:
                valid_ips += 1
                if args.output:
                    with open(args.output, "a") as f:
                        f.write(f"{ip}\n")
                if not args.silent:
                    print(f"\n{ip} is valid, hostname: {hostname}")
            if args.stats:
                elapsed_time = time.time() - start_time
                progress = (ip_list.index(ip) + 1) / len(ip_list) * 100
                stats = f"\rProgress: {progress:.2f}%, Elapsed time: {elapsed_time:.2f} seconds, Valid IPs found: {valid_ips}"
                print(stats, end="")
    print("\nScan completed.")
