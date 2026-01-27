#!/usr/bin/env python3
"""
NullSec Network Sniffer - Packet Capture & Analysis Tool
Capture and analyze network traffic with filtering support
Part of the NullSec Tools Collection
"""

import sys
import socket
import struct
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║     _   __      ____   _____                                  ║
║    / | / /_  __/ / /  / ___/___  _____                        ║
║   /  |/ / / / / / /   \__ \/ _ \/ ___/                        ║
║  / /|  / /_/ / / /   ___/ /  __/ /__                          ║
║ /_/ |_/\__,_/_/_/   /____/\___/\___/                          ║
║                                                               ║
║                  Network Sniffer v1.0                         ║
║           Packet Capture & Analysis Tool                      ║
╚═══════════════════════════════════════════════════════════════╝
"""

# Protocol numbers
PROTOCOLS = {
    1: 'ICMP',
    6: 'TCP',
    17: 'UDP',
    41: 'IPv6',
    47: 'GRE',
    50: 'ESP',
    51: 'AH',
    89: 'OSPF',
    132: 'SCTP'
}

# Common ports
COMMON_PORTS = {
    20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'TELNET', 25: 'SMTP',
    53: 'DNS', 67: 'DHCP', 68: 'DHCP', 69: 'TFTP', 80: 'HTTP',
    110: 'POP3', 119: 'NNTP', 123: 'NTP', 135: 'RPC', 137: 'NETBIOS',
    138: 'NETBIOS', 139: 'NETBIOS', 143: 'IMAP', 161: 'SNMP',
    162: 'SNMP-TRAP', 389: 'LDAP', 443: 'HTTPS', 445: 'SMB',
    465: 'SMTPS', 514: 'SYSLOG', 587: 'SMTP', 636: 'LDAPS',
    993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 1521: 'ORACLE',
    3306: 'MYSQL', 3389: 'RDP', 5432: 'POSTGRES', 5900: 'VNC',
    6379: 'REDIS', 8080: 'HTTP-PROXY', 8443: 'HTTPS-ALT',
    27017: 'MONGODB'
}


class PacketSniffer:
    """Network packet capture and analysis"""
    
    def __init__(self, interface: str = None, filter_proto: str = None,
                 filter_port: int = None, filter_host: str = None):
        self.interface = interface
        self.filter_proto = filter_proto
        self.filter_port = filter_port
        self.filter_host = filter_host
        self.packet_count = 0
        self.stats = defaultdict(int)
        self.connections = {}
        
    def create_socket(self) -> socket.socket:
        """Create raw socket for packet capture"""
        try:
            # Linux raw socket
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            if self.interface:
                sock.bind((self.interface, 0))
            return sock
        except PermissionError:
            print("[-] Root privileges required for packet capture")
            sys.exit(1)
        except AttributeError:
            print("[-] Raw socket not supported on this platform")
            sys.exit(1)
    
    def parse_ethernet(self, data: bytes) -> Tuple[str, str, int, bytes]:
        """Parse Ethernet frame"""
        dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])
        return (
            self.format_mac(dest_mac),
            self.format_mac(src_mac),
            socket.htons(proto),
            data[14:]
        )
    
    def parse_ipv4(self, data: bytes) -> Dict:
        """Parse IPv4 packet"""
        version_header_len = data[0]
        version = version_header_len >> 4
        header_len = (version_header_len & 0xF) * 4
        
        ttl, proto, checksum, src, dest = struct.unpack('! 8x B B H 4s 4s', data[:20])
        
        return {
            'version': version,
            'header_len': header_len,
            'ttl': ttl,
            'protocol': proto,
            'protocol_name': PROTOCOLS.get(proto, f'Unknown({proto})'),
            'checksum': checksum,
            'src': self.format_ipv4(src),
            'dest': self.format_ipv4(dest),
            'payload': data[header_len:]
        }
    
    def parse_tcp(self, data: bytes) -> Dict:
        """Parse TCP segment"""
        src_port, dest_port, seq, ack, offset_flags = struct.unpack('! H H L L H', data[:14])
        
        offset = (offset_flags >> 12) * 4
        flags = {
            'URG': bool(offset_flags & 0x20),
            'ACK': bool(offset_flags & 0x10),
            'PSH': bool(offset_flags & 0x08),
            'RST': bool(offset_flags & 0x04),
            'SYN': bool(offset_flags & 0x02),
            'FIN': bool(offset_flags & 0x01)
        }
        
        flag_str = ''.join([f[0] for f, v in flags.items() if v])
        
        return {
            'src_port': src_port,
            'dest_port': dest_port,
            'src_service': COMMON_PORTS.get(src_port, ''),
            'dest_service': COMMON_PORTS.get(dest_port, ''),
            'seq': seq,
            'ack': ack,
            'flags': flag_str,
            'payload': data[offset:]
        }
    
    def parse_udp(self, data: bytes) -> Dict:
        """Parse UDP datagram"""
        src_port, dest_port, length = struct.unpack('! H H H', data[:6])
        
        return {
            'src_port': src_port,
            'dest_port': dest_port,
            'src_service': COMMON_PORTS.get(src_port, ''),
            'dest_service': COMMON_PORTS.get(dest_port, ''),
            'length': length,
            'payload': data[8:]
        }
    
    def parse_icmp(self, data: bytes) -> Dict:
        """Parse ICMP packet"""
        icmp_type, code, checksum = struct.unpack('! B B H', data[:4])
        
        type_names = {
            0: 'Echo Reply',
            3: 'Destination Unreachable',
            4: 'Source Quench',
            5: 'Redirect',
            8: 'Echo Request',
            11: 'Time Exceeded',
            12: 'Parameter Problem',
            13: 'Timestamp Request',
            14: 'Timestamp Reply'
        }
        
        return {
            'type': icmp_type,
            'type_name': type_names.get(icmp_type, 'Unknown'),
            'code': code,
            'checksum': checksum,
            'payload': data[4:]
        }
    
    @staticmethod
    def format_mac(mac_bytes: bytes) -> str:
        """Format MAC address"""
        return ':'.join(f'{b:02x}' for b in mac_bytes)
    
    @staticmethod
    def format_ipv4(ip_bytes: bytes) -> str:
        """Format IPv4 address"""
        return '.'.join(str(b) for b in ip_bytes)
    
    def matches_filter(self, ip_info: Dict, transport_info: Dict = None) -> bool:
        """Check if packet matches filter criteria"""
        # Protocol filter
        if self.filter_proto:
            if ip_info['protocol_name'].lower() != self.filter_proto.lower():
                return False
        
        # Host filter
        if self.filter_host:
            if self.filter_host not in (ip_info['src'], ip_info['dest']):
                return False
        
        # Port filter
        if self.filter_port and transport_info:
            ports = (transport_info.get('src_port'), transport_info.get('dest_port'))
            if self.filter_port not in ports:
                return False
        
        return True
    
    def format_packet(self, timestamp: str, ip_info: Dict,
                     transport_info: Dict = None) -> str:
        """Format packet for display"""
        proto = ip_info['protocol_name']
        src = ip_info['src']
        dest = ip_info['dest']
        
        output = f"[{timestamp}] {proto:5} | {src:15}"
        
        if transport_info:
            src_port = transport_info.get('src_port', '')
            dest_port = transport_info.get('dest_port', '')
            src_svc = transport_info.get('src_service', '')
            dest_svc = transport_info.get('dest_service', '')
            flags = transport_info.get('flags', '')
            
            src_str = f"{src_port}"
            if src_svc:
                src_str += f"({src_svc})"
            
            dest_str = f"{dest_port}"
            if dest_svc:
                dest_str += f"({dest_svc})"
            
            output += f":{src_str:12} -> {dest:15}:{dest_str:12}"
            
            if flags:
                output += f" [{flags}]"
        else:
            output += f"{' ':13} -> {dest:15}"
            
            if proto == 'ICMP' and transport_info:
                output += f" {transport_info.get('type_name', '')}"
        
        return output
    
    def print_hex_dump(self, data: bytes, max_bytes: int = 64) -> None:
        """Print hex dump of data"""
        data = data[:max_bytes]
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            print(f"        {i:04x}: {hex_str:48} {ascii_str}")
    
    def capture(self, count: int = 0, timeout: int = 0, verbose: bool = False,
               show_payload: bool = False) -> None:
        """Start packet capture"""
        sock = self.create_socket()
        start_time = time.time()
        
        print(f"\n[+] Starting capture...")
        if self.filter_proto:
            print(f"[+] Protocol filter: {self.filter_proto}")
        if self.filter_host:
            print(f"[+] Host filter: {self.filter_host}")
        if self.filter_port:
            print(f"[+] Port filter: {self.filter_port}")
        print("=" * 80)
        
        try:
            while True:
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    break
                
                # Check count
                if count and self.packet_count >= count:
                    break
                
                raw_data, addr = sock.recvfrom(65535)
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                
                # Parse Ethernet frame
                dest_mac, src_mac, eth_proto, data = self.parse_ethernet(raw_data)
                
                # Only process IPv4 (0x0800)
                if eth_proto != 8:
                    continue
                
                # Parse IP
                ip_info = self.parse_ipv4(data)
                transport_info = None
                
                # Parse transport layer
                proto = ip_info['protocol']
                if proto == 6:  # TCP
                    transport_info = self.parse_tcp(ip_info['payload'])
                elif proto == 17:  # UDP
                    transport_info = self.parse_udp(ip_info['payload'])
                elif proto == 1:  # ICMP
                    transport_info = self.parse_icmp(ip_info['payload'])
                
                # Apply filters
                if not self.matches_filter(ip_info, transport_info):
                    continue
                
                self.packet_count += 1
                self.stats[ip_info['protocol_name']] += 1
                
                # Print packet info
                output = self.format_packet(timestamp, ip_info, transport_info)
                print(output)
                
                # Show payload hex dump
                if show_payload and transport_info and transport_info.get('payload'):
                    self.print_hex_dump(transport_info['payload'])
                
        except KeyboardInterrupt:
            pass
        finally:
            sock.close()
            self.print_stats()
    
    def print_stats(self) -> None:
        """Print capture statistics"""
        print("\n" + "=" * 80)
        print(f"[+] Capture Statistics:")
        print(f"    Total Packets: {self.packet_count}")
        print(f"    Protocol Breakdown:")
        for proto, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            pct = (count / self.packet_count * 100) if self.packet_count else 0
            print(f"      {proto:8}: {count:6} ({pct:.1f}%)")


def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description='NullSec Network Sniffer - Packet Capture Tool'
    )
    parser.add_argument('-i', '--interface', help='Network interface to capture on')
    parser.add_argument('-c', '--count', type=int, default=0,
                       help='Number of packets to capture (0=unlimited)')
    parser.add_argument('-t', '--timeout', type=int, default=0,
                       help='Capture timeout in seconds (0=unlimited)')
    parser.add_argument('-p', '--protocol', choices=['tcp', 'udp', 'icmp'],
                       help='Filter by protocol')
    parser.add_argument('--port', type=int, help='Filter by port number')
    parser.add_argument('--host', help='Filter by IP address')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-x', '--hexdump', action='store_true',
                       help='Show payload hex dump')
    
    args = parser.parse_args()
    
    sniffer = PacketSniffer(
        interface=args.interface,
        filter_proto=args.protocol,
        filter_port=args.port,
        filter_host=args.host
    )
    
    sniffer.capture(
        count=args.count,
        timeout=args.timeout,
        verbose=args.verbose,
        show_payload=args.hexdump
    )


if __name__ == '__main__':
    main()
