# 🔧 Tools Overview

Complete reference of all tools included in NullSec Tools.

---

## Quick Reference

| Tool | Language | Category | Description |
|------|----------|----------|-------------|
| `email_hunter` | Python | Recon | Email address enumeration |
| `portscan` | Python/Go | Network | TCP/UDP port scanner |
| `hashcrack` | Python | Crypto | Multi-algorithm hash cracker |
| `sniffer` | Python | Network | Packet capture and analysis |
| `crawler` | Python | Web | Web crawler with JS support |
| `subdomain_enum` | Go | Recon | Fast subdomain discovery |
| `arpwatch` | Go | Network | ARP table monitoring |
| `dnsenum` | Go | Recon | DNS enumeration |
| `hashwitch` | Rust | Crypto | Hash identification |
| `memgrep` | Rust | Forensics | Memory pattern search |
| `entropy` | Rust | Analysis | File entropy analyzer |
| `hexdump` | C | Utility | Binary file hex viewer |
| `logparse` | C | Forensics | Log file parser |

---

## Reconnaissance Tools

### email_hunter
**Language:** Python  
**Purpose:** Enumerate email addresses from various sources

```bash
email_hunter -d example.com -o emails.txt
email_hunter --domain example.com --sources google,bing,linkedin
```

**Options:**
- `-d, --domain` - Target domain
- `-o, --output` - Output file
- `--sources` - Search sources (google, bing, linkedin, hunter.io)
- `--verify` - Verify email addresses
- `-t, --threads` - Number of threads

---

### subdomain_enum
**Language:** Go  
**Purpose:** Fast concurrent subdomain enumeration

```bash
subdomain_enum -d example.com -w wordlist.txt
subdomain_enum --domain example.com --resolvers resolvers.txt -o subs.txt
```

**Options:**
- `-d, --domain` - Target domain
- `-w, --wordlist` - Subdomain wordlist
- `-o, --output` - Output file
- `--resolvers` - Custom DNS resolvers
- `-c, --concurrency` - Concurrent requests (default: 50)
- `--wildcard` - Detect wildcard DNS

---

### dnsenum
**Language:** Go  
**Purpose:** Comprehensive DNS enumeration

```bash
dnsenum -d example.com
dnsenum --domain example.com --zone-transfer --reverse
```

**Options:**
- `-d, --domain` - Target domain
- `--zone-transfer` - Attempt zone transfer
- `--reverse` - Reverse DNS lookup
- `--mx` - Enumerate MX records
- `--ns` - Enumerate NS records

---

## Network Tools

### portscan
**Language:** Python/Go  
**Purpose:** Fast TCP/UDP port scanning

```bash
# Python version
portscan -t 192.168.1.1 -p 1-1000
portscan --target 192.168.1.0/24 --top-ports 100

# Go version (faster)
portscan-go -t 192.168.1.1 -p 1-65535 -c 1000
```

**Options:**
- `-t, --target` - Target IP/range/CIDR
- `-p, --ports` - Port range (1-1000, 22,80,443)
- `--top-ports` - Scan top N common ports
- `-c, --concurrency` - Concurrent connections
- `--udp` - UDP scan
- `-sV` - Version detection
- `-o, --output` - Output file (json, csv, txt)

---

### sniffer
**Language:** Python  
**Purpose:** Network packet capture and analysis

```bash
sniffer -i eth0 -f "tcp port 80"
sniffer --interface wlan0 --filter "host 192.168.1.1" -o capture.pcap
```

**Options:**
- `-i, --interface` - Network interface
- `-f, --filter` - BPF filter expression
- `-o, --output` - Save to pcap file
- `-c, --count` - Number of packets to capture
- `--hex` - Display hex dump
- `--follow` - Follow TCP streams

---

### arpwatch
**Language:** Go  
**Purpose:** Monitor ARP table for changes

```bash
arpwatch -i eth0
arpwatch --interface wlan0 --alert-cmd "notify-send"
```

**Options:**
- `-i, --interface` - Network interface
- `--alert-cmd` - Command to run on changes
- `--db` - ARP database file
- `-d, --daemon` - Run as daemon

---

## Password/Hash Tools

### hashcrack
**Language:** Python  
**Purpose:** Multi-algorithm hash cracker

