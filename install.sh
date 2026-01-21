#!/bin/bash
# ============================================================================
# NullSec Tools Installer
# ============================================================================
# by bad-antics development
# https://github.com/bad-antics/nullsec-tools
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

INSTALL_DIR="$HOME/.local/bin"
DATA_DIR="$HOME/.local/share/nullsec"
CONFIG_DIR="$HOME/.config/nullsec"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

info() { echo -e "${CYAN}[*]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

banner() {
    echo -e "${RED}"
    cat << 'BANNER'
    _   __      ____  _____              
   / | / /_  __/ / / / ___/___  _____    
  /  |/ / / / / / /  \__ \/ _ \/ ___/    
 / /|  / /_/ / / /  ___/ /  __/ /__      
/_/ |_/\__,_/_/_/  /____/\___/\___/      
                                          
  ████████╗ ██████╗  ██████╗ ██╗      ███████╗
  ╚══██╔══╝██╔═══██╗██╔═══██╗██║      ██╔════╝
     ██║   ██║   ██║██║   ██║██║      ███████╗
     ██║   ██║   ██║██║   ██║██║      ╚════██║
     ██║   ╚██████╔╝╚██████╔╝███████╗ ███████║
     ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝ ╚══════╝
BANNER
    echo -e "${NC}"
    echo -e "  ${WHITE}[ bad-antics development | Installer ]${NC}"
    echo ""
}

check_deps() {
    info "Checking dependencies..."
    
    local missing=()
    
    for cmd in bash curl jq openssl; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        warn "Missing core dependencies: ${missing[*]}"
        echo "  Install with: sudo apt install ${missing[*]}"
    else
        success "Core dependencies satisfied"
    fi
}

install_tools() {
    info "Installing NullSec tools..."
    
    mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$CONFIG_DIR"
    
    local count=0
    
    if [[ -d "$SCRIPT_DIR/linux" ]]; then
        for tool in "$SCRIPT_DIR"/linux/nullsec-*; do
            if [[ -f "$tool" ]]; then
                cp "$tool" "$INSTALL_DIR/"
                chmod +x "$INSTALL_DIR/$(basename "$tool")"
                ((count++))
            fi
        done
    fi
    
    success "Installed $count tools to $INSTALL_DIR"
}

setup_path() {
    local shell_rc=""
    
    if [[ -f "$HOME/.zshrc" ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        shell_rc="$HOME/.bashrc"
    fi
    
    if [[ -n "$shell_rc" ]]; then
        if ! grep -q "$INSTALL_DIR" "$shell_rc" 2>/dev/null; then
            echo "" >> "$shell_rc"
            echo "# NullSec Tools" >> "$shell_rc"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$shell_rc"
            success "Added $INSTALL_DIR to PATH in $shell_rc"
        else
            info "PATH already configured"
        fi
    fi
}

verify_install() {
    info "Verifying installation..."
    
    local tools
    tools=$(ls "$INSTALL_DIR"/nullsec-* 2>/dev/null | wc -l)
    
    if [[ $tools -gt 0 ]]; then
        success "Installation complete!"
        echo ""
        echo -e "  ${WHITE}Tools installed:${NC} $tools"
        echo -e "  ${WHITE}Location:${NC} $INSTALL_DIR"
        echo -e "  ${WHITE}Data:${NC} $DATA_DIR"
        echo ""
        echo -e "  ${CYAN}Reload your shell or run:${NC}"
        echo "    source ~/.bashrc"
        echo ""
        echo -e "  ${CYAN}Verify with:${NC}"
        echo "    nullsec-fetch"
    else
        error "Installation may have failed"
    fi
}

uninstall() {
    warn "Uninstalling NullSec tools..."
    
    rm -f "$INSTALL_DIR"/nullsec-*
    
    read -p "Remove data directories? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$DATA_DIR" "$CONFIG_DIR"
        success "Data directories removed"
    fi
    
    success "NullSec tools uninstalled"
}

show_help() {
    banner
    cat << 'HELP'
USAGE:
    ./install.sh [options]

OPTIONS:
    --install     Install tools (default)
    --update      Update existing installation
    --uninstall   Remove NullSec tools
    --help        Show this help

EXAMPLES:
    ./install.sh
    ./install.sh --update
    ./install.sh --uninstall

HELP
}

main() {
    banner
    
    case "$1" in
        --uninstall|-u)
            uninstall
            ;;
        --help|-h)
            show_help
            ;;
        *)
            check_deps
            install_tools
            setup_path
            verify_install
            ;;
    esac
}

main "$@"
