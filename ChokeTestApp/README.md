# Choke Test Safety Check - Native macOS App

A lightweight, native Swift/SwiftUI application for analyzing 3D models against safety-standard choke test cylinders.

**Size:** ~10-20 MB (vs 1.3GB for Python version)
**Performance:** Native Swift with optimized algorithms
**UI:** Clean, minimalist SwiftUI design

## Features

✨ **Native Performance**
- Pure Swift implementation
- Optimized geometric algorithms
- Instant startup and analysis
- <20MB app size

🎯 **Minimalist Design**
- Clean SwiftUI interface
- Drag & drop support
- Real-time 3D preview with SceneKit
- Keyboard shortcuts

🔍 **Analysis**
- STL and 3MF file support
- US CPSC and EU EN-71 standards
- Batch processing
- PDF report generation

## Quick Start

### Requirements

- macOS 13.0 (Ventura) or later
- Xcode 15.0 or later

### Building

```bash
# Open in Xcode
open ChokeTestApp.xcodeproj

# Or build from command line
xcodebuild -project ChokeTestApp.xcodeproj \
    -scheme ChokeTestApp \
    -configuration Release \
    build
```

### Running

1. Open `ChokeTestApp.xcodeproj` in Xcode
2. Press `⌘R` to build and run
3. Or build and find the app in `build/Release/Choke Test Safety Check.app`

## Architecture

### Core Components

```
ChokeTestApp/
├── Models/
│   ├── ChokeStandard.swift      # Safety standard definitions
│   ├── Mesh.swift                # 3D mesh representation
│   └── ChokeTestResult.swift     # Analysis results
├── Services/
│   ├── ChokeTestAnalyzer.swift   # Core analysis algorithm
│   ├── MeshLoader.swift          # STL/3MF parsing
│   └── PDFReportGenerator.swift  # PDF export
└── Views/
    ├── ContentView.swift         # Main UI
    ├── MeshPreviewView.swift     # 3D visualization
    └── SettingsView.swift        # Settings panel
```

### Key Algorithms

**Choke Test Analysis** (`ChokeTestAnalyzer.swift`)
- Tests 360 orientations for optimal fit
- Minimum enclosing circle (Welzl's algorithm)
- Height calculation per orientation
- Concurrent processing with Swift async/await

**Mesh Loading** (`MeshLoader.swift`)
- Binary and ASCII STL parsing
- 3MF ZIP extraction and XML parsing
- Efficient vertex deduplication

**3D Preview** (`MeshPreviewView.swift`)
- SceneKit integration
- Interactive camera controls
- Visual hazard indication

## Performance

| Metric | Native Swift | Python py2app |
|--------|-------------|---------------|
| **App Size** | 10-20 MB | 1,300 MB |
| **Startup** | <1 second | 3-5 seconds |
| **Memory** | 50-100 MB | 150-250 MB |
| **Analysis Speed** | Fast | Fast |

## Development

### Project Structure

The app follows a clean SwiftUI architecture:

- **Models:** Pure Swift data structures
- **Services:** Business logic and algorithms
- **Views:** SwiftUI components
- **No Dependencies:** 100% native Swift/SwiftUI

### Adding Features

1. **New Safety Standard:**
   ```swift
   // In ChokeStandard.swift
   static let custom = ChokeStandard(
       name: "Custom",
       diameterMM: 30.0,
       heightMM: 50.0,
       description: "Custom standard"
   )
   ```

2. **New File Format:**
   - Add parser in `MeshLoader.swift`
   - Update `FileType` enum

3. **UI Customization:**
   - Modify SwiftUI views
   - All styling uses native system colors/fonts

### Building for Distribution

```bash
# Archive for distribution
xcodebuild -project ChokeTestApp.xcodeproj \
    -scheme ChokeTestApp \
    -configuration Release \
    -archivePath build/ChokeTestApp.xcarchive \
    archive

# Export
xcodebuild -exportArchive \
    -archivePath build/ChokeTestApp.xcarchive \
    -exportPath build/Export \
    -exportOptionsPlist ExportOptions.plist
```

### Code Signing

For distribution, you'll need:

1. Apple Developer account
2. Developer ID Application certificate
3. Notarization

See [Apple's documentation](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution) for details.

## Usage

### Basic Workflow

1. **Open Files:** Drag .stl or .3mf files onto the app
2. **Review Results:** See instant analysis results
3. **Export Report:** ⌘E to export PDF report

### Keyboard Shortcuts

- `⌘O` - Open STL files
- `⌘⇧O` - Open 3MF project
- `⌘E` - Export PDF report
- `⌘,` - Settings
- `⌘Q` - Quit

### File Support

- **STL:** Binary and ASCII formats
- **3MF:** Bambu Studio and standard 3MF files

## Safety Standards

### US CPSC (Default)
- Diameter: 31.75mm (1.25")
- Height: 57.15mm (2.25")

### EU EN-71
- Diameter: 31.2mm (~1.23")
- Height: 52.3mm (~2.06")

## Comparison: Swift vs Python

### Why Native Swift?

**Size:**
- Swift: 10-20 MB app
- Python: 1,300 MB (includes Python runtime, all dependencies)

**Performance:**
- Swift: Native compiled code, instant startup
- Python: Interpreted, slower startup

**Integration:**
- Swift: Native macOS APIs, system UI
- Python: Qt wrapper, non-native feel

**Maintenance:**
- Swift: Pure Swift, no dependencies
- Python: Multiple dependencies to maintain

### Migration Notes

The Swift version is a complete rewrite with:
- Same analysis algorithm (minimum enclosing circle)
- Same file format support (STL, 3MF)
- Same safety standards (CPSC, EN-71)
- Cleaner, more maintainable code
- Better performance and user experience

## Troubleshooting

### Build Issues

**"Command line tools not found"**
```bash
xcode-select --install
```

**"Signing for X requires a development team"**
- Set your development team in Xcode project settings
- Or disable signing for local development

### Runtime Issues

**"App is damaged"**
- Right-click → Open (first time only)
- Or: `xattr -cr "Choke Test Safety Check.app"`

**File won't open**
- Check file format (must be .stl or .3mf)
- Verify file isn't corrupted

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with Swift and SwiftUI
- Uses SceneKit for 3D visualization
- Implements Welzl's algorithm for minimum enclosing circle
- Safety standards from CPSC and EN-71

---

**Made with native Swift for maximum performance and minimal footprint**
