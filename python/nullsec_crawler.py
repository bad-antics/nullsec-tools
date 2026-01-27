#!/usr/bin/env python3
"""
NullSec Web Crawler - Deep Web Reconnaissance Tool
Crawl and map web applications, discover endpoints and resources
Part of the NullSec Tools Collection
"""

import sys
import re
import json
import argparse
import urllib.parse
from typing import Set, Dict, List, Optional
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[-] Required: pip install requests beautifulsoup4")
    sys.exit(1)

BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║     _   __      ____   _____                                  ║
║    / | / /_  __/ / /  / ___/___  _____                        ║
║   /  |/ / / / / / /   \__ \/ _ \/ ___/                        ║
║  / /|  / /_/ / / /   ___/ /  __/ /__                          ║
║ /_/ |_/\__,_/_/_/   /____/\___/\___/                          ║
║                                                               ║
║                   Web Crawler v1.0                            ║
║           Deep Web Reconnaissance Tool                        ║
╚═══════════════════════════════════════════════════════════════╝
"""

class WebCrawler:
    """Deep web crawler for reconnaissance"""
    
    def __init__(self, base_url: str, max_depth: int = 3, threads: int = 10,
                 respect_robots: bool = True, user_agent: str = None):
        self.base_url = base_url.rstrip('/')
        self.parsed_base = urllib.parse.urlparse(base_url)
        self.max_depth = max_depth
        self.threads = threads
        self.respect_robots = respect_robots
        
        self.visited: Set[str] = set()
        self.to_visit: Set[str] = {self.base_url}
        self.external_links: Set[str] = set()
        self.emails: Set[str] = set()
        self.forms: List[Dict] = []
        self.scripts: Set[str] = set()
        self.comments: List[str] = []
        self.parameters: Set[str] = set()
        self.endpoints: Dict[str, Dict] = {}
        self.errors: List[str] = []
        
        self.disallowed: Set[str] = set()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'NullSec-Crawler/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        if respect_robots:
            self.parse_robots()
    
    def parse_robots(self) -> None:
        """Parse robots.txt for disallowed paths"""
        try:
            robots_url = f"{self.parsed_base.scheme}://{self.parsed_base.netloc}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('disallow:'):
                        path = line[9:].strip()
                        if path:
                            self.disallowed.add(path)
                            
                print(f"[+] Found {len(self.disallowed)} disallowed paths in robots.txt")
        except Exception:
            pass
    
    def is_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots:
            return True
        
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or '/'
        
        for disallowed in self.disallowed:
            if path.startswith(disallowed):
                return False
        
        return True
    
    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to same domain"""
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc == self.parsed_base.netloc or not parsed.netloc
    
    def normalize_url(self, url: str, current_url: str) -> Optional[str]:
        """Normalize and validate URL"""
        # Remove fragments
        url = url.split('#')[0]
        
        if not url or url.startswith(('javascript:', 'mailto:', 'tel:', 'data:')):
            return None
        
        # Handle relative URLs
        if not url.startswith(('http://', 'https://')):
            url = urllib.parse.urljoin(current_url, url)
        
        # Parse and normalize
        parsed = urllib.parse.urlparse(url)
        
        # Rebuild without fragments
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path or '/',
            parsed.params,
            parsed.query,
            ''
        ))
        
        return normalized
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        """Extract all links from page"""
        links = set()
        
        # <a> tags
        for a in soup.find_all('a', href=True):
            url = self.normalize_url(a['href'], current_url)
            if url:
                links.add(url)
        
        # <link> tags
        for link in soup.find_all('link', href=True):
            url = self.normalize_url(link['href'], current_url)
            if url:
                links.add(url)
        
        # <script> src
        for script in soup.find_all('script', src=True):
            url = self.normalize_url(script['src'], current_url)
            if url:
                self.scripts.add(url)
        
        # <img> src
        for img in soup.find_all('img', src=True):
            url = self.normalize_url(img['src'], current_url)
            if url:
                links.add(url)
        
        return links
    
    def extract_forms(self, soup: BeautifulSoup, current_url: str) -> None:
        """Extract form information"""
        for form in soup.find_all('form'):
            form_data = {
                'action': self.normalize_url(form.get('action', ''), current_url),
                'method': form.get('method', 'GET').upper(),
                'page': current_url,
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', '')
                }
                if input_data['name']:
                    form_data['inputs'].append(input_data)
                    self.parameters.add(input_data['name'])
            
            self.forms.append(form_data)
    
    def extract_emails(self, text: str) -> None:
        """Extract email addresses"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        self.emails.update(emails)
    
    def extract_comments(self, html: str) -> None:
        """Extract HTML comments"""
        comment_pattern = r'<!--(.*?)-->'
        comments = re.findall(comment_pattern, html, re.DOTALL)
        for comment in comments:
            comment = comment.strip()
            if comment and len(comment) > 5:
                self.comments.append(comment[:200])
    
    def extract_parameters(self, url: str) -> None:
        """Extract URL parameters"""
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        self.parameters.update(params.keys())
    
    def crawl_page(self, url: str) -> Set[str]:
        """Crawl a single page"""
        if not self.is_allowed(url):
            return set()
        
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            
            # Store endpoint info
            self.endpoints[url] = {
                'status': response.status_code,
                'content_type': response.headers.get('Content-Type', ''),
                'server': response.headers.get('Server', ''),
                'size': len(response.content)
            }
            
            if response.status_code != 200:
                return set()
            
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return set()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract information
            links = self.extract_links(soup, url)
            self.extract_forms(soup, url)
            self.extract_emails(html)
            self.extract_comments(html)
            self.extract_parameters(url)
            
            # Separate internal and external links
            internal_links = set()
            for link in links:
                if self.is_same_domain(link):
                    internal_links.add(link)
                else:
                    self.external_links.add(link)
            
            return internal_links
            
        except requests.exceptions.Timeout:
            self.errors.append(f"Timeout: {url}")
        except requests.exceptions.ConnectionError:
            self.errors.append(f"Connection error: {url}")
        except Exception as e:
            self.errors.append(f"Error crawling {url}: {str(e)}")
        
        return set()
    
    def crawl(self, callback=None) -> None:
        """Start crawling"""
        depth = 0
        
        while self.to_visit and depth < self.max_depth:
            depth += 1
            current_batch = self.to_visit - self.visited
            self.to_visit = set()
            
            if not current_batch:
                break
            
            print(f"\n[*] Depth {depth}: Crawling {len(current_batch)} URLs...")
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {
                    executor.submit(self.crawl_page, url): url
                    for url in current_batch
                }
                
                for future in as_completed(futures):
                    url = futures[future]
                    self.visited.add(url)
                    
                    try:
                        new_links = future.result()
                        self.to_visit.update(new_links - self.visited)
                        
                        if callback:
                            callback(len(self.visited), len(self.to_visit))
                    except Exception as e:
                        self.errors.append(f"Error processing {url}: {str(e)}")
            
            print(f"    Visited: {len(self.visited)} | Queued: {len(self.to_visit)}")
    
    def get_results(self) -> Dict:
        """Get crawl results"""
        return {
            'base_url': self.base_url,
            'pages_crawled': len(self.visited),
            'internal_urls': sorted(self.visited),
            'external_urls': sorted(self.external_links),
            'emails': sorted(self.emails),
            'forms': self.forms,
            'scripts': sorted(self.scripts),
            'parameters': sorted(self.parameters),
            'comments': self.comments[:50],  # Limit comments
            'endpoints': self.endpoints,
            'errors': self.errors[:20]  # Limit errors
        }
    
    def print_summary(self) -> None:
        """Print crawl summary"""
        print("\n" + "=" * 60)
        print("CRAWL SUMMARY")
        print("=" * 60)
        print(f"\n[+] Base URL: {self.base_url}")
        print(f"[+] Pages Crawled: {len(self.visited)}")
        print(f"[+] External Links: {len(self.external_links)}")
        print(f"[+] Forms Found: {len(self.forms)}")
        print(f"[+] Emails Found: {len(self.emails)}")
        print(f"[+] Scripts Found: {len(self.scripts)}")
        print(f"[+] Parameters Found: {len(self.parameters)}")
        print(f"[+] Comments Found: {len(self.comments)}")
        
        if self.emails:
            print(f"\n[+] Emails Discovered:")
            for email in sorted(self.emails)[:10]:
                print(f"    - {email}")
        
        if self.parameters:
            print(f"\n[+] Parameters Discovered:")
            for param in sorted(self.parameters)[:20]:
                print(f"    - {param}")
        
        if self.forms:
            print(f"\n[+] Forms Discovered:")
            for form in self.forms[:5]:
                print(f"    [{form['method']}] {form['action']}")
                for inp in form['inputs'][:3]:
                    print(f"        - {inp['name']} ({inp['type']})")
        
        if self.errors:
            print(f"\n[-] Errors ({len(self.errors)}):")
            for error in self.errors[:5]:
                print(f"    - {error}")


def progress_callback(visited: int, queued: int) -> None:
    """Print progress"""
    print(f"\r    Progress: {visited} visited, {queued} queued", end='', flush=True)


def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description='NullSec Web Crawler - Deep Web Reconnaissance'
    )
    parser.add_argument('url', help='Target URL to crawl')
    parser.add_argument('-d', '--depth', type=int, default=3,
                       help='Maximum crawl depth (default: 3)')
    parser.add_argument('-t', '--threads', type=int, default=10,
                       help='Number of threads (default: 10)')
    parser.add_argument('--no-robots', action='store_true',
                       help='Ignore robots.txt')
    parser.add_argument('-o', '--output', help='Output JSON file')
    parser.add_argument('-u', '--user-agent', help='Custom user agent')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    print(f"\n[+] Target: {args.url}")
    print(f"[+] Max Depth: {args.depth}")
    print(f"[+] Threads: {args.threads}")
    print(f"[+] Respect Robots.txt: {not args.no_robots}")
    
    crawler = WebCrawler(
        base_url=args.url,
        max_depth=args.depth,
        threads=args.threads,
        respect_robots=not args.no_robots,
        user_agent=args.user_agent
    )
    
    try:
        crawler.crawl(callback=progress_callback)
    except KeyboardInterrupt:
        print("\n\n[!] Crawl interrupted by user")
    
    crawler.print_summary()
    
    if args.output:
        results = crawler.get_results()
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[+] Results saved to: {args.output}")


if __name__ == '__main__':
    main()
