# 📚 NullSec Tools Reference

<div align="center">

**Complete Tool Documentation**

by **bad-antics development**

[![GitHub](https://img.shields.io/badge/GitHub-bad--antics-black?logo=github)](https://github.com/bad-antics)

</div>

---

## 🔴 Red Team / Penetration Testing Tools

### nullsec-scan
**Network Scanner & Port Discovery**

```bash
nullsec-scan quick <target>       # Fast scan
nullsec-scan full <target>        # Comprehensive scan
nullsec-scan stealth <target>     # Slow, stealthy scan
nullsec-scan vuln <target>        # Vulnerability scan
```

**Keywords:** nmap wrapper, port scanner, network reconnaissance, penetration testing, red team, ethical hacking

---

### nullsec-crack
**Password Cracking Wrapper**

```bash
nullsec-crack identify <hash>     # Identify hash type
nullsec-crack john <file> [wl]    # Crack with John
nullsec-crack hashcat <file> <m>  # Crack with Hashcat
nullsec-crack zip <file>          # Crack ZIP password
nullsec-crack ssh <keyfile>       # Crack SSH passphrase
```

**Keywords:** password cracker, john the ripper, hashcat, hash identification, brute force, dictionary attack

---

### nullsec-payload
**Payload Generation & Encoding**

```bash
nullsec-payload reverse bash <ip> <port>
nullsec-payload reverse python <ip> <port>
nullsec-payload reverse powershell <ip> <port>
nullsec-payload webshell php
nullsec-payload encode base64 <payload>
```

**Keywords:** reverse shell, payload generator, msfvenom alternative, web shell, pentesting payloads

---

### nullsec-enum
**Service Enumeration Toolkit**

```bash
nullsec-enum smb <target>         # SMB enumeration
nullsec-enum http <target>        # HTTP enumeration
nullsec-enum ssh <target>         # SSH enumeration
nullsec-enum dns <target>         # DNS enumeration
nullsec-enum ldap <target>        # LDAP enumeration
```

**Keywords:** service enumeration, smb enum, ldap enum, active directory, network enumeration

---

### nullsec-osint
**Open Source Intelligence**

```bash
nullsec-osint domain <domain>     # Domain recon
nullsec-osint email <email>       # Email lookup
nullsec-osint username <user>     # Username search
nullsec-osint ip <address>        # IP investigation
nullsec-osint dorks <domain>      # Google dorks
```

**Keywords:** OSINT, reconnaissance, information gathering, social engineering, domain lookup, shodan

---

### nullsec-c2
**Command & Control Wrapper**

```bash
nullsec-c2 http <port>            # HTTP server
nullsec-c2 https <port>           # HTTPS server
nullsec-c2 beacon bash <ip> <p>   # Generate beacon
nullsec-c2 handler <port>         # Multi-handler
nullsec-c2 smb <dir>              # SMB server
```

**Keywords:** C2 framework, command and control, red team infrastructure, beacon, implant

---

### nullsec-spoof
**Identity & Traffic Spoofing**

```bash
nullsec-spoof mac random          # Random MAC
nullsec-spoof mac <vendor>        # Vendor MAC
nullsec-spoof hostname <name>     # Change hostname
nullsec-spoof dns <ip> <domain>   # DNS spoofing
nullsec-spoof full                # Full identity change
```

**Keywords:** MAC spoofing, identity spoofing, anonymity, traffic manipulation, MITM

---

### nullsec-portknock
**Port Knocking Client/Server**

```bash
nullsec-portknock knock <ip> <seq>
nullsec-portknock server <seq> <cmd>
nullsec-portknock save <name> <seq>
```

**Keywords:** port knocking, firewall bypass, covert channel, steganography, security

---

### nullsec-honeypot
**Lightweight Honeypot System**

```bash
nullsec-honeypot ssh <port>       # Fake SSH
nullsec-honeypot http <port>      # Fake HTTP
nullsec-honeypot ftp <port>       # Fake FTP
nullsec-honeypot multi            # Multiple services
```

**Keywords:** honeypot, intrusion detection, deception technology, threat intelligence, blue team

---

### nullsec-wordlist
**Wordlist Generation**

```bash
nullsec-wordlist generate <base>
nullsec-wordlist cewl <url>
nullsec-wordlist usernames <name>
nullsec-wordlist mangle <file>
```

**Keywords:** wordlist generator, password list, dictionary, brute force, custom wordlist

---

### nullsec-evade
**Anti-Detection Toolkit**

```bash
nullsec-evade history             # Clear history
nullsec-evade timestomp <file>    # Modify timestamps
nullsec-evade detect              # Check for AV/EDR
nullsec-evade hide <file>         # Hide file
```

**Keywords:** evasion, anti-forensics, EDR bypass, AV evasion, red team

---

## 🔵 Blue Team / Defensive Tools

### nullsec-harden
**System Hardening**

```bash
nullsec-harden firewall           # Configure firewall
nullsec-harden ssh                # Secure SSH
nullsec-harden kernel             # Kernel hardening
nullsec-harden audit              # Enable auditing
```

**Keywords:** system hardening, security configuration, CIS benchmark, compliance, hardening guide

---

### nullsec-audit
**Security Audit Framework**

```bash
nullsec-audit full                # Complete audit
nullsec-audit network             # Network audit
nullsec-audit users               # User audit
nullsec-audit permissions         # Permission audit
```

**Keywords:** security audit, vulnerability assessment, compliance check, security scanner

---

### nullsec-dfir
**Digital Forensics & Incident Response**

```bash
nullsec-dfir acquire <device>     # Disk acquisition
nullsec-dfir memory               # Memory dump
nullsec-dfir volatile             # Volatile data
nullsec-dfir timeline <path>      # File timeline
```

**Keywords:** DFIR, digital forensics, incident response, memory forensics, disk forensics

---

### nullsec-monitor
**System Monitoring**

```bash
nullsec-monitor processes
nullsec-monitor network
nullsec-monitor files <path>
nullsec-monitor resources
```

**Keywords:** system monitor, process monitor, security monitoring, SIEM, logging

---

### nullsec-netwatch
**Network Traffic Analyzer**

```bash
nullsec-netwatch live
nullsec-netwatch capture <file>
nullsec-netwatch analyze <pcap>
```

**Keywords:** network monitor, packet capture, traffic analysis, wireshark alternative, IDS

---

## 🟢 Privacy & Encryption Tools

### nullsec-crypt
**File Encryption (AES-256-GCM)**

```bash
nullsec-crypt encrypt <file>
nullsec-crypt decrypt <file>
nullsec-crypt shred <file>
```

**Keywords:** file encryption, AES-256, secure encryption, privacy tool, cryptography

---

### nullsec-vault
**Encrypted Secrets Vault**

```bash
nullsec-vault add <key> <value>
nullsec-vault get <key>
nullsec-vault list
nullsec-vault export
```

**Keywords:** password manager, secrets vault, credential storage, secure vault, encryption

---

### nullsec-tunnel
**SSH Tunneling Toolkit**

```bash
nullsec-tunnel local <lp> <rh> <rp> <ssh>
nullsec-tunnel remote <rp> <lh> <lp> <ssh>
nullsec-tunnel socks <port> <ssh>
nullsec-tunnel jump <lp> <jump> <target> <tp>
```

**Keywords:** SSH tunnel, port forwarding, SOCKS proxy, pivoting, lateral movement

---

### nullsec-proxy
**Proxy Chain Management**

```bash
nullsec-proxy tor
nullsec-proxy chain <proxies>
nullsec-proxy test
```

**Keywords:** proxy chain, Tor, anonymity, VPN alternative, privacy

---

## 🟡 System Utilities

### nullsec-backup
**Encrypted Backup System**

```bash
nullsec-backup create <source> <dest>
nullsec-backup restore <backup>
nullsec-backup verify <backup>
```

**Keywords:** encrypted backup, secure backup, rsync alternative, backup tool

---

### nullsec-sandbox
**Sandboxed Execution**

```bash
nullsec-sandbox run <command>
nullsec-sandbox analyze <file>
```

**Keywords:** sandbox, malware analysis, isolated execution, security sandbox

---

### nullsec-fetch
**System Information Display**

```bash
nullsec-fetch
nullsec-fetch --minimal
nullsec-fetch --json
```

**Keywords:** neofetch alternative, system info, Linux fetch, terminal art

---

## 🎨 Theming Tools

### nullsec-theme
**GTK Theme Manager**

```bash
nullsec-theme list
nullsec-theme apply <name>
nullsec-theme create <name>
```

**Keywords:** GTK theme, Linux customization, dark theme, hacker theme

---

### nullsec-backgrounds
**Wallpaper Generator**

```bash
nullsec-backgrounds generate <style>
nullsec-backgrounds list
```

**Keywords:** wallpaper generator, procedural backgrounds, Linux wallpaper, hacker wallpaper

---

<div align="center">

## 🔗 Links

- **GitHub:** [github.com/bad-antics](https://github.com/bad-antics)
- **Tools:** [nullsec-tools](https://github.com/bad-antics/nullsec-tools)
- **Linux:** [nullsec-linux](https://github.com/bad-antics/nullsec-linux)
- **Docs:** [nullsec-docs](https://github.com/bad-antics/nullsec-docs)

---

**Developed by [bad-antics](https://github.com/bad-antics)**

*NullSec Project © 2025 - Hack Ethically*

</div>
