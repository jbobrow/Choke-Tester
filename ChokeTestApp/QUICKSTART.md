# Quick Start - Native Swift App

Get up and running with the Choke Test Safety Check native macOS app in 5 minutes.

## Prerequisites

You need:
- macOS 13.0+ (Ventura or later)
- Xcode 15.0+ (from Mac App Store)

## Setup

### Option 1: Create Xcode Project (First Time)

Since Xcode projects are user-specific, you'll need to create one:

```bash
# Navigate to the Swift app directory
cd ChokeTestApp

# Open Xcode and create new project
open -a Xcode
```

In Xcode:
1. File → New → Project
2. Choose: **macOS** → **App**
3. Fill in:
   - **Product Name:** ChokeTestApp
   - **Organization Identifier:** com.bambuchoke
   - **Interface:** SwiftUI
   - **Language:** Swift
4. **Save Location:** Choose the `ChokeTestApp` folder
5. When prompted to replace, click **Replace**

The source files are already in place!

### Option 2: Swift Package Manager (Alternative)

```bash
cd ChokeTestApp
swift build
swift run
```

## Building

### In Xcode

1. Open the project: `open ChokeTestApp.xcodeproj`
2. Select scheme: **ChokeTestApp**
3. Press `⌘R` to build and run

### Command Line

```bash
# Quick build and run
make run

# Or build release
make build

# Install to /Applications
make install
```

## First Run

1. App opens with drop zone
2. Drag a .stl or .3mf file onto the window
3. See instant analysis results
4. Click an object to preview in 3D

## Key Features

- **Drag & Drop:** Just drop files onto the app
- **Instant Analysis:** Native Swift performance
- **3D Preview:** Interactive SceneKit visualization
- **PDF Export:** ⌘E to export report
- **Settings:** ⌘, to change safety standard

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open STL | ⌘O |
| Open 3MF | ⌘⇧O |
| Export PDF | ⌘E |
| Settings | ⌘, |
| Quit | ⌘Q |

## Project Structure

```
ChokeTestApp/
├── ChokeTestApp.swift         # Main app entry
├── Models/
│   ├── ChokeStandard.swift    # Safety standards
│   ├── Mesh.swift             # 3D mesh data
│   └── ChokeTestResult.swift  # Analysis results
├── Services/
│   ├── ChokeTestAnalyzer.swift      # Core algorithm
│   ├── MeshLoader.swift             # File parsing
│   └── PDFReportGenerator.swift     # PDF export
└── Views/
    ├── ContentView.swift            # Main UI
    ├── MeshPreviewView.swift        # 3D preview
    └── SettingsView.swift           # Settings panel
```

## Development Tips

### Making Changes

1. Edit any `.swift` file
2. Press `⌘B` to build
3. Press `⌘R` to run with changes

### Debugging

- Set breakpoints by clicking line numbers
- Press `⌘R` to run in debug mode
- View variables in Debug Area (⌘⇧Y)

### Testing

```bash
make test
# Or in Xcode: ⌘U
```

## Common Issues

### "No such module 'X'"

This app has zero external dependencies. If you see this:
- Clean build folder: ⌘⇧K
- Rebuild: ⌘B

### "Signing requires a development team"

- In Xcode, select project → ChokeTestApp target
- Signing & Capabilities tab
- Select your Apple ID or team

### App won't open on other Macs

The app needs code signing for distribution:
- See [BUILD.md](BUILD.md) for signing instructions
- Or build on each Mac

## Next Steps

- Read [README.md](README.md) for full features
- See [BUILD.md](BUILD.md) for distribution
- Customize the app by editing Swift files

## Why Native Swift?

**10-20 MB** vs **1.3 GB** Python version
- Instant startup
- Native macOS look and feel
- Better performance
- No dependencies
- Smaller app size

## Need Help?

- Check [BUILD.md](BUILD.md) for detailed build instructions
- See [README.md](README.md) for features and architecture
- Open an issue on GitHub

---

**Time to first run:** ~5 minutes
**App size:** ~10-20 MB
**Dependencies:** None (pure Swift)

Happy testing! 🎯
