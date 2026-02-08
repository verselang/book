#!/usr/bin/env bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Verse Documentation Setup & Build Script ===${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    "$1" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null
}

# Check for Python 3.8+
echo -e "${YELLOW}Checking Python installation...${NC}"
PYTHON_CMD=""

# Try different Python commands
for cmd in python3 python; do
    if command_exists "$cmd"; then
        VERSION=$(get_python_version "$cmd" || echo "0.0")
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)

        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]; then
            PYTHON_CMD="$cmd"
            echo -e "${GREEN}Found Python $VERSION at $cmd${NC}"
            break
        fi
    fi
done

# Install Python if not found or version too old
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}Python 3.8+ not found. Installing Python...${NC}"

    # Detect OS and install Python accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            echo "Installing Python via Homebrew..."
            brew install python@3.12
            PYTHON_CMD="python3"
        else
            echo -e "${RED}Homebrew not found. Please install Homebrew first:${NC}"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi

    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            echo "Installing Python via apt..."
            sudo apt-get update
            sudo apt-get install -y python3.12 python3-pip python3-venv
            PYTHON_CMD="python3"
        elif command_exists yum; then
            echo "Installing Python via yum..."
            sudo yum install -y python3 python3-pip
            PYTHON_CMD="python3"
        elif command_exists dnf; then
            echo "Installing Python via dnf..."
            sudo dnf install -y python3 python3-pip
            PYTHON_CMD="python3"
        else
            echo -e "${RED}Unable to install Python automatically. Please install Python 3.8+ manually.${NC}"
            exit 1
        fi

    else
        echo -e "${RED}Unsupported OS. Please install Python 3.8+ manually.${NC}"
        exit 1
    fi

    # Verify installation
    if ! command_exists "$PYTHON_CMD"; then
        echo -e "${RED}Python installation failed.${NC}"
        exit 1
    fi
fi

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists, using existing one..."
else
    if ! "$PYTHON_CMD" -m venv venv 2>/dev/null; then
        echo -e "${YELLOW}Virtual environment creation failed. Trying with --without-pip...${NC}"
        "$PYTHON_CMD" -m venv --without-pip venv
        source venv/bin/activate
        curl -sS https://bootstrap.pypa.io/get-pip.py | python
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install pip. Please install python3-venv package:${NC}"
            echo "  sudo apt install python3-venv"
            exit 1
        fi
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install required packages
echo -e "${YELLOW}Installing MkDocs and dependencies...${NC}"
pip install -r requirements.txt

# Install the custom Verse lexer
echo -e "${YELLOW}Installing custom Verse syntax highlighter...${NC}"

if [ -f "setup.py" ]; then
    pip install -e .
    echo -e "${GREEN}Custom Verse lexer installed${NC}"
else
    echo -e "${YELLOW}setup.py not found, skipping Verse lexer installation...${NC}"
fi

# Build the documentation
echo -e "${YELLOW}Building documentation site...${NC}"
mkdocs build --verbose

# Check if build was successful
if [ -d "site" ]; then
    echo -e "${GREEN}✓ Documentation built successfully!${NC}"
    echo -e "${GREEN}  Static site generated in: ./site/${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. To view the site locally:"
    echo "     source venv/bin/activate && mkdocs serve"
    echo "     Then open http://localhost:8000"
    echo ""
    echo "  2. To deploy the static site:"
    echo "     Copy the contents of ./site/ to your web server"
    echo ""
else
    echo -e "${RED}✗ Build failed. Please check the output above for errors.${NC}"
    exit 1
fi

echo -e "${GREEN}=== Setup Complete ===${NC}"