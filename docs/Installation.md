# 📦 Installation Guide

## System Requirements

### Minimum
- **OS**: Linux (Debian/Ubuntu, Arch, Fedora), macOS 12+, Windows 10/11
- **RAM**: 4GB
- **Disk**: 500MB free space
- **Python**: 3.9+

### Recommended
- **RAM**: 8GB+
- **CPU**: Multi-core for concurrent tools
- **Disk**: 2GB for full installation with wordlists

---

## Quick Install (Recommended)

### Using the Install Script

```bash
curl -sSL https://raw.githubusercontent.com/bad-antics/nullsec-tools/main/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools
./install.sh
```

---

## Manual Installation

### 1. Clone Repository

```bash
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools
```

### 2. Python Tools

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install as package
pip install -e .
```

### 3. Go Tools

```bash
# Ensure Go 1.21+ is installed
go version

# Build all Go tools
cd go
go mod download
go build -o ../bin/ ./...
```

### 4. Rust Tools

```bash
# Ensure Rust is installed
rustc --version

# Build all Rust tools
cd rust
cargo build --release
cp target/release/* ../bin/
```

### 5. C Tools

```bash
# Ensure build tools are installed
# Debian/Ubuntu: apt install build-essential libpcap-dev libssl-dev
# Arch: pacman -S base-devel libpcap openssl
# macOS: xcode-select --install && brew install libpcap openssl

cd c
make
cp bin/* ../bin/
```

---

## Platform-Specific Instructions

### Debian/Ubuntu

```bash
# Install dependencies
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-venv \
  golang-go \
  rustc cargo \
  build-essential \
  libpcap-dev libssl-dev libcurl4-openssl-dev \
  nmap masscan

# Clone and install
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools && ./install.sh
```

### Arch Linux

```bash
sudo pacman -S python python-pip go rust base-devel libpcap openssl nmap masscan
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools && ./install.sh
```

### Fedora/RHEL

```bash
sudo dnf install python3 python3-pip golang rust cargo gcc make libpcap-devel openssl-devel
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools && ./install.sh
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python go rust libpcap openssl nmap masscan

# Clone and install
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools && ./install.sh
```

### Windows (WSL2 Recommended)

```powershell
# Enable WSL2
wsl --install -d Ubuntu

# Then follow Ubuntu instructions inside WSL
```

---

## Docker Installation

```bash
# Pull the image
docker pull ghcr.io/bad-antics/nullsec-tools:latest

# Run interactively
docker run -it --rm ghcr.io/bad-antics/nullsec-tools

# Run specific tool
docker run --rm ghcr.io/bad-antics/nullsec-tools portscan -t 192.168.1.1
```

### Build from Dockerfile

```bash
git clone https://github.com/bad-antics/nullsec-tools.git
cd nullsec-tools
docker build -t nullsec-tools .
```

---

## NullSec Linux (Pre-installed)

All NullSec Tools come pre-installed on [NullSec Linux](https://github.com/bad-antics/nullsec-linux). Download the ISO and boot directly into a fully configured security environment.

---

## Verify Installation

```bash
# Check Python tools
nullsec --version
email_hunter --help

# Check Go tools  
portscan --version

# Check Rust tools
hashcrack --version

# Run test suite
cd nullsec-tools
python -m pytest tests/
```

---

## Updating

```bash
cd nullsec-tools
git pull
./install.sh --update
```

---

## Uninstalling

```bash
cd nullsec-tools
./install.sh --uninstall

# Or manually
pip uninstall nullsec-tools
rm -rf ~/nullsec-tools
```

---

## Troubleshooting

See [Troubleshooting](Troubleshooting) for common issues.

| Issue | Solution |
|-------|----------|
| `pip: command not found` | Install Python: `apt install python3-pip` |
| `go: command not found` | Install Go: `apt install golang-go` |
| `cargo: command not found` | Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| Permission denied | Run with `sudo` or fix file permissions |
| Missing libpcap | Install: `apt install libpcap-dev` |
