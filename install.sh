#!/bin/bash
#
# GenSec Template Generator - Install Script
# Works on Linux and macOS
#

set -e

echo "========================================"
echo "  GenSec Lab Template Generator"
echo "  Installation Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python is not installed.${NC}"
        echo "Please install Python 3.10 or higher from https://www.python.org/"
        exit 1
    fi

    # Check version
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
        echo -e "${RED}Error: Python 3.10+ required (found $PYTHON_VERSION)${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Found Python $PYTHON_VERSION"
}

# Check for pip
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    elif command -v uv &> /dev/null; then
        PIP_CMD="uv pip"
        echo -e "${GREEN}✓${NC} Found uv"
        return
    else
        echo -e "${RED}Error: pip is not installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Found pip"
}

# Create virtual environment
create_venv() {
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}!${NC} Virtual environment already exists"
    else
        echo "Creating virtual environment..."
        if command -v uv &> /dev/null; then
            uv venv
        else
            $PYTHON_CMD -m venv .venv
        fi
        echo -e "${GREEN}✓${NC} Created virtual environment"
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo -e "${GREEN}✓${NC} Activated virtual environment"
    elif [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
        echo -e "${GREEN}✓${NC} Activated virtual environment"
    else
        echo -e "${RED}Error: Could not find virtual environment activation script${NC}"
        exit 1
    fi
}

# Install the package
install_package() {
    echo "Installing gensec-template..."
    if command -v uv &> /dev/null; then
        uv pip install .
    else
        pip install .
    fi
    echo -e "${GREEN}✓${NC} Installed gensec-template"
}

# Main installation
main() {
    echo "Checking requirements..."
    echo ""

    check_python
    check_pip

    echo ""
    echo "Setting up environment..."
    echo ""

    create_venv
    activate_venv
    install_package

    echo ""
    echo "========================================"
    echo -e "${GREEN}Installation complete!${NC}"
    echo "========================================"
    echo ""
    echo "To use gensec-template:"
    echo ""
    echo "  1. Activate the virtual environment:"
    echo "     source .venv/bin/activate"
    echo ""
    echo "  2. Run the tool:"
    echo "     gensec-template list"
    echo "     gensec-template generate 01.3"
    echo ""
    echo "For help:"
    echo "     gensec-template --help"
    echo ""
}

# Run main
main
