#!/bin/bash
#
# macOS DMG Creator
#
# Creates a distributable DMG file for the Choke Test Safety Check app.
#
# Usage:
#   ./create_dmg.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_NAME="Choke Test Safety Check"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
APP_PATH="$DIST_DIR/$APP_NAME.app"
DMG_NAME="ChokeTestSafetyCheck-macOS.dmg"
TEMP_DMG="$DIST_DIR/temp.dmg"
FINAL_DMG="$DIST_DIR/$DMG_NAME"
VOLUME_NAME="Choke Test Installer"

# Print colored message
print_msg() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_msg "$BLUE" "🔍 Checking prerequisites..."

    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_msg "$RED" "❌ Error: This script must be run on macOS"
        exit 1
    fi

    if [[ ! -d "$APP_PATH" ]]; then
        print_msg "$RED" "❌ Error: App not found at $APP_PATH"
        print_msg "$YELLOW" "   Run ./build_macos.sh first"
        exit 1
    fi

    print_msg "$GREEN" "✓ App found"
}

# Create DMG
create_dmg() {
    print_msg "$BLUE" "📦 Creating DMG installer..."

    # Remove old DMG if exists
    rm -f "$FINAL_DMG" "$TEMP_DMG"

    # Get app size
    APP_SIZE=$(du -sk "$APP_PATH" | cut -f1)
    DMG_SIZE=$((APP_SIZE / 1024 + 100))  # Add 100MB padding

    print_msg "$BLUE" "   Creating disk image (${DMG_SIZE}MB)..."

    # Create temporary DMG
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$VOLUME_NAME" "$TEMP_DMG" -ov -quiet

    # Mount the DMG
    print_msg "$BLUE" "   Mounting disk image..."
    MOUNT_POINT=$(hdiutil attach "$TEMP_DMG" -nobrowse -readwrite | grep "/Volumes/" | awk '{print $3}')

    if [[ -z "$MOUNT_POINT" ]]; then
        print_msg "$RED" "❌ Failed to mount DMG"
        exit 1
    fi

    print_msg "$BLUE" "   Copying application..."

    # Copy app to DMG
    cp -R "$APP_PATH" "$MOUNT_POINT/"

    # Create Applications symlink for easy installation
    ln -s /Applications "$MOUNT_POINT/Applications"

    # Create a README
    cat > "$MOUNT_POINT/README.txt" << EOF
Choke Test Safety Check
========================

Installation:
1. Drag "Choke Test Safety Check.app" to the Applications folder
2. Open from Applications or Spotlight

Usage:
• Open .3mf or .stl files directly in the app
• Drag and drop files onto the app window
• Batch process folders of 3D models

For help and documentation, visit:
https://github.com/yourusername/choke-tester

© 2025 Bambu Choke Check
EOF

    # Set background and icon positions (optional)
    # This requires additional tools like create-dmg or manual AppleScript

    print_msg "$BLUE" "   Finalizing..."

    # Sync and unmount
    sync
    hdiutil detach "$MOUNT_POINT" -quiet

    # Convert to compressed read-only DMG
    print_msg "$BLUE" "   Compressing..."
    hdiutil convert "$TEMP_DMG" -format UDZO -o "$FINAL_DMG" -ov -quiet

    # Clean up temp DMG
    rm -f "$TEMP_DMG"

    if [[ -f "$FINAL_DMG" ]]; then
        DMG_SIZE=$(du -h "$FINAL_DMG" | cut -f1)
        print_msg "$GREEN" "✓ DMG created successfully!"
        print_msg "$GREEN" "   Location: $FINAL_DMG"
        print_msg "$BLUE" "   Size: $DMG_SIZE"
    else
        print_msg "$RED" "❌ Failed to create DMG"
        exit 1
    fi
}

# Test DMG
test_dmg() {
    print_msg "$BLUE" "🧪 Testing DMG..."

    # Verify DMG
    if hdiutil verify "$FINAL_DMG" -quiet; then
        print_msg "$GREEN" "✓ DMG verification passed"
    else
        print_msg "$RED" "❌ DMG verification failed"
        exit 1
    fi

    # Optionally open the DMG
    print_msg "$YELLOW" "Opening DMG for inspection..."
    open "$FINAL_DMG"
}

# Enhanced DMG with styling (requires node/create-dmg or manual AppleScript)
create_styled_dmg() {
    if command -v create-dmg &> /dev/null; then
        print_msg "$BLUE" "📦 Creating styled DMG with create-dmg..."

        create-dmg \
            --volname "$VOLUME_NAME" \
            --volicon "macos_resources/AppIcon.icns" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --icon "$APP_NAME.app" 175 120 \
            --hide-extension "$APP_NAME.app" \
            --app-drop-link 425 120 \
            --no-internet-enable \
            "$FINAL_DMG" \
            "$APP_PATH"

        print_msg "$GREEN" "✓ Styled DMG created"
    else
        print_msg "$YELLOW" "⚠️  create-dmg not found, using basic DMG"
        print_msg "$YELLOW" "   Install with: brew install create-dmg"
        create_dmg
    fi
}

show_usage() {
    cat << EOF
Usage: ./create_dmg.sh [OPTIONS]

Create a distributable DMG installer for the Choke Test Safety Check app.

OPTIONS:
    --styled        Create a styled DMG (requires create-dmg)
    --test          Create DMG and open for inspection
    --help          Show this help message

EXAMPLES:
    ./create_dmg.sh                # Create basic DMG
    ./create_dmg.sh --styled       # Create styled DMG (prettier)
    ./create_dmg.sh --test         # Create and test DMG

NOTES:
    - Requires the app to be built first (run ./build_macos.sh)
    - For styled DMG: brew install create-dmg
    - Output: dist/ChokeTestSafetyCheck-macOS.dmg

EOF
}

# Main
main() {
    local use_styled=false
    local do_test=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --styled)
                use_styled=true
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
    print_msg "$GREEN" "  DMG Installer Creator"
    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    check_prerequisites

    if [[ "$use_styled" == true ]]; then
        create_styled_dmg
    else
        create_dmg
    fi

    if [[ "$do_test" == true ]]; then
        test_dmg
    fi

    echo
    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_msg "$GREEN" "  ✓ DMG Ready for Distribution!"
    print_msg "$GREEN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_msg "$BLUE" ""
    print_msg "$BLUE" "  DMG location: $FINAL_DMG"
    print_msg "$BLUE" ""
    print_msg "$BLUE" "  Users can now:"
    print_msg "$BLUE" "    1. Download the DMG"
    print_msg "$BLUE" "    2. Open it"
    print_msg "$BLUE" "    3. Drag the app to Applications"
    print_msg "$BLUE" ""
}

main "$@"
