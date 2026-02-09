# Choke Test Safety Check

A native macOS application for analyzing 3D-printed objects against safety-standard choke test cylinders to identify potential choking hazards.

![Platform](https://img.shields.io/badge/platform-macOS-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Visual Analysis**: Check 3D models against US CPSC and EU EN-71 safety standards
- **Batch Processing**: Analyze entire folders of models at once
- **Multiple Formats**: Support for .STL and .3MF (Bambu Studio) files
- **Detailed Reports**: Export results as PDF, CSV, or JSON
- **Drag & Drop**: Simple drag-and-drop interface
- **Native macOS**: Optimized native application for macOS

## Screenshots

The app features a clean, modern interface:
- Results table showing all analyzed objects
- 3D preview of selected objects
- Visual indication of choking hazards
- Drag & drop file support

## Quick Start

### For Users

#### Download & Install

1. Download the latest `ChokeTestSafetyCheck-macOS.dmg` from releases
2. Open the DMG file
3. Drag "Choke Test Safety Check" to Applications
4. Launch from Applications or Spotlight

#### Using the App

1. **Open files**: Drag .stl or .3mf files onto the app window
2. **Review results**: See which objects are potential choking hazards
3. **Export report**: File → Export PDF Report

### For Developers

#### Running from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/choke-tester.git
cd choke-tester

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 run.py
```

#### Building for macOS

See [BUILD_MACOS.md](BUILD_MACOS.md) for detailed build instructions.

Quick build:
```bash
# Install build dependencies
pip install -r requirements-macos.txt

# Build the app
./build_macos.sh

# Create installer DMG
./create_dmg.sh
```

## Safety Standards

The app supports two safety standards:

- **US CPSC**: 1.25" diameter × 2.25" height (31.75mm × 57.15mm)
- **EU EN-71**: 1.23" diameter × 2.06" height (31.2mm × 52.3mm)

Objects that can fit entirely within the choke cylinder are flagged as potential hazards.

## Command Line Usage

The app also supports command-line operation:

```bash
# Analyze a single file
python3 run.py --cli model.stl

# Batch process a folder
python3 run.py --batch /path/to/models --output /path/to/reports

# Open file in GUI
python3 run.py --file model.3mf

# Use EU standard
python3 run.py --cli model.stl --standard eu_en71
```

## Use Cases

- **Parents**: Check small 3D-printed toys before giving to children
- **Makers**: Ensure prints are safe for young children
- **Educators**: Verify classroom materials meet safety standards
- **Businesses**: Batch-check product safety compliance

## Technical Details

### Built With

- **PySide6**: Modern Qt6 GUI framework
- **trimesh**: 3D mesh processing
- **NumPy/SciPy**: Numerical computations
- **shapely**: Geometric analysis
- **ReportLab**: PDF report generation
- **py2app**: macOS application bundling

### How It Works

1. Load 3D mesh from STL or 3MF file
2. Test all possible orientations of the object
3. For each orientation:
   - Project to 2D from cylinder's perspective
   - Calculate minimum enclosing circle
   - Check if it fits within cylinder diameter and height
4. Report if object fits in any orientation (= hazard)

### Architecture

```
Choke-Tester/
├── analyzer/          # Core choke test algorithms
│   ├── choke_check.py    # Main analysis logic
│   └── standards.py      # Safety standard definitions
├── batch/             # Batch processing
│   └── batch_processor.py
├── integrations/      # File format support
│   └── read_3mf.py       # 3MF file parsing
├── reports/           # Report generation
│   └── pdf_report.py     # PDF export
├── ui/                # GUI components
│   ├── app.py            # Application entry point
│   ├── main_window.py    # Main window
│   ├── preview_widget.py # 3D preview
│   ├── results_table.py  # Results display
│   └── settings_dialog.py
├── tests/             # Unit tests
└── run.py             # Main entry point
```

## macOS Optimization

This app is specifically optimized for macOS with:

- Native `.app` bundle
- File associations for .3mf and .stl files
- Dark mode support
- Retina display optimization
- macOS-native dialogs and UI elements
- Drag & drop support
- Quick Look integration (planned)

## Development

### Running Tests

```bash
pytest tests/
```

### Development Mode

For rapid testing without rebuilding:

```bash
./launch_macos.sh
```

Or use alias mode:
```bash
./build_macos.sh --dev
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### App Won't Open

Right-click the app and select "Open" to bypass Gatekeeper, or:
```bash
xattr -cr "/Applications/Choke Test Safety Check.app"
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Build Issues

See [BUILD_MACOS.md](BUILD_MACOS.md) troubleshooting section.

## Roadmap

- [ ] Quick Look plugin for .3mf files
- [ ] Custom safety standards
- [ ] 3D visualization improvements
- [ ] Batch processing progress improvements
- [ ] Cloud sync for reports
- [ ] iOS companion app

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built for use with Bambu Studio
- Safety standards from CPSC and EN-71
- Icon design inspired by safety symbols

## Disclaimer

This tool is provided as-is for informational purposes. Always follow official safety guidelines and regulations. The developers are not responsible for any injuries or damages resulting from the use of this software.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/choke-tester/issues)
- **Documentation**: [BUILD_MACOS.md](BUILD_MACOS.md)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/choke-tester/discussions)

---

**Made with ❤️ for safer 3D printing**
