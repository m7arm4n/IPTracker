import argparse
import asyncio
import ipaddress
import json
import socket
import sys
import time
import signal

if sys.platform != "win32":
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:
        pass

class AsyncRateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.allowance = float(rate_limit) if rate_limit else 0.0
        self.last_check = time.monotonic()

    async def wait(self):
        if not self.rate_limit or self.rate_limit <= 0:
            return
        current = time.monotonic()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += time_passed * self.rate_limit
        if self.allowance > self.rate_limit:
            self.allowance = self.rate_limit
        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) / self.rate_limit
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0

class ScannerCore:
    def __init__(self, concurrency, rate_limit, retries, fcrdns):
        self.sem = asyncio.Semaphore(concurrency)
        self.limiter = AsyncRateLimiter(rate_limit)
        self.retries = retries
        self.fcrdns = fcrdns
        self.loop = asyncio.get_running_loop()

    async def get_ptr(self, ip):
        for _ in range(self.retries + 1):
            try:
                hostname, _ = await self.loop.getnameinfo((ip, 0), socket.NI_NAMEREQD)
                return hostname
            except Exception:
                await asyncio.sleep(0.2)
        return None

    async def get_a(self, name):
        for _ in range(self.retries + 1):
            try:
                info = await self.loop.getaddrinfo(name, None, family=socket.AF_INET)
                return [item[4][0] for item in info]
            except Exception:
                await asyncio.sleep(0.2)
        return []

    async def scan_ip(self, ip):
        async with self.sem:
            await self.limiter.wait()
            ptr = await self.get_ptr(ip)
            if not ptr:
                return {"ip": ip, "valid": False}
            
            result = {"ip": ip, "valid": True, "hostname": ptr}
            
            if self.fcrdns:
                a_records = await self.get_a(ptr)
                result["fcrdns"] = ip in a_records
                
            return result

def parse_ips(inputs):
    ips = []
    for item in inputs:
        item = item.strip()
        if not item:
            continue
        try:
            net = ipaddress.ip_network(item, strict=False)
            for ip in net:
                ips.append(str(ip))
        except ValueError:
            pass
    return list(dict.fromkeys(ips))

async def run_scan(args, ip_list):
    scanner = ScannerCore(args.threads, args.rate_limit, args.retries, args.fcrdns)
    out_file = open(args.output, "a", encoding="utf-8") if args.output else None
    
    total_ips = len(ip_list)
    processed = 0
    valid = 0
    start_time = time.monotonic()
    
    tasks = [asyncio.create_task(scanner.scan_ip(ip)) for ip in ip_list]
    
    try:
        for future in asyncio.as_completed(tasks):
            res = await future
            processed += 1
            
            if res["valid"]:
                valid += 1
                
                if args.json:
                    line = json.dumps(res)
                else:
                    line = f"{res['ip']} is valid, hostname: {res['hostname']}" if args.description else res['ip']
                    if args.fcrdns:
                        line += f" [FCrDNS: {res.get('fcrdns', False)}]"
                        
                if out_file:
                    out_file.write(line + "\n")
                    out_file.flush()
                    
                if not args.silent:
                    if args.stats:
                        sys.stderr.write("\r\033[K")
                    try:
                        print(line)
                        sys.stdout.flush()
                    except BrokenPipeError:
                        devnull = open(sys.platform == "win32" and "NUL" or "/dev/null", "w")
                        sys.stdout = devnull
                        
            if args.stats:
                elapsed = time.monotonic() - start_time
                progress = (processed / total_ips) * 100
                stats_msg = f"\rProgress: {progress:.1f}% ({processed}/{total_ips}) | Valid: {valid} | Time: {elapsed:.1f}s"
                sys.stderr.write(stats_msg)
                sys.stderr.flush()
    except asyncio.CancelledError:
        pass
    finally:
        if args.stats:
            sys.stderr.write("\n")
        if out_file:
            out_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list")
    parser.add_argument("-p", "--ip")
    parser.add_argument("-o", "--output")
    parser.add_argument("-s", "--silent", action="store_true")
    parser.add_argument("-S", "--stats", action="store_true")
    parser.add_argument("-t", "--threads", type=int, default=1000)
    parser.add_argument("-d", "--description", action="store_true")
    parser.add_argument("-r", "--rate-limit", type=float, default=0.0)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--fcrdns", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    raw_inputs = []
    if args.list:
        with open(args.list, "r", encoding="utf-8") as f:
            raw_inputs.extend(f.readlines())
    elif args.ip:
        raw_inputs.append(args.ip)
    elif not sys.stdin.isatty():
        raw_inputs.extend(sys.stdin.readlines())
    else:
        parser.print_help()
        sys.exit(1)

    ip_list = parse_ips(raw_inputs)
    
    if not ip_list:
        sys.exit(1)

    try:
        asyncio.run(run_scan(args, ip_list))
    except KeyboardInterrupt:
        for task in asyncio.all_tasks():
            task.cancel()
        sys.exit(0)

if __name__ == "__main__":
    main()

