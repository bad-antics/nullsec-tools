# 🛠️ NullSec Tools Wiki

Welcome to the **NullSec Tools** documentation! This wiki provides comprehensive guides for installation, usage, and contribution.

## 📖 Quick Navigation

| Section | Description |
|---------|-------------|
| [Installation](Installation) | Setup guide for all platforms |
| [Tools Overview](Tools-Overview) | Complete list of all tools |
| [Python Tools](Python-Tools) | Python-based security tools |
| [Go Tools](Go-Tools) | Go-based network tools |
| [Rust Tools](Rust-Tools) | Rust-based system tools |
| [C Tools](C-Tools) | Low-level C utilities |
| [Configuration](Configuration) | Config files and customization |
| [API Reference](API-Reference) | Library APIs and interfaces |
| [Contributing](Contributing) | How to contribute |
| [Troubleshooting](Troubleshooting) | Common issues and fixes |

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools

# Install Python tools
pip install -r requirements.txt

# Build Go tools
cd go && go build ./...

# Build Rust tools
cd rust && cargo build --release

# Build C tools
cd c && make
```

## 🔧 Tool Categories

### Reconnaissance
- `email_hunter` - Email address enumeration
- `shodan_scan` - Shodan API integration
- `subdomain_enum` - Subdomain discovery

### Network Analysis
- `portscan` - Fast TCP/UDP port scanner
- `sniffer` - Network packet capture
- `arpwatch` - ARP monitoring

### Password/Hash
- `hashcrack` - Multi-algorithm hash cracker
- `hashwitch` - Hash identification

### Web Security
- `crawler` - Web crawler with JS rendering
- `webfuzz` - Web application fuzzer

### Forensics
- `memgrep` - Memory analysis
- `logparse` - Log file parser

## 📊 Language Distribution

| Language | Tools | Purpose |
|----------|-------|---------|
| Python | 15+ | Scripting, automation, web tools |
| Go | 8+ | Network tools, concurrent scanning |
| Rust | 6+ | System tools, performance-critical |
| C | 4+ | Low-level utilities |

## 🔗 Related Projects

- [NullSec Linux](https://github.com/bad-antics/nullsec-linux) - Security distro with all tools pre-installed
- [Marshall Browser](https://github.com/bad-antics/marshall) - OSINT-focused web browser
- [NullSec Framework](https://github.com/bad-antics/nullsec-framework) - Modular security framework

## ⚠️ Legal Notice

These tools are provided for **authorized security testing and educational purposes only**. Users must obtain proper authorization before testing any systems they do not own.

---

<p align="center">
  <b>Part of the NullSec Security Suite</b><br>
  <a href="https://github.com/bad-antics">@bad-antics</a>
</p>
