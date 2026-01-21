#!/usr/bin/env python3
"""
NullSec Subdomain Enumerator
Fast async subdomain discovery tool
Author: bad-antics | Twitter: @AnonAntics | Discord: discord.gg/killers
"""

import asyncio
import aiohttp
import argparse
import dns.resolver
import sys
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║     ███╗   ██╗██╗   ██╗██╗     ██╗     ███████╗███████╗   ║
║     ████╗  ██║██║   ██║██║     ██║     ██╔════╝██╔════╝   ║
║     ██╔██╗ ██║██║   ██║██║     ██║     ███████╗█████╗     ║
║     ██║╚██╗██║██║   ██║██║     ██║     ╚════██║██╔══╝     ║
║     ██║ ╚████║╚██████╔╝███████╗███████╗███████║███████╗   ║
║     ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝   ║
║                  SUBDOMAIN ENUMERATOR                      ║
║            bad-antics | @AnonAntics | discord.gg/killers  ║
╚═══════════════════════════════════════════════════════════╝
"""

DEFAULT_WORDLIST = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "ns2",
    "vpn", "admin", "test", "portal", "blog", "dev", "staging", "api", "m",
    "mobile", "app", "cdn", "static", "assets", "img", "images", "video",
    "media", "download", "uploads", "files", "docs", "wiki", "help", "support",
    "status", "beta", "alpha", "demo", "shop", "store", "secure", "login",
    "auth", "sso", "git", "gitlab", "github", "jenkins", "ci", "build",
    "docker", "k8s", "kubernetes", "aws", "azure", "cloud", "backup", "db",
    "database", "mysql", "postgres", "mongo", "redis", "elastic", "kibana",
    "grafana", "prometheus", "nagios", "zabbix", "monitor", "logs", "sentry"
]

class SubdomainEnumerator:
    def __init__(self, domain: str, wordlist: List[str], threads: int = 50):
        self.domain = domain
        self.wordlist = wordlist
        self.threads = threads
        self.found: Set[str] = set()
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 2
        self.resolver.lifetime = 2

    def dns_resolve(self, subdomain: str) -> bool:
        """Resolve subdomain via DNS"""
        try:
            full_domain = f"{subdomain}.{self.domain}"
            self.resolver.resolve(full_domain, 'A')
            return True
        except:
            return False

    async def http_check(self, session: aiohttp.ClientSession, subdomain: str) -> bool:
        """Check if subdomain responds via HTTP"""
        full_domain = f"{subdomain}.{self.domain}"
        for proto in ['https', 'http']:
            try:
                async with session.get(f"{proto}://{full_domain}", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status < 500:
                        return True
            except:
                continue
        return False

    def enumerate_dns(self) -> Set[str]:
        """DNS-based enumeration"""
        print(f"[*] Starting DNS enumeration with {len(self.wordlist)} subdomains...")
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            results = list(executor.map(self.dns_resolve, self.wordlist))
        
        for i, found in enumerate(results):
            if found:
                subdomain = f"{self.wordlist[i]}.{self.domain}"
                self.found.add(subdomain)
                print(f"[+] Found: {subdomain}")
        
        return self.found

    async def enumerate_http(self) -> Set[str]:
        """HTTP-based enumeration"""
        print(f"[*] Starting HTTP enumeration...")
        connector = aiohttp.TCPConnector(limit=self.threads, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.http_check(session, sub) for sub in self.wordlist]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, found in enumerate(results):
                if found is True:
                    subdomain = f"{self.wordlist[i]}.{self.domain}"
                    self.found.add(subdomain)
                    if subdomain not in self.found:
                        print(f"[+] Found: {subdomain}")
        
        return self.found

def load_wordlist(path: str) -> List[str]:
    """Load wordlist from file"""
    try:
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] Wordlist not found: {path}")
        sys.exit(1)

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description='NullSec Subdomain Enumerator')
    parser.add_argument('domain', help='Target domain')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--dns-only', action='store_true', help='DNS enumeration only')
    parser.add_argument('--http-only', action='store_true', help='HTTP enumeration only')
    
    args = parser.parse_args()
    
    wordlist = load_wordlist(args.wordlist) if args.wordlist else DEFAULT_WORDLIST
    enumerator = SubdomainEnumerator(args.domain, wordlist, args.threads)
    
    found = set()
    
    if not args.http_only:
        found.update(enumerator.enumerate_dns())
    
    if not args.dns_only:
        asyncio.run(enumerator.enumerate_http())
        found.update(enumerator.found)
    
    print(f"\n[*] Total subdomains found: {len(found)}")
    
    if args.output and found:
        with open(args.output, 'w') as f:
            f.write('\n'.join(sorted(found)))
        print(f"[*] Results saved to: {args.output}")

if __name__ == '__main__':
    main()
