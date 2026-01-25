#!/usr/bin/env python3
"""
NullSec Port Scanner - Fast Async Port Scanner
High-performance port scanner with service detection
Part of the NullSec Tools Collection
"""

import sys
import socket
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Tuple

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║     _   __      ____   _____                                  ║
║    / | / /_  __/ / /  / ___/___  _____                        ║
║   /  |/ / / / / / /   \__ \/ _ \/ ___/                        ║
║  / /|  / /_/ / / /   ___/ /  __/ /__                          ║
║ /_/ |_/\__,_/_/_/   /____/\___/\___/                          ║
║                                                               ║
║                   Port Scanner v1.0                           ║
║             Fast Async Port Scanner                           ║
╚═══════════════════════════════════════════════════════════════╝
"""

# Common ports and their services
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 111: 'RPCBind', 135: 'MSRPC', 139: 'NetBIOS',
    143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 993: 'IMAPS', 995: 'POP3S',
    1433: 'MSSQL', 1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Proxy',
    8443: 'HTTPS-Alt', 27017: 'MongoDB', 6667: 'IRC', 9200: 'Elasticsearch'
}

class PortScanner:
    """Async port scanner with service detection"""
    
    def __init__(self, target: str, timeout: float = 1.0, concurrency: int = 500):
        self.target = target
        self.timeout = timeout
        self.concurrency = concurrency
        self.open_ports: List[Dict] = []
        
    async def scan_port(self, port: int) -> Tuple[int, bool, str]:
        """Scan a single port"""
        try:
            conn = asyncio.open_connection(self.target, port)
            reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)
            
            # Try to grab banner
            banner = ""
            try:
                writer.write(b"HEAD / HTTP/1.0\r\n\r\n")
                await writer.drain()
                data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
                banner = data.decode('utf-8', errors='ignore').strip()[:100]
            except:
                pass
            
            writer.close()
            await writer.wait_closed()
            
            return (port, True, banner)
        except:
            return (port, False, "")
    
    async def scan_ports(self, ports: List[int], callback=None) -> List[Dict]:
        """Scan multiple ports concurrently"""
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async def bounded_scan(port: int):
            async with semaphore:
                return await self.scan_port(port)
        
        tasks = [bounded_scan(port) for port in ports]
        results = await asyncio.gather(*tasks)
        
        for port, is_open, banner in results:
            if is_open:
                service = COMMON_PORTS.get(port, 'Unknown')
                result = {
                    'port': port,
                    'state': 'open',
                    'service': service,
                    'banner': banner
                }
                self.open_ports.append(result)
                if callback:
                    callback(result)
        
        return self.open_ports
    
    def get_port_range(self, port_spec: str) -> List[int]:
        """Parse port specification"""
        ports = []
        
        if port_spec == 'common':
            return list(COMMON_PORTS.keys())
        elif port_spec == 'all':
            return list(range(1, 65536))
        elif port_spec == 'top100':
            return [21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
                   143, 443, 445, 993, 995, 1433, 1521, 3306, 3389,
                   5432, 5900, 6379, 8080, 8443, 27017]
        
        for part in port_spec.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        
        return sorted(set(ports))


def print_result(result: Dict):
    """Print scan result as it comes in"""
    banner_info = f" | {result['banner'][:50]}" if result['banner'] else ""
    print(f"  [OPEN] {result['port']:>5}/tcp  {result['service']:<15}{banner_info}")


async def main_async(args):
    """Main async function"""
    scanner = PortScanner(
        target=args.target,
        timeout=args.timeout,
        concurrency=args.concurrency
    )
    
    ports = scanner.get_port_range(args.ports)
    
    print(f"\n[+] Target: {args.target}")
    print(f"[+] Ports: {len(ports)} ports to scan")
    print(f"[+] Timeout: {args.timeout}s")
    print(f"[+] Concurrency: {args.concurrency}")
    print(f"[+] Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("\nDiscovered Ports:")
    
    start_time = datetime.now()
    results = await scanner.scan_ports(ports, callback=print_result)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print(f"[+] Scan Complete!")
    print(f"[+] {len(results)} open ports found")
    print(f"[+] Scanned {len(ports)} ports in {elapsed:.2f} seconds")
    print(f"[+] Rate: {len(ports)/elapsed:.0f} ports/second")
    
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump({
                'target': args.target,
                'scan_time': datetime.now().isoformat(),
                'ports_scanned': len(ports),
                'open_ports': results
            }, f, indent=2)
        print(f"[+] Results saved to: {args.output}")


def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description='NullSec Port Scanner - Fast Async Port Scanner'
    )
    parser.add_argument('target', help='Target IP or hostname')
    parser.add_argument('-p', '--ports', default='common',
                       help='Port specification: common, top100, all, 1-1000, 80,443,8080')
    parser.add_argument('-t', '--timeout', type=float, default=1.0,
                       help='Connection timeout (default: 1.0s)')
    parser.add_argument('-c', '--concurrency', type=int, default=500,
                       help='Max concurrent connections (default: 500)')
    parser.add_argument('-o', '--output', help='Output file (JSON)')
    
    args = parser.parse_args()
    
    # Resolve hostname
    try:
        socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"[-] Error: Cannot resolve hostname '{args.target}'")
        sys.exit(1)
    
    asyncio.run(main_async(args))


if __name__ == '__main__':
    main()
