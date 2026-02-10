# Building Native macOS App

This guide explains how to build **Choke Test Safety Check** as a native macOS application.

## Quick Start

### Prerequisites

- macOS 10.15 (Catalina) or later
- Python 3.9 or later
- Xcode Command Line Tools: `xcode-select --install`

### Build Steps

1. **Set up environment**
   ```bash
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements-macos.txt
   ```

2. **Build the app**
   ```bash
   ./build_macos.sh
   ```

3. **Create installer DMG** (optional)
   ```bash
   ./create_dmg.sh
   ```

The built app will be in `dist/Choke Test Safety Check.app`

## Detailed Guide

### Build Modes

#### Production Build
Full standalone application, optimized for distribution:
```bash
./build_macos.sh
```

#### Development Build
Faster build that links to source code (for testing):
```bash
./build_macos.sh --dev
```

#### Build and Test
Build and automatically launch the app:
```bash
./build_macos.sh --test
```

### Custom App Icon

The app uses `macos_resources/AppIcon.icns`. To customize:

1. Create a 1024x1024 PNG icon
2. Generate the .icns file:
   ```bash
   cd macos_resources
   python generate_icons.py your_icon.png
   ```

See `macos_resources/ICON_README.md` for details.

### DMG Installer

Create a distributable DMG installer:

```bash
./create_dmg.sh
```

#### Styled DMG (Recommended)

For a prettier installer with custom background:

```bash
# Install create-dmg
brew install create-dmg

# Create styled DMG
./create_dmg.sh --styled
```

### Code Signing

#### Ad-hoc Signing (Local Testing)

Automatically applied by build script. Good for local testing but not for distribution.

#### Developer ID Signing (Distribution)

To distribute outside the Mac App Store:

1. Join [Apple Developer Program](https://developer.apple.com/programs/)
2. Create a Developer ID Application certificate
3. The build script will auto-detect and use it

To manually sign:
```bash
codesign --deep --force --sign "Developer ID Application: Your Name" \
    "dist/Choke Test Safety Check.app"
```

#### Notarization (Required for Distribution)

For macOS 10.15+, apps must be notarized:

```bash
# Create app-specific password at appleid.apple.com
# Store in keychain
xcrun notarytool store-credentials "notarytool-profile" \
    --apple-id "your@email.com" \
    --team-id "YOUR_TEAM_ID"

# Notarize
xcrun notarytool submit "dist/ChokeTestSafetyCheck-macOS.dmg" \
    --keychain-profile "notarytool-profile" \
    --wait

# Staple ticket to DMG
xcrun stapler staple "dist/ChokeTestSafetyCheck-macOS.dmg"
```

## File Structure

```
Choke-Tester/
├── setup_macos.py          # py2app configuration
├── build_macos.sh          # Build automation script
├── create_dmg.sh           # DMG creation script
├── launch_macos.sh         # Quick launcher (dev mode)
├── requirements-macos.txt  # macOS build dependencies
├── BUILD_MACOS.md          # This file
└── macos_resources/        # macOS-specific resources
    ├── AppIcon.icns        # App icon
    ├── generate_icons.py   # Icon generation script
    └── ICON_README.md      # Icon creation guide
```

## Troubleshooting

### Build Fails with Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements-macos.txt
```

### App Won't Open - "Damaged" Error

This happens with unsigned apps. Right-click → Open, or:
```bash
xattr -cr "dist/Choke Test Safety Check.app"
open "dist/Choke Test Safety Check.app"
```

### Missing Icon

If AppIcon.icns doesn't exist:
```bash
cd macos_resources
bash create_placeholder_icon.sh
```

### Large App Size

The app includes Python and all dependencies. To reduce size:

1. Use `--optimize 2` (already enabled)
2. Exclude unused packages in `setup_macos.py`
3. Strip debug symbols (already enabled)

Typical size: 150-250 MB

### PySide6 Issues

If PySide6 causes problems:
```bash
pip uninstall PySide6
pip install PySide6>=6.5.0 --no-cache-dir
```

### File Associations Don't Work

File associations (.3mf, .stl) are configured in `setup_macos.py` under `CFBundleDocumentTypes`. They should work automatically after installation.

To test:
```bash
open -a "Choke Test Safety Check" test.3mf
```

## Development Workflow

### Quick Testing (No Build)

```bash
./launch_macos.sh
```

Or directly:
```bash
python3 run.py
```

### Development Build (Fast)

```bash
# First time
./build_macos.sh --dev

# App is now linked to source code
# Changes to Python files are immediately reflected
open "dist/Choke Test Safety Check.app"
```

### Production Build (Distribution)

```bash
# Full build with optimization
./build_macos.sh

# Create DMG
./create_dmg.sh --styled

# Result: dist/ChokeTestSafetyCheck-macOS.dmg
```

## Advanced Configuration

### Customizing the Build

Edit `setup_macos.py` to customize:

- **Bundle identifier**: `CFBundleIdentifier`
- **Version**: `CFBundleVersion`
- **Required macOS version**: `LSMinimumSystemVersion`
- **File associations**: `CFBundleDocumentTypes`
- **Included packages**: `packages` list
- **Excluded packages**: `excludes` list

### Adding Resources

To include additional files in the app bundle:

```python
# In setup_macos.py
DATA_FILES = [
    ('resources', ['path/to/resource.txt']),
]
```

### Custom Info.plist

The Info.plist is generated from the `plist` dict in `setup_macos.py`. Add custom keys there.

## Distribution Checklist

Before distributing your app:

- [ ] Custom app icon created
- [ ] Version number updated in `setup_macos.py`
- [ ] App tested on clean macOS installation
- [ ] Code signed with Developer ID
- [ ] App notarized (for macOS 10.15+)
- [ ] DMG created and tested
- [ ] DMG notarized and stapled
- [ ] Release notes prepared

## Performance Optimization

### Startup Time

The app should launch in 2-5 seconds. If slower:

1. Check for unnecessary imports in `run.py`
2. Lazy-load heavy modules
3. Use `--optimize 2` (already enabled)

### App Size

Reduce size by excluding unused packages:

```python
# In setup_macos.py
'excludes': [
    'tkinter',
    'test',
    'unittest',
    'distutils',
    'setuptools',
    # Add more unused packages
],
```

### Memory Usage

Monitor with Activity Monitor. Typical usage: 100-200 MB.

## Support

For issues:

1. Check this guide
2. Review `build_macos.sh` output for errors
3. Test with `--dev` mode first
4. Check py2app documentation: https://py2app.readthedocs.io/

## Resources

- [py2app Documentation](https://py2app.readthedocs.io/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [macOS Code Signing Guide](https://developer.apple.com/developer-id/)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
