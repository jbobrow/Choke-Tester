#!/usr/bin/env python3
"""
Generate macOS .icns icon from a source PNG image.

Usage:
    python generate_icons.py icon_source.png

Requirements:
    - Source image should be at least 1024x1024 PNG
    - Requires 'iconutil' (built into macOS)
    - Or use: pip install pillow

This script creates all required icon sizes for a macOS app icon.
"""

import sys
import os
import subprocess
from pathlib import Path

def generate_iconset_with_sips(source_image: str):
    """
    Generate .iconset using macOS built-in 'sips' tool.
    This only works on macOS.
    """
    source = Path(source_image)
    if not source.exists():
        print(f"Error: {source_image} not found")
        sys.exit(1)

    iconset_dir = source.parent / "AppIcon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Icon sizes required for macOS
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    print(f"Generating icon set from {source.name}...")

    for size in sizes:
        # Standard resolution
        output = iconset_dir / f"icon_{size}x{size}.png"
        subprocess.run([
            'sips', '-z', str(size), str(size),
            str(source), '--out', str(output)
        ], check=True, capture_output=True)
        print(f"  ✓ {size}x{size}")

        # Retina resolution (@2x)
        if size <= 512:
            output_2x = iconset_dir / f"icon_{size}x{size}@2x.png"
            subprocess.run([
                'sips', '-z', str(size * 2), str(size * 2),
                str(source), '--out', str(output_2x)
            ], check=True, capture_output=True)
            print(f"  ✓ {size}x{size}@2x")

    # Convert to .icns
    icns_path = source.parent / "AppIcon.icns"
    print(f"\nConverting to {icns_path.name}...")
    subprocess.run([
        'iconutil', '-c', 'icns', str(iconset_dir),
        '-o', str(icns_path)
    ], check=True)

    print(f"✓ Created {icns_path}")
    print(f"\nYou can now delete the {iconset_dir.name} directory if desired.")


def generate_iconset_with_pillow(source_image: str):
    """
    Generate .iconset using Pillow (works cross-platform).
    Note: Still requires iconutil on macOS to create .icns
    """
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow not installed. Install with: pip install pillow")
        sys.exit(1)

    source = Path(source_image)
    if not source.exists():
        print(f"Error: {source_image} not found")
        sys.exit(1)

    iconset_dir = source.parent / "AppIcon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    img = Image.open(source)

    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')

    sizes = [16, 32, 64, 128, 256, 512, 1024]

    print(f"Generating icon set from {source.name}...")

    for size in sizes:
        # Standard resolution
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        output = iconset_dir / f"icon_{size}x{size}.png"
        resized.save(output)
        print(f"  ✓ {size}x{size}")

        # Retina resolution (@2x)
        if size <= 512:
            resized_2x = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
            output_2x = iconset_dir / f"icon_{size}x{size}@2x.png"
            resized_2x.save(output_2x)
            print(f"  ✓ {size}x{size}@2x")

    print(f"\n✓ Created {iconset_dir.name}/")

    # Try to convert to .icns if on macOS
    try:
        icns_path = source.parent / "AppIcon.icns"
        print(f"Converting to {icns_path.name}...")
        subprocess.run([
            'iconutil', '-c', 'icns', str(iconset_dir),
            '-o', str(icns_path)
        ], check=True)
        print(f"✓ Created {icns_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠  iconutil not found. To complete icon generation:")
        print(f"   Run this on macOS: iconutil -c icns {iconset_dir} -o AppIcon.icns")


def create_default_icon():
    """Create a simple default icon using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not available, skipping default icon creation")
        return

    # Create a simple 1024x1024 icon
    size = 1024
    img = Image.new('RGB', (size, size), color='#2196F3')
    draw = ImageDraw.Draw(img)

    # Draw a safety warning symbol
    margin = size // 6
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill='#FFC107', outline='#FF6F00', width=20)

    # Draw an exclamation mark
    center_x = size // 2
    draw.rectangle([center_x - 40, size // 3, center_x + 40, size // 2 + 50],
                   fill='#212121')
    draw.ellipse([center_x - 40, size // 2 + 100, center_x + 40, size // 2 + 180],
                 fill='#212121')

    output_path = Path(__file__).parent / "icon_source.png"
    img.save(output_path)
    print(f"Created default icon: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No source image provided. Creating default icon...")
        source = create_default_icon()
        if source:
            generate_iconset_with_pillow(source)
    else:
        source_image = sys.argv[1]

        # Try macOS native tools first
        if sys.platform == 'darwin':
            try:
                generate_iconset_with_sips(source_image)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("sips/iconutil not available, trying Pillow...")
                generate_iconset_with_pillow(source_image)
        else:
            generate_iconset_with_pillow(source_image)
