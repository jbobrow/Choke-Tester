#!/bin/bash
#
# macOS Native App Build Script
#
# This script builds a native macOS application bundle for Choke Test Safety Check.
#
# Usage:
#   ./build_macos.sh              # Build production app
#   ./build_macos.sh --dev        # Build in alias mode (development)
#   ./build_macos.sh --clean      # Clean build artifacts
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

APP_NAME="Choke Test Safety Check"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"

# Print colored message
print_msg() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Clean build artifacts
clean_build() {
    print_msg "$YELLOW" "🧹 Cleaning build artifacts..."
    rm -rf "$DIST_DIR" "$BUILD_DIR"
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    print_msg "$GREEN" "✓ Clean complete"
}

# Check prerequisites
check_prerequisites() {
    print_msg "$BLUE" "🔍 Checking prerequisites..."

    # Check if on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_msg "$RED" "❌ Error: This script must be run on macOS"
        exit 1
    fi

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_msg "$RED" "❌ Error: python3 not found"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_msg "$GREEN" "✓ Python $PYTHON_VERSION"

    # Check if virtual environment is activated (recommended)
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_msg "$YELLOW" "⚠️  Warning: No virtual environment detected"
        print_msg "$YELLOW" "   Consider using: python3 -m venv venv && source venv/bin/activate"
    else
        print_msg "$GREEN" "✓ Virtual environment: $VIRTUAL_ENV"
    fi

    # Check if py2app is installed
    if ! python3 -c "import py2app" 2>/dev/null; then
        print_msg "$YELLOW" "⚠️  py2app not found. Installing..."
        pip install py2app
    else
        print_msg "$GREEN" "✓ py2app installed"
    fi

    # Check if icon exists, create if not
    if [[ ! -f "macos_resources/AppIcon.icns" ]]; then
        print_msg "$YELLOW" "⚠️  AppIcon.icns not found"
        print_msg "$YELLOW" "   The app will use a default system icon"
        print_msg "$YELLOW" "   To create a custom icon, see macos_resources/ICON_README.md"

        # Try to create a placeholder
        if [[ -f "macos_resources/create_placeholder_icon.sh" ]]; then
            print_msg "$BLUE" "   Attempting to create placeholder icon..."
            (cd macos_resources && bash create_placeholder_icon.sh) || true
        fi
    else
        print_msg "$GREEN" "✓ AppIcon.icns found"
    fi
}

# Install dependencies
install_dependencies() {
    print_msg "$BLUE" "📦 Installing dependencies..."

    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_msg "$GREEN" "✓ Dependencies installed"
    else
        print_msg "$YELLOW" "⚠️  requirements.txt not found"
    fi

    # Install py2app if not already installed
    pip install py2app
}

# Build the app
build_app() {
    local mode=$1

    print_msg "$BLUE" "🔨 Building macOS application..."

    # Clean previous builds
    rm -rf "$DIST_DIR" "$BUILD_DIR"

    if [[ "$mode" == "dev" ]]; then
        print_msg "$YELLOW" "Building in ALIAS mode (development)..."
        python3 setup_macos.py py2app -A
    else
        print_msg "$BLUE" "Building in PRODUCTION mode..."
        python3 setup_macos.py py2app
    fi

    if [[ -d "$DIST_DIR/$APP_NAME.app" ]]; then
        print_msg "$GREEN" "✓ Build successful!"
        print_msg "$GREEN" "   App location: $DIST_DIR/$APP_NAME.app"

        # Show app size
        APP_SIZE=$(du -sh "$DIST_DIR/$APP_NAME.app" | cut -f1)
        print_msg "$BLUE" "   App size: $APP_SIZE"
    else
        print_msg "$RED" "❌ Build failed"
        exit 1
    fi
}

# Test the app
test_app() {
    print_msg "$BLUE" "🧪 Testing application..."

    if [[ ! -d "$DIST_DIR/$APP_NAME.app" ]]; then
        print_msg "$RED" "❌ App not found. Build first."
        exit 1
    fi

    print_msg "$YELLOW" "Opening application..."
    open "$DIST_DIR/$APP_NAME.app"

    print_msg "$GREEN" "✓ App launched"
    print_msg "$YELLOW" "   Please verify the app works correctly"
}

# Sign the app (optional)
sign_app() {
    print_msg "$BLUE" "✍️  Code signing..."

    # Check if a signing identity is available
    if security find-identity -v -p codesigning | grep -q "Developer ID Application"; then
        IDENTITY=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | awk '{print $2}')
        print_msg "$BLUE" "   Found signing identity: $IDENTITY"

        codesign --force --deep --sign "$IDENTITY" "$DIST_DIR/$APP_NAME.app"
        print_msg "$GREEN" "✓ App signed"
    else
        print_msg "$YELLOW" "⚠️  No code signing identity found"
        print_msg "$YELLOW" "   App will be unsigned (use --adhoc for testing)"
        print_msg "$YELLOW" "   To distribute, you'll need an Apple Developer account"

        # Ad-hoc signing for local testing
        codesign --force --deep --sign - "$DIST_DIR/$APP_NAME.app"
        print_msg "$BLUE" "   Applied ad-hoc signature (for testing only)"
    fi
}

# Show usage
show_usage() {
    cat << EOF
Usage: ./build_macos.sh [OPTIONS]

Build a native macOS application for Choke Test Safety Check.

OPTIONS:
    --clean         Clean build artifacts and exit
    --dev           Build in alias mode (for development)
    --no-sign       Skip code signing
    --test          Build and test the app
    --help          Show this help message

EXAMPLES:
    ./build_macos.sh                # Full production build
    ./build_macos.sh --dev          # Development build (faster, links to source)
    ./build_macos.sh --clean        # Clean build artifacts
    ./build_macos.sh --test         # Build and launch app for testing

NOTES:
    - Requires macOS to build
    - Recommend using a virtual environment
    - See macos_resources/ICON_README.md to customize the app icon
    - Built app will be in: dist/Choke Test Safety Check.app

EOF
}

# Main script
main() {
    local mode="production"
    local do_sign=true
    local do_test=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                clean_build
                exit 0
                ;;
            --dev)
                mode="dev"
                shift
                ;;
            --no-sign)
                do_sign=false
                shift
                ;;
            --test)
                do_test=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_msg "$RED" "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_msg "$GREEN" "  Choke Test Safety Check - macOS Build"
    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    check_prerequisites
    install_dependencies
    build_app "$mode"

    if [[ "$do_sign" == true && "$mode" != "dev" ]]; then
        sign_app
    fi

    if [[ "$do_test" == true ]]; then
        test_app
    fi

    echo
    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_msg "$GREEN" "  ✓ Build Complete!"
    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_msg "$BLUE" ""
    print_msg "$BLUE" "  App location: $DIST_DIR/$APP_NAME.app"
    print_msg "$BLUE" ""
    print_msg "$BLUE" "  Next steps:"
    print_msg "$BLUE" "    • Test:  open '$DIST_DIR/$APP_NAME.app'"
    print_msg "$BLUE" "    • Package: ./create_dmg.sh"
    print_msg "$BLUE" ""
}

main "$@"
