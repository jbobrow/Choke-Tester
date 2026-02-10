# Changelog

All notable changes to Choke Test Safety Check will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-09

### Added - macOS Native App Release

- **Native macOS application** with full py2app build system
- **Automated build scripts** (`build_macos.sh`, `create_dmg.sh`)
- **DMG installer** creation with optional styled layout
- **App icon generation** tools and templates
- **File associations** for .3mf and .stl files on macOS
- **Code signing support** for distribution
- **Comprehensive documentation**:
  - `README.md` - Main project documentation
  - `BUILD_MACOS.md` - Detailed build guide
  - `macos_resources/ICON_README.md` - Icon creation guide
- **Development tools**:
  - Makefile for common tasks
  - Quick launcher script
  - Development build mode
- **macOS optimizations**:
  - Dark mode support
  - Retina display optimization
  - Native dialogs and UI elements
  - Drag & drop file handling
  - argv emulation for file opening

### Changed

- Updated `.gitignore` for build artifacts
- Enhanced setup for macOS-specific requirements
- Optimized application bundle size and startup time

### Technical Details

- Bundle identifier: `com.bambuchoke.choketest`
- Minimum macOS version: 10.15 (Catalina)
- Build system: py2app 0.28.0+
- GUI framework: PySide6 6.5.0+

### Developer Notes

The app can now be built as a native macOS application with:
```bash
make build    # or ./build_macos.sh
make dmg      # or ./create_dmg.sh
```

For development:
```bash
make run      # Run from source
make dev      # Build in alias mode and open
```

## [0.9.0] - Previous Version

### Features

- 3D model choke test analysis
- Support for STL and 3MF (Bambu Studio) files
- US CPSC and EU EN-71 safety standards
- Batch processing capability
- PDF, CSV, and JSON report export
- Interactive 3D preview
- Drag & drop interface
- CLI mode for automation

---

For installation and usage instructions, see [README.md](README.md).
For building from source, see [BUILD_MACOS.md](BUILD_MACOS.md).
