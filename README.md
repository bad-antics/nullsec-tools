<div align="center">

# 🔐 NullSec Tools

### Professional Security Toolkit by bad-antics

[![License: NPL](https://img.shields.io/badge/License-NullSec%20Public-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-blue.svg)]()
[![Shell](https://img.shields.io/badge/Shell-Bash-green.svg)]()
[![Tools](https://img.shields.io/badge/Tools-50+-purple.svg)]()
[![GitHub](https://img.shields.io/badge/GitHub-bad--antics-black.svg)](https://github.com/bad-antics)

```
    _   __      ____  _____           
   / | / /_  __/ / / / ___/___  _____ 
  /  |/ / / / / / /  \__ \/ _ \/ ___/ 
 / /|  / /_/ / / /  ___/ /  __/ /__   
/_/ |_/\__,_/_/_/  /____/\___/\___/   
                                      
    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
       ██║   ██║   ██║██║   ██║██║     ███████╗
       ██║   ██║   ██║██║   ██║██║     ╚════██║
       ██║   ╚██████╔╝╚██████╔╝███████╗███████║
       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝

    [ bad-antics development | Est. 2025 ]
```

</div>

---

## ⚠️ Legal Disclaimer

**These tools are for AUTHORIZED SECURITY TESTING ONLY.**

By using these tools, you agree to:
- Only use them on systems you own or have explicit written permission to test
- Comply with all applicable laws and regulations
- Accept full responsibility for your actions
- Not use these tools for malicious purposes

**The developers assume no liability for misuse of these tools.**

---

## 📦 Tool Categories

### 🔴 Red Team / Offensive

| Tool | Description |
|------|-------------|
| `nullsec-scan` | Network & port scanner |
| `nullsec-crack` | Password cracking wrapper (John/Hashcat) |
| `nullsec-payload` | Payload generation & encoding |
| `nullsec-enum` | Service enumeration toolkit |
| `nullsec-osint` | Open Source Intelligence gathering |
| `nullsec-c2` | Command & Control framework wrapper |
| `nullsec-spoof` | Identity/MAC/DNS spoofing |
| `nullsec-portknock` | Port knocking client/server |
| `nullsec-honeypot` | Lightweight honeypot system |
| `nullsec-wordlist` | Wordlist generation |
| `nullsec-evade` | Anti-detection techniques |

### 🔵 Blue Team / Defensive

| Tool | Description |
|------|-------------|
| `nullsec-harden` | System hardening toolkit |
| `nullsec-audit` | Security audit framework |
| `nullsec-monitor` | System monitoring |
| `nullsec-netwatch` | Network traffic analyzer |
| `nullsec-dfir` | Digital Forensics & IR |
| `nullsec-forensics` | Evidence collection |
| `nullsec-log` | Log management |
| `nullsec-keylog-detect` | Keylogger detection |

### 🟢 Privacy & Encryption

| Tool | Description |
|------|-------------|
| `nullsec-crypt` | File encryption (AES-256-GCM) |
| `nullsec-vault` | Encrypted secrets vault |
| `nullsec-privacy` | Privacy hardening |
| `nullsec-proxy` | Proxy chain management |
| `nullsec-tunnel` | SSH tunneling toolkit |
| `nullsec-shred` | Secure file deletion |
| `nullsec-hash` | Hashing utilities |

### 🟡 System & Utilities

| Tool | Description |
|------|-------------|
| `nullsec-backup` | Encrypted backups |
| `nullsec-container` | Container security |
| `nullsec-sandbox` | Sandboxed execution |
| `nullsec-fetch` | System info (neofetch-style) |
| `nullsec-update` | System updater |
| `nullsec-verify` | File integrity checker |
| `nullsec-watch` | File system watcher |
| `nullsec-recon` | Reconnaissance toolkit |

### 🎨 Theming & Customization

| Tool | Description |
|------|-------------|
| `nullsec-theme` | GTK theme manager |
| `nullsec-backgrounds` | Wallpaper generator |
| `nullsec-icons` | Icon theme manager |
| `nullsec-plymouth` | Boot splash manager |

---

## 🚀 Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools
chmod +x install.sh
./install.sh
```

### Manual Install

```bash
# Clone repository
git clone https://github.com/bad-antics/nullsec-tools.git

# Copy tools to your path
cp nullsec-tools/linux/* ~/.local/bin/

# Make executable
chmod +x ~/.local/bin/nullsec-*

# Verify installation
nullsec-fetch
```

### Dependencies

```bash
# Debian/Ubuntu
sudo apt install nmap netcat-openbsd curl jq openssl imagemagick \
    john hashcat socat proxychains4 tor

# Arch Linux
sudo pacman -S nmap gnu-netcat curl jq openssl imagemagick \
    john hashcat socat proxychains-ng tor
```

---

## 📖 Usage Examples

```bash
# Network scanning
nullsec-scan quick 192.168.1.0/24
nullsec-scan stealth 10.10.10.1

# Password cracking
nullsec-crack identify "5f4dcc3b5aa765d61d8327deb882cf99"
nullsec-crack john hashes.txt /path/to/wordlist.txt

# OSINT gathering
nullsec-osint domain example.com
nullsec-osint email user@example.com

# Enumeration
nullsec-enum smb 192.168.1.100
nullsec-enum http 192.168.1.100

# Encryption
nullsec-crypt encrypt secret.txt
nullsec-vault add api_key "sk-xxxx"

# System hardening
nullsec-harden firewall
nullsec-harden ssh
nullsec-audit full

# Tunneling
nullsec-tunnel socks 1080 user@proxy.host
nullsec-tunnel local 3306 db.internal 3306 user@jump.host
```

---

## 🏗️ Project Structure

```
nullsec-tools/
├── linux/              # Linux tools
│   ├── nullsec-scan
│   ├── nullsec-crack
│   ├── nullsec-payload
│   └── ... (50+ tools)
├── scripts/            # Helper scripts
├── LICENSE             # NullSec Public License
├── README.md           # This file
├── TOOLS.md            # Detailed tool docs
└── CHANGELOG.md        # Version history
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-tool`)
3. Commit your changes (`git commit -am 'Add new tool'`)
4. Push to the branch (`git push origin feature/new-tool`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **NullSec Public License v1.0** - see [LICENSE](LICENSE) for details.

**Key Points:**
- ✅ Free for authorized security testing
- ✅ Open source and modifiable
- ❌ No unauthorized/malicious use
- ❌ No liability for misuse

---

## 🔗 Links

- **GitHub:** [github.com/bad-antics](https://github.com/bad-antics)
- **NullSec Linux:** [github.com/bad-antics/nullsec-linux](https://github.com/bad-antics/nullsec-linux)
- **Documentation:** [github.com/bad-antics/nullsec-docs](https://github.com/bad-antics/nullsec-docs)

---

<div align="center">

**Developed with 💀 by [bad-antics](https://github.com/bad-antics)**

*NullSec Project © 2025 - Hack Ethically*

```
┌──────────────────────────────────────────┐
│  "Security is not a product, but a       │
│   process." - Bruce Schneier             │
└──────────────────────────────────────────┘
```

</div>

[![Twitter](https://img.shields.io/badge/Twitter-@AnonAntics-1DA1F2?style=flat&logo=twitter&logoColor=white)](https://twitter.com/AnonAntics)
[![Discord](https://img.shields.io/badge/Discord-killers-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/killers)
