
"""
Port Scanner - TCP Connect Scan

A multi-threaded port scanner that identifies open ports and running
services on a target host. Uses the full TCP three-way handshake
(socket.connect), so it works without root privileges.
"""


import socket
import sys
import argparse
import threading
import queue
import time
from datetime import datetime

# Fallback service names for common ports (used if the OS service DB
# doesn't know the port, e.g. on minimal containers)
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 111: "RPCbind", 123: "NTP", 135: "MSRPC", 137: "NetBIOS-NS",
    139: "NetBIOS-SSN", 143: "IMAP", 161: "SNMP", 389: "LDAP", 443: "HTTPS",
    445: "SMB", 465: "SMTPS", 587: "SMTP-Submission", 993: "IMAPS",
    995: "POP3S", 1433: "MSSQL", 1521: "Oracle-DB", 2049: "NFS",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8000: "HTTP-Alt", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
    9200: "Elasticsearch", 27017: "MongoDB",
}


class PortScanner:
    def __init__(self, target, ports, threads=100, timeout=1.0, grab_banner=True, verbose=True):
        self.target = target
        self.ports = ports
        self.threads = threads
        self.timeout = timeout
        self.grab_banner = grab_banner
        self.verbose = verbose
        self.open_ports = []   # list of (port, service, banner)
        self.lock = threading.Lock()
        self.q = queue.Queue()

    def resolve_target(self):
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror:
            print(f"[!] Could not resolve hostname: {self.target}")
            sys.exit(1)

    @staticmethod
    def get_service_name(port):
        try:
            return socket.getservbyport(port, "tcp")
        except OSError:
            return COMMON_PORTS.get(port, "unknown")

    def grab_service_banner(self, sock, port):
        """Try to read a banner; for HTTP(S)-like ports, send a probe first."""
        try:
            sock.settimeout(1.0)
            if port in (80, 8000, 8080, 8888):
                sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            data = sock.recv(1024)
            return data.decode(errors="ignore").strip().split("\n")[0]
        except Exception:
            return ""

    def scan_port(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            result = sock.connect_ex((ip, port))
            if result == 0:
                service = self.get_service_name(port)
                banner = self.grab_service_banner(sock, port) if self.grab_banner else ""
                with self.lock:
                    self.open_ports.append((port, service, banner))
                    if self.verbose:
                        banner_display = f"  {banner[:60]}" if banner else ""
                        print(f"[+] {port:5d}/tcp  open   {service:16s}{banner_display}")
        except Exception:
            pass
        finally:
            sock.close()

    def _worker(self, ip):
        while True:
            try:
                port = self.q.get_nowait()
            except queue.Empty:
                return
            self.scan_port(ip, port)
            self.q.task_done()

    def run(self):
        ip = self.resolve_target()
        if self.verbose:
            print("=" * 64)
            print(f"Target        : {self.target} ({ip})")
            print(f"Ports to scan : {len(self.ports)}")
            print(f"Threads       : {self.threads}   Timeout: {self.timeout}s")
            print(f"Started       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 64)

        start = time.time()
        for port in self.ports:
            self.q.put(port)

        workers = [threading.Thread(target=self._worker, args=(ip,), daemon=True)
                   for _ in range(min(self.threads, len(self.ports)))]
        for t in workers:
            t.start()
        for t in workers:
            t.join()

        elapsed = time.time() - start
        if self.verbose:
            print("=" * 64)
            print(f"Scan finished in {elapsed:.2f}s  |  {len(self.open_ports)} open port(s) found")
            print("=" * 64)
            if self.open_ports:
                print(f"\n{'PORT':<10}{'SERVICE':<18}BANNER")
                for port, service, banner in sorted(self.open_ports):
                    print(f"{port}/tcp{'':<5}{service:<18}{banner[:50]}")

        return sorted(self.open_ports)


def parse_ports(port_string):
    """Parse a port spec like '80,443,8000-8100' into a sorted list of ints."""
    ports = set()
    for part in port_string.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-")
            start, end = int(start), int(end)
            if not (0 < start <= 65535 and 0 < end <= 65535 and start <= end):
                raise ValueError(f"Invalid port range: {part}")
            ports.update(range(start, end + 1))
        else:
            p = int(part)
            if not (0 < p <= 65535):
                raise ValueError(f"Invalid port: {p}")
            ports.add(p)
    return sorted(ports)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-threaded TCP port scanner with service/banner detection.",
        epilog="Example: python3 port_scanner.py scanme.nmap.org -p 1-1000",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Target IP address or hostname")
    parser.add_argument("-p", "--ports", default="1-1024",
                         help="Ports to scan, e.g. '1-1000' or '22,80,443' (default: 1-1024)")
    parser.add_argument("-t", "--threads", type=int, default=100,
                         help="Number of concurrent threads (default: 100)")
    parser.add_argument("-T", "--timeout", type=float, default=1.0,
                         help="Per-connection timeout in seconds (default: 1.0)")
    parser.add_argument("--no-banner", action="store_true",
                         help="Disable banner grabbing (faster)")
    parser.add_argument("-o", "--output", help="Save results to a file (plain text)")

    args = parser.parse_args()

    try:
        ports = parse_ports(args.ports)
    except ValueError as e:
        print(f"[!] {e}")
        sys.exit(1)

    scanner = PortScanner(
        target=args.target,
        ports=ports,
        threads=args.threads,
        timeout=args.timeout,
        grab_banner=not args.no_banner,
    )
    results = scanner.run()

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"Port scan results for {args.target}\n")
            f.write(f"Scanned at: {datetime.now()}\n\n")
            for port, service, banner in results:
                f.write(f"{port}/tcp\t{service}\t{banner}\n")
        print(f"\n[+] Results saved to {args.output}")


if __name__ == "__main__":
    main()