#!/usr/bin/env python3
"""
NullSec Email Hunter - OSINT Email Discovery Tool
Discovers email addresses associated with a domain using multiple sources
Part of the NullSec Tools Collection
"""

import re
import sys
import json
import argparse
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set, Dict

BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║     _   __      ____   _____              ______              ║
║    / | / /_  __/ / /  / ___/___  _____   /_  __/___  ____     ║
║   /  |/ / / / / / /   \__ \/ _ \/ ___/    / / / __ \/ __ \    ║
║  / /|  / /_/ / / /   ___/ /  __/ /__     / / / /_/ / /_/ /    ║
║ /_/ |_/\__,_/_/_/   /____/\___/\___/    /_/  \____/\____/     ║
║                                                               ║
║                   Email Hunter v1.0                           ║
║             OSINT Email Discovery Tool                        ║
╚═══════════════════════════════════════════════════════════════╝
"""

class EmailHunter:
    """Email discovery and validation tool"""
    
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    
    COMMON_PATTERNS = [
        '{first}.{last}',
        '{first}{last}',
        '{f}{last}',
        '{first}_{last}',
        '{first}-{last}',
        '{last}.{first}',
        '{first}',
        '{last}',
        '{f}.{last}',
        '{first}.{l}',
    ]
    
    def __init__(self, domain: str, verbose: bool = False):
        self.domain = domain.lower().strip()
        self.emails: Set[str] = set()
        self.verbose = verbose
        self.sources_checked = []
        
    def log(self, msg: str):
        if self.verbose:
            print(f"[*] {msg}")
    
    def search_web(self, query: str) -> str:
        """Perform a web search and return results"""
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=100"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            self.log(f"Search error: {e}")
            return ""
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract emails matching the target domain"""
        all_emails = self.EMAIL_PATTERN.findall(text)
        return {email.lower() for email in all_emails 
                if email.lower().endswith(f"@{self.domain}")}
    
    def search_google_dorks(self) -> Set[str]:
        """Use Google dorks to find emails"""
        self.log("Searching via Google dorks...")
        self.sources_checked.append('google_dorks')
        
        dorks = [
            f'site:{self.domain} email',
            f'site:{self.domain} contact',
            f'"{self.domain}" email',
            f'intext:"@{self.domain}"',
            f'filetype:pdf site:{self.domain}',
            f'filetype:doc site:{self.domain}',
        ]
        
        found = set()
        for dork in dorks:
            result = self.search_web(dork)
            found.update(self.extract_emails_from_text(result))
        
        return found
    
    def search_hunter_io(self, api_key: str = None) -> Set[str]:
        """Search Hunter.io for domain emails"""
        if not api_key:
            self.log("Hunter.io: No API key provided, skipping")
            return set()
        
        self.log("Searching Hunter.io...")
        self.sources_checked.append('hunter_io')
        
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={self.domain}&api_key={api_key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                return {email['value'] for email in data.get('data', {}).get('emails', [])}
        except Exception as e:
            self.log(f"Hunter.io error: {e}")
            return set()
    
    def generate_patterns(self, first: str, last: str) -> List[str]:
        """Generate email patterns from name"""
        patterns = []
        first = first.lower()
        last = last.lower()
        
        for pattern in self.COMMON_PATTERNS:
            email = pattern.format(
                first=first,
                last=last,
                f=first[0] if first else '',
                l=last[0] if last else ''
            ) + f"@{self.domain}"
            patterns.append(email)
        
        return patterns
    
    def check_social_media(self) -> Set[str]:
        """Check social media for leaked emails"""
        self.log("Checking social media sources...")
        self.sources_checked.append('social_media')
        
        queries = [
            f'site:linkedin.com "{self.domain}"',
            f'site:twitter.com "@{self.domain}"',
            f'site:github.com "{self.domain}"',
        ]
        
        found = set()
        for query in queries:
            result = self.search_web(query)
            found.update(self.extract_emails_from_text(result))
        
        return found
    
    def check_pastebin_leaks(self) -> Set[str]:
        """Check paste sites for leaked emails"""
        self.log("Checking paste sites for leaks...")
        self.sources_checked.append('paste_sites')
        
        result = self.search_web(f'site:pastebin.com "@{self.domain}"')
        return self.extract_emails_from_text(result)
    
    def run_full_scan(self, hunter_api: str = None) -> Dict:
        """Run a comprehensive email discovery scan"""
        print(f"\n[+] Starting email discovery for: {self.domain}")
        print("=" * 50)
        
        # Run all discovery methods
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.search_google_dorks): 'google',
                executor.submit(self.check_social_media): 'social',
                executor.submit(self.check_pastebin_leaks): 'pastes',
            }
            
            if hunter_api:
                futures[executor.submit(self.search_hunter_io, hunter_api)] = 'hunter'
            
            for future in as_completed(futures):
                source = futures[future]
                try:
                    emails = future.result()
                    self.emails.update(emails)
                    if emails:
                        print(f"[+] {source}: Found {len(emails)} emails")
                except Exception as e:
                    print(f"[-] {source}: Error - {e}")
        
        return {
            'domain': self.domain,
            'emails': sorted(list(self.emails)),
            'count': len(self.emails),
            'sources': self.sources_checked
        }

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description='NullSec Email Hunter - OSINT Email Discovery'
    )
    parser.add_argument('domain', help='Target domain (e.g., example.com)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--hunter-api', help='Hunter.io API key')
    parser.add_argument('-o', '--output', help='Output file (JSON)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    hunter = EmailHunter(args.domain, verbose=args.verbose)
    results = hunter.run_full_scan(hunter_api=args.hunter_api)
    
    print("\n" + "=" * 50)
    print(f"[+] Scan Complete!")
    print(f"[+] Found {results['count']} unique emails for {args.domain}")
    print("=" * 50)
    
    if results['emails']:
        print("\nDiscovered Emails:")
        for email in results['emails']:
            print(f"  • {email}")
    
    if args.output:
        with open(args.output, 'w') as f:
            if args.format == 'json':
                json.dump(results, f, indent=2)
            else:
                f.write(f"Domain: {results['domain']}\n")
                f.write(f"Total: {results['count']}\n\n")
                for email in results['emails']:
                    f.write(f"{email}\n")
        print(f"\n[+] Results saved to: {args.output}")

if __name__ == '__main__':
    main()