```bash
hashcrack -h 5d41402abc4b2a76b9719d911017c592 -w rockyou.txt
hashcrack --hash-file hashes.txt --wordlist wordlist.txt --type md5
hashcrack -h '$2a$10$...' --type bcrypt --rules
```

**Supported Algorithms:**
- MD5, SHA1, SHA256, SHA512
- bcrypt, scrypt, argon2
- NTLM, LM
- MySQL, PostgreSQL
- WPA/WPA2

**Options:**
- `-h, --hash` - Single hash or hash file
- `-w, --wordlist` - Wordlist file
- `-t, --type` - Hash algorithm (auto-detect if omitted)
- `--rules` - Apply mutation rules
- `-m, --mode` - 0=wordlist, 1=bruteforce, 2=hybrid
- `--gpu` - Use GPU acceleration

---

### hashwitch
**Language:** Rust  
**Purpose:** Identify hash algorithms

```bash
hashwitch 5d41402abc4b2a76b9719d911017c592
hashwitch --file hashes.txt
```

**Output:**
```
Hash: 5d41402abc4b2a76b9719d911017c592
Possible algorithms:
  [95%] MD5
  [80%] MD4
  [70%] NTLM
```

---

## Web Security Tools

### crawler
**Language:** Python  
**Purpose:** Web crawler with JavaScript rendering

```bash
crawler -u https://example.com -d 3
crawler --url https://example.com --depth 5 --js --screenshots
```

**Options:**
- `-u, --url` - Starting URL
- `-d, --depth` - Crawl depth
- `--js` - Enable JavaScript rendering
- `--screenshots` - Take screenshots
- `--forms` - Extract forms
- `--links` - Extract all links
- `-o, --output` - Output directory

---

### webfuzz
**Language:** Python  
**Purpose:** Web application fuzzer

```bash
webfuzz -u "https://example.com/api?id=FUZZ" -w payloads.txt
webfuzz --url https://example.com/FUZZ --wordlist dirs.txt --mc 200,301
```

**Options:**
- `-u, --url` - URL with FUZZ keyword
- `-w, --wordlist` - Payload wordlist
- `--mc` - Match HTTP codes
- `--fc` - Filter HTTP codes
- `--ms` - Match response size
- `-H, --header` - Custom headers
- `-t, --threads` - Concurrent threads

---

## Forensics Tools

### memgrep
**Language:** Rust  
**Purpose:** Search patterns in memory dumps

```bash
memgrep -f memory.dmp -p "password"
memgrep --file memory.dmp --pattern "BEGIN RSA" --hex
```

**Options:**
- `-f, --file` - Memory dump file
- `-p, --pattern` - Search pattern
- `--regex` - Use regex pattern
- `--hex` - Search hex pattern
- `-o, --output` - Output matches to file

---

### logparse
**Language:** C  
**Purpose:** Parse and analyze log files

```bash
logparse -f /var/log/auth.log -t syslog
logparse --file access.log --type apache --filter "404"
```

**Supported Formats:**
- syslog
- Apache/nginx access logs
- JSON logs
- Windows Event logs

---

## Utility Tools

### hexdump
**Language:** C  
**Purpose:** Display binary files in hex format

```bash
hexdump -f binary.exe
hexdump --file program -o 0x1000 -l 256
```

**Options:**
- `-f, --file` - Input file
- `-o, --offset` - Start offset
- `-l, --length` - Number of bytes
- `-c, --columns` - Bytes per row

---

### entropy
**Language:** Rust  
**Purpose:** Calculate file entropy

```bash
entropy -f suspicious.exe
entropy --file binary --block-size 256 --graph
```

**Output:**
```
File: suspicious.exe
Overall entropy: 7.82 (high - possibly packed/encrypted)

Block analysis:
  0x0000-0x0100: 4.21 (low)
  0x0100-0x0200: 7.95 (high) ← Possible encrypted section
  0x0200-0x0300: 7.91 (high)
```

---

## See Also

- [Python Tools](Python-Tools) - Detailed Python tool documentation
- [Go Tools](Go-Tools) - Detailed Go tool documentation
- [Rust Tools](Rust-Tools) - Detailed Rust tool documentation
- [API Reference](API-Reference) - Library APIs
