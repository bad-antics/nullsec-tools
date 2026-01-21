# 📥 NullSec Tools Installation Guide

<div align="center">

**by bad-antics development**

</div>

---

## System Requirements

### Minimum
- **OS:** Linux (Debian/Ubuntu, Arch, Fedora, or compatible)
- **Shell:** Bash 4.0+
- **Memory:** 512MB RAM
- **Storage:** 100MB free space

### Recommended
- **OS:** NullSec Linux, Kali Linux, Parrot OS, or Debian 12+
- **Shell:** Bash 5.0+ or Zsh
- **Memory:** 2GB+ RAM
- **Storage:** 1GB+ free space (for wordlists)

---

## Quick Installation

### One-Line Install

```bash
curl -sL https://raw.githubusercontent.com/bad-antics/nullsec-tools/main/install.sh | bash
```

### Git Clone Install

```bash
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools
./install.sh
```

---

## Manual Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools
```

### Step 2: Create Directory

```bash
mkdir -p ~/.local/bin
```

### Step 3: Copy Tools

```bash
cp linux/nullsec-* ~/.local/bin/
```

### Step 4: Set Permissions

```bash
chmod +x ~/.local/bin/nullsec-*
```

### Step 5: Add to PATH

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload:

```bash
source ~/.bashrc
```

### Step 6: Verify Installation

```bash
nullsec-fetch
```

---

## Dependencies

### Core Dependencies

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y \
    bash \
    coreutils \
    curl \
    wget \
    jq \
    openssl \
    gnupg

# Arch Linux
sudo pacman -S --noconfirm \
    bash \
    coreutils \
    curl \
    wget \
    jq \
    openssl \
    gnupg
```

### Network Tools

```bash
# Debian/Ubuntu
sudo apt install -y \
    nmap \
    netcat-openbsd \
    socat \
    proxychains4 \
    tor \
    whois \
    dnsutils

# Arch Linux
sudo pacman -S --noconfirm \
    nmap \
    gnu-netcat \
    socat \
    proxychains-ng \
    tor \
    whois \
    bind
```

### Security Tools

```bash
# Debian/Ubuntu
sudo apt install -y \
    john \
    hashcat \
    hydra \
    aircrack-ng \
    wordlists

# Arch Linux (AUR required for some)
sudo pacman -S --noconfirm \
    john \
    hashcat \
    hydra \
    aircrack-ng
```

### Graphics/Theming

```bash
# Debian/Ubuntu
sudo apt install -y \
    imagemagick \
    inkscape \
    gtk2-engines-murrine

# Arch Linux
sudo pacman -S --noconfirm \
    imagemagick \
    inkscape \
    gtk-engine-murrine
```

---

## Optional: Install All Dependencies

```bash
# Debian/Ubuntu - Full install
sudo apt install -y nmap netcat-openbsd curl wget jq openssl \
    gnupg socat proxychains4 tor whois dnsutils john hashcat \
    hydra imagemagick python3 python3-pip ruby golang

# Install Python tools
pip3 install impacket requests beautifulsoup4
```

---

## Updating

### Using Git

```bash
cd ~/nullsec-tools
git pull origin main
./install.sh --update
```

### Using nullsec-update

```bash
nullsec-update tools
```

---

## Uninstallation

```bash
# Remove tools
rm -f ~/.local/bin/nullsec-*

# Remove data directories (optional)
rm -rf ~/.local/share/nullsec
rm -rf ~/.config/nullsec
```

---

## Troubleshooting

### "Command not found"

Ensure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permission Denied

Make tools executable:

```bash
chmod +x ~/.local/bin/nullsec-*
```

### Missing Dependencies

Check which tools need dependencies:

```bash
nullsec-verify deps
```

---

## Platform-Specific Notes

### NullSec Linux

All tools pre-installed. Just update:

```bash
nullsec-update
```

### Kali Linux

Most dependencies already available:

```bash
sudo apt install -y jq imagemagick
```

### WSL (Windows Subsystem for Linux)

Works with limitations:
- Network tools may require elevated privileges
- Some hardware features unavailable

### macOS (Experimental)

Some tools work with Homebrew:

```bash
brew install bash coreutils nmap jq openssl
```

---

## Getting Help

```bash
# Tool-specific help
nullsec-<tool> --help

# List all tools
ls ~/.local/bin/nullsec-*

# View documentation
cat ~/nullsec-tools/TOOLS.md
```

---

## Support

- **Issues:** [GitHub Issues](https://github.com/bad-antics/nullsec-tools/issues)
- **Docs:** [nullsec-docs](https://github.com/bad-antics/nullsec-docs)

---

<div align="center">

**bad-antics development** | NullSec Project © 2025

</div>
