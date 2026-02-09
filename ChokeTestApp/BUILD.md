# Building Choke Test Safety Check - Native Swift App

Complete guide for building the native macOS application from source.

## Prerequisites

### Required

- **macOS 13.0 (Ventura) or later**
- **Xcode 15.0 or later**
  - Install from Mac App Store or [developer.apple.com](https://developer.apple.com/xcode/)

### Optional

- **Command Line Tools:**
  ```bash
  xcode-select --install
  ```

- **Make** (usually pre-installed)

## Quick Build

### Option 1: Xcode GUI

1. Open the project:
   ```bash
   open ChokeTestApp.xcodeproj
   ```

2. Select scheme: **ChokeTestApp**

3. Build: `⌘B`

4. Run: `⌘R`

### Option 2: Command Line

```bash
# Build release version
make build

# Build and run
make run

# Install to /Applications
make install
```

## Build Configurations

### Debug Build

Fast incremental builds for development:

```bash
make debug
# Or
xcodebuild -project ChokeTestApp.xcodeproj \
    -scheme ChokeTestApp \
    -configuration Debug \
    build
```

**Output:** `build/Debug/Choke Test Safety Check.app`

### Release Build

Optimized for distribution:

```bash
make build
# Or
xcodebuild -project ChokeTestApp.xcodeproj \
    -scheme ChokeTestApp \
    -configuration Release \
    build
```

**Output:** `build/Release/Choke Test Safety Check.app`

**Optimizations:**
- Compiler optimizations enabled (-O)
- Dead code stripping
- Size optimizations
- No debug symbols

## Project Structure

```
ChokeTestApp/
├── ChokeTestApp.xcodeproj/    # Xcode project file
├── ChokeTestApp/
│   ├── ChokeTestApp.swift     # App entry point
│   ├── Models/                # Data models
│   ├── Views/                 # SwiftUI views
│   ├── Services/              # Business logic
│   ├── Resources/             # Assets, icons
│   ├── Info.plist             # App metadata
│   └── *.entitlements         # App capabilities
├── Makefile                   # Build automation
├── README.md                  # Documentation
└── BUILD.md                   # This file
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/choke-tester.git
cd choke-tester/ChokeTestApp

# Open in Xcode
open ChokeTestApp.xcodeproj
```

### 2. Development Cycle

```bash
# Make changes to Swift files
# Build and run for testing
make run

# Check app size
make size
```

### 3. Testing

```bash
# Run tests
make test

# Or in Xcode: ⌘U
```

## Distribution

### Creating a Distributable Build

#### Step 1: Archive

```bash
make archive
```

This creates `build/ChokeTestApp.xcarchive`

#### Step 2: Export

Create `ExportOptions.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>developer-id</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
</dict>
</plist>
```

Export the archive:

```bash
xcodebuild -exportArchive \
    -archivePath build/ChokeTestApp.xcarchive \
    -exportPath build/Export \
    -exportOptionsPlist ExportOptions.plist
```

### Code Signing

#### For Local Development

Xcode will automatically sign with your Apple ID:

1. Open Xcode
2. Select project in navigator
3. Select "ChokeTestApp" target
4. Go to "Signing & Capabilities"
5. Select your team

#### For Distribution

You'll need:

1. **Apple Developer Program** membership ($99/year)
2. **Developer ID Application** certificate
3. **Notarization** (required for macOS 10.15+)

##### Getting a Certificate

1. Go to [developer.apple.com](https://developer.apple.com)
2. Account → Certificates
3. Create **Developer ID Application** certificate
4. Download and install in Keychain

##### Signing the App

```bash
codesign --deep --force --sign "Developer ID Application: Your Name (TEAM_ID)" \
    "build/Release/Choke Test Safety Check.app"
```

##### Verify Signature

```bash
codesign --verify --verbose "build/Release/Choke Test Safety Check.app"
spctl --assess --verbose "build/Release/Choke Test Safety Check.app"
```

### Notarization

Required for distribution outside the Mac App Store:

#### Step 1: Create App-Specific Password

1. Go to [appleid.apple.com](https://appleid.apple.com)
2. Sign in
3. Generate app-specific password

#### Step 2: Store Credentials

```bash
xcrun notarytool store-credentials "notarytool-profile" \
    --apple-id "your@email.com" \
    --team-id "YOUR_TEAM_ID" \
    --password "app-specific-password"
```

#### Step 3: Notarize

```bash
# Create a ZIP of the app
ditto -c -k --keepParent \
    "build/Release/Choke Test Safety Check.app" \
    "ChokeTestApp.zip"

# Submit for notarization
xcrun notarytool submit "ChokeTestApp.zip" \
    --keychain-profile "notarytool-profile" \
    --wait

# Staple the ticket
xcrun stapler staple "build/Release/Choke Test Safety Check.app"
```

#### Step 4: Verify

```bash
xcrun stapler validate "build/Release/Choke Test Safety Check.app"
spctl --assess --type exec --verbose \
    "build/Release/Choke Test Safety Check.app"
```

### Creating a DMG

For easy distribution:

```bash
# Create DMG with create-dmg (install via brew)
create-dmg \
    --volname "Choke Test Safety Check" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "Choke Test Safety Check.app" 175 120 \
    --hide-extension "Choke Test Safety Check.app" \
    --app-drop-link 425 120 \
    "ChokeTestSafetyCheck.dmg" \
    "build/Release/Choke Test Safety Check.app"
```

## Optimization Tips

### Reducing App Size

Already optimized to ~10-20MB through:

✅ No external dependencies
✅ Native Swift/SwiftUI only
✅ Compiler optimizations
✅ Dead code stripping
✅ Asset compression

### Improving Build Times

```bash
# Use debug builds during development
make debug

# Incremental builds in Xcode (⌘B)
# Only rebuilds changed files
```

### Performance Profiling

In Xcode:

1. Run with Instruments: `⌘I`
2. Choose template:
   - **Time Profiler** for CPU usage
   - **Allocations** for memory usage
   - **Leaks** for memory leaks

## Troubleshooting

### "Cannot find 'X' in scope"

**Solution:** Build target → Build Phases → Compile Sources
- Ensure all Swift files are included

### "No such module 'X'"

**Solution:** This app has no external dependencies
- If you see this, the project is misconfigured

### "Signing for requires a development team"

**Solution:**
1. Free option: Add Apple ID in Xcode preferences
2. Or: Disable automatic signing and use manual

### "Code signature invalid"

**Solution:**
```bash
# Remove quarantine attribute
xattr -cr "Choke Test Safety Check.app"

# Re-sign
codesign --force --deep --sign - "Choke Test Safety Check.app"
```

### Build is slow

**Solution:**
- Use debug builds during development
- Close other apps to free up memory
- Consider using SSD for faster I/O

### App won't run on other Macs

**Solution:**
- Check deployment target (macOS 13.0)
- Ensure proper code signing
- Notarize for distribution

## Deployment Targets

### Minimum Version

Currently set to **macOS 13.0 (Ventura)**

To change:

1. Open project in Xcode
2. Select project in navigator
3. Select target
4. General → Deployment Info → macOS Deployment Target

**Note:** Lowering the deployment target may require API availability checks.

### Architecture

Builds for **Apple Silicon (arm64) and Intel (x86_64)** by default.

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build

on: [push, pull_request]

jobs:
  build:
    runs-on: macos-13

    steps:
    - uses: actions/checkout@v3

    - name: Build
      run: |
        cd ChokeTestApp
        xcodebuild -project ChokeTestApp.xcodeproj \
          -scheme ChokeTestApp \
          -configuration Release \
          build

    - name: Upload Artifact
      uses: actions/upload-artifact@v3
      with:
        name: ChokeTestApp
        path: ChokeTestApp/build/Release/Choke Test Safety Check.app
```

## Version Management

Update version numbers in:

1. **Xcode:**
   - Select project → Select target → General
   - Update Version and Build number

2. **Info.plist:**
   - `CFBundleShortVersionString` (version)
   - `CFBundleVersion` (build)

## Resources

- [Swift Documentation](https://swift.org/documentation/)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [Xcode Help](https://help.apple.com/xcode/)
- [Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

**Questions?** Open an issue or check the README.md for more information.
