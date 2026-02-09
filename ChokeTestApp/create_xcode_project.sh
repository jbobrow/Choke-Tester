#!/bin/bash
#
# Create Xcode Project for Choke Test Safety Check
#
# This script sets up the Xcode project structure
#

set -e

echo "Creating Xcode project structure..."

# Create project bundle if it doesn't exist
mkdir -p ChokeTestApp.xcodeproj

# Check if user has Xcode installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode not found. Please install Xcode from the Mac App Store."
    exit 1
fi

echo ""
echo "✓ Xcode found"
echo ""
echo "To complete the project setup:"
echo ""
echo "1. Open Xcode"
echo "2. File → New → Project"
echo "3. Choose macOS → App"
echo "4. Product Name: ChokeTestApp"
echo "5. Organization Identifier: com.bambuchoke"
echo "6. Interface: SwiftUI"
echo "7. Language: Swift"
echo "8. Save in: $(pwd)"
echo ""
echo "9. Replace the default files with the ones in ChokeTestApp/"
echo ""
echo "Or use this Swift Package Manager approach:"
echo ""
echo "  swift package init --type executable"
echo "  # Then add SwiftUI support manually"
echo ""
echo "For a pre-configured project, the maintainer should commit"
echo "the .xcodeproj file to the repository."
echo ""

# Create a Package.swift as alternative
cat > Package.swift << 'EOF'
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ChokeTestApp",
    platforms: [
        .macOS(.v13)
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "ChokeTestApp",
            dependencies: [],
            path: "ChokeTestApp"
        )
    ]
)
EOF

echo "✓ Created Package.swift as alternative build system"
echo ""
echo "To build with Swift Package Manager:"
echo "  swift build"
echo "  swift run"
echo ""
