"""
macOS native app build configuration using py2app.

Build commands:
    python setup_macos.py py2app           # Build production .app bundle
    python setup_macos.py py2app -A        # Build alias mode (for development)

The built app will be in dist/Choke Test Safety Check.app
"""

from setuptools import setup
import os

APP = ['run.py']
APP_NAME = 'Choke Test Safety Check'
VERSION = '1.0.0'

DATA_FILES = []

OPTIONS = {
    'argv_emulation': True,  # Enable drag-and-drop file handling
    'iconfile': 'macos_resources/AppIcon.icns',  # App icon
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.bambuchoke.choketest',
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.15.0',  # Catalina or later
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Bambu Studio Project',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Default',
                'LSItemContentTypes': ['com.bambulab.3mf'],
                'CFBundleTypeExtensions': ['3mf'],
            },
            {
                'CFBundleTypeName': 'STL 3D Model',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Default',
                'LSItemContentTypes': ['public.standard-tesselated-geometry-format'],
                'CFBundleTypeExtensions': ['stl'],
            },
        ],
        'UTExportedTypeDeclarations': [
            {
                'UTTypeIdentifier': 'com.bambulab.3mf',
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['3mf'],
                    'public.mime-type': ['application/vnd.ms-package.3dmanufacturing-3dmodel+xml'],
                },
                'UTTypeConformsTo': ['public.data', 'public.archive'],
                'UTTypeDescription': 'Bambu Studio 3D Manufacturing Format',
            },
        ],
        'NSPrincipalClass': 'NSApplication',
        'NSHumanReadableCopyright': '© 2025 Bambu Choke Check',
    },
    'packages': [
        'PySide6',
        'trimesh',
        'numpy',
        'scipy',
        'shapely',
        'reportlab',
        'matplotlib',
        'analyzer',
        'batch',
        'integrations',
        'reports',
        'ui',
    ],
    'includes': [
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'trimesh.exchange.export',
        'trimesh.exchange.load',
    ],
    'excludes': [
        'tkinter',
        'test',
        'unittest',
        'distutils',
        'setuptools',
    ],
    'resources': [],
    'optimize': 2,  # Maximum optimization
    'compressed': True,  # Compress Python bytecode
    'semi_standalone': False,  # Full standalone app
    'site_packages': True,
    'strip': True,  # Strip debug symbols
}

setup(
    name=APP_NAME,
    app=APP,
    version=VERSION,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
