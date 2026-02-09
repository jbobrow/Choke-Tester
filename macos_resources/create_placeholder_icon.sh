#!/bin/bash
# Create a placeholder icon for development
# This creates a simple colored square icon

set -e

ICONSET_DIR="AppIcon.iconset"
mkdir -p "$ICONSET_DIR"

# Create simple colored icons at each size
create_icon() {
    local size=$1
    local output=$2
    # Create a blue square with rounded corners
    sips -z $size $size /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns --out "$output" 2>/dev/null || {
        # Fallback: create solid color image
        python3 -c "
from PIL import Image
img = Image.new('RGB', ($size, $size), color='#2196F3')
img.save('$output')
        " 2>/dev/null || {
            echo "Note: Cannot create icon at size $size - install Pillow or run on macOS"
        }
    }
}

echo "Creating placeholder icon set..."

# Standard and retina sizes
create_icon 16 "$ICONSET_DIR/icon_16x16.png"
create_icon 32 "$ICONSET_DIR/icon_16x16@2x.png"
create_icon 32 "$ICONSET_DIR/icon_32x32.png"
create_icon 64 "$ICONSET_DIR/icon_32x32@2x.png"
create_icon 128 "$ICONSET_DIR/icon_128x128.png"
create_icon 256 "$ICONSET_DIR/icon_128x128@2x.png"
create_icon 256 "$ICONSET_DIR/icon_256x256.png"
create_icon 512 "$ICONSET_DIR/icon_256x256@2x.png"
create_icon 512 "$ICONSET_DIR/icon_512x512.png"
create_icon 1024 "$ICONSET_DIR/icon_512x512@2x.png"

# Convert to .icns (macOS only)
if command -v iconutil &> /dev/null; then
    echo "Converting to AppIcon.icns..."
    iconutil -c icns "$ICONSET_DIR" -o AppIcon.icns
    echo "✓ Created AppIcon.icns"
    rm -rf "$ICONSET_DIR"
else
    echo "⚠  iconutil not found. Run 'iconutil -c icns $ICONSET_DIR -o AppIcon.icns' on macOS"
fi
