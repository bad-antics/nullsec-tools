#!/usr/bin/env python3
"""
NullSec Hash Cracker - Multi-Algorithm Hash Cracking Tool
Supports MD5, SHA1, SHA256, SHA512, NTLM, and more
Part of the NullSec Tools Collection
"""

import sys
import hashlib
import argparse
import itertools
import string
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Optional, List, Callable

BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║     _   __      ____   _____                                  ║
║    / | / /_  __/ / /  / ___/___  _____                        ║
║   /  |/ / / / / / /   \__ \/ _ \/ ___/                        ║
║  / /|  / /_/ / / /   ___/ /  __/ /__                          ║
║ /_/ |_/\__,_/_/_/   /____/\___/\___/                          ║
║                                                               ║
║                   Hash Cracker v1.0                           ║
║            Multi-Algorithm Hash Cracking                      ║
╚═══════════════════════════════════════════════════════════════╝
"""

class HashCracker:
    """Multi-algorithm hash cracking tool"""
    
    ALGORITHMS = {
        'md5': (hashlib.md5, 32),
        'sha1': (hashlib.sha1, 40),
        'sha256': (hashlib.sha256, 64),
        'sha512': (hashlib.sha512, 128),
        'sha384': (hashlib.sha384, 96),
        'sha224': (hashlib.sha224, 56),
    }
    
    def __init__(self, target_hash: str, algorithm: str = 'auto'):
        self.target_hash = target_hash.lower().strip()
        self.algorithm = algorithm
        self.hash_func = None
        self.attempts = 0
        self.found = False
        self.plaintext = None
        
        if algorithm == 'auto':
            self.algorithm = self.detect_algorithm()
        
        if self.algorithm in self.ALGORITHMS:
            self.hash_func = self.ALGORITHMS[self.algorithm][0]
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def detect_algorithm(self) -> str:
        """Auto-detect hash algorithm based on length"""
        hash_len = len(self.target_hash)
        
        for algo, (func, length) in self.ALGORITHMS.items():
            if hash_len == length:
                return algo
        
        # Default to MD5 for 32-char hashes
        if hash_len == 32:
            return 'md5'
        
        raise ValueError(f"Cannot auto-detect algorithm for hash length {hash_len}")
    
    def compute_hash(self, plaintext: str) -> str:
        """Compute hash of plaintext"""
        return self.hash_func(plaintext.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if password matches target hash"""
        self.attempts += 1
        if self.compute_hash(password) == self.target_hash:
            self.found = True
            self.plaintext = password
            return True
        return False
    
    def dictionary_attack(self, wordlist_path: str, callback: Callable = None) -> Optional[str]:
        """Perform dictionary attack using wordlist"""
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    password = line.strip()
                    if not password:
                        continue
                    
                    if self.check_password(password):
                        return password
                    
                    if callback and self.attempts % 100000 == 0:
                        callback(self.attempts)
        except FileNotFoundError:
            print(f"[-] Wordlist not found: {wordlist_path}")
        
        return None
    
    def brute_force(self, charset: str, min_len: int, max_len: int,
                   callback: Callable = None) -> Optional[str]:
        """Perform brute force attack"""
        for length in range(min_len, max_len + 1):
            for combo in itertools.product(charset, repeat=length):
                password = ''.join(combo)
                
                if self.check_password(password):
                    return password
                
                if callback and self.attempts % 100000 == 0:
                    callback(self.attempts, password)
        
        return None
    
    def rule_attack(self, base_words: List[str], rules: List[str]) -> Optional[str]:
        """Apply transformation rules to base words"""
        for word in base_words:
            # Original word
            if self.check_password(word):
                return word
            
            for rule in rules:
                transformed = self.apply_rule(word, rule)
                if transformed and self.check_password(transformed):
                    return transformed
        
        return None
    
    def apply_rule(self, word: str, rule: str) -> Optional[str]:
        """Apply a transformation rule to a word"""
        if rule == 'capitalize':
            return word.capitalize()
        elif rule == 'uppercase':
            return word.upper()
        elif rule == 'lowercase':
            return word.lower()
        elif rule == 'reverse':
            return word[::-1]
        elif rule == 'leet':
            leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
            return ''.join(leet_map.get(c.lower(), c) for c in word)
        elif rule.startswith('append_'):
            suffix = rule[7:]
            return word + suffix
        elif rule.startswith('prepend_'):
            prefix = rule[8:]
            return prefix + word
        elif rule.startswith('year_'):
            year = rule[5:]
            return word + year
        return None


def progress_callback(attempts: int, current: str = ""):
    """Print progress"""
    current_str = f" | Current: {current[:20]}" if current else ""
    print(f"\r[*] Attempts: {attempts:,}{current_str}", end='', flush=True)


def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description='NullSec Hash Cracker - Multi-Algorithm Hash Cracking'
    )
    parser.add_argument('hash', help='Target hash to crack')
    parser.add_argument('-a', '--algorithm', default='auto',
                       choices=['auto', 'md5', 'sha1', 'sha256', 'sha512'],
                       help='Hash algorithm (default: auto-detect)')
    parser.add_argument('-w', '--wordlist', help='Path to wordlist file')
    parser.add_argument('-b', '--bruteforce', action='store_true',
                       help='Enable brute force mode')
    parser.add_argument('--charset', default='lowercase',
                       choices=['lowercase', 'uppercase', 'digits', 'alpha', 'alnum', 'all'],
                       help='Character set for brute force')
    parser.add_argument('--min-len', type=int, default=1, help='Minimum password length')
    parser.add_argument('--max-len', type=int, default=6, help='Maximum password length')
    parser.add_argument('-r', '--rules', action='store_true',
                       help='Enable rule-based attack')
    
    args = parser.parse_args()
    
    # Character sets
    charsets = {
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'digits': string.digits,
        'alpha': string.ascii_letters,
        'alnum': string.ascii_letters + string.digits,
        'all': string.ascii_letters + string.digits + string.punctuation
    }
    
    try:
        cracker = HashCracker(args.hash, args.algorithm)
        print(f"\n[+] Target Hash: {args.hash}")
        print(f"[+] Algorithm: {cracker.algorithm.upper()}")
        print("=" * 50)
        
        result = None
        
        # Dictionary attack
        if args.wordlist:
            print(f"\n[*] Starting dictionary attack with: {args.wordlist}")
            result = cracker.dictionary_attack(args.wordlist, progress_callback)
        
        # Rule-based attack
        if not result and args.rules and args.wordlist:
            print("\n[*] Starting rule-based attack...")
            rules = ['capitalize', 'uppercase', 'leet', 'reverse',
                    'append_123', 'append_!', 'year_2024', 'year_2025']
            with open(args.wordlist, 'r', errors='ignore') as f:
                words = [line.strip() for line in f][:10000]
            result = cracker.rule_attack(words, rules)
        
        # Brute force
        if not result and args.bruteforce:
            charset = charsets[args.charset]
            print(f"\n[*] Starting brute force (length {args.min_len}-{args.max_len})...")
            print(f"[*] Character set: {args.charset} ({len(charset)} chars)")
            result = cracker.brute_force(charset, args.min_len, args.max_len, progress_callback)
        
        print("\n" + "=" * 50)
        if result:
            print(f"[+] PASSWORD FOUND!")
            print(f"[+] Hash: {args.hash}")
            print(f"[+] Plaintext: {result}")
            print(f"[+] Attempts: {cracker.attempts:,}")
        else:
            print(f"[-] Password not found")
            print(f"[-] Attempts: {cracker.attempts:,}")
        
    except ValueError as e:
        print(f"[-] Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
