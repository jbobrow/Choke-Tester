#!/bin/bash
#
# Xcode Project Setup Script
# Creates a properly configured Xcode project for ChokeTestApp
#

set -e

echo "🎯 ChokeTestApp - Xcode Project Setup"
echo ""

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode not found. Please install Xcode from the Mac App Store."
    exit 1
fi

echo "✓ Xcode found"
echo ""

# Check current directory
if [[ ! -f "setup_xcode.sh" ]]; then
    echo "❌ Please run this script from the ChokeTestApp directory"
    echo "   cd ChokeTestApp && ./setup_xcode.sh"
    exit 1
fi

echo "📁 Setting up project structure..."
echo ""

# Create a clean project structure
PROJECT_NAME="ChokeTest"
BUNDLE_ID="com.bambuchoke.choketest"

# Check if project already exists
if [[ -d "${PROJECT_NAME}.xcodeproj" ]]; then
    echo "⚠️  Project already exists: ${PROJECT_NAME}.xcodeproj"
    read -p "   Delete and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "${PROJECT_NAME}.xcodeproj"
        rm -rf "${PROJECT_NAME}"
        echo "   Deleted existing project"
    else
        echo "   Keeping existing project. Exiting."
        exit 0
    fi
fi

echo ""
echo "Creating Xcode project structure..."
echo ""

# Create the Xcode project using xcodebuild
# We'll use a template approach

cat > create_project.sh << 'INNER_EOF'
#!/bin/bash

# This script creates the Xcode project using AppleScript to automate Xcode
osascript <<'EOF'
tell application "Xcode"
    -- We can't easily create projects via AppleScript
    -- So we'll provide manual instructions instead
end tell
EOF
INNER_EOF

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Manual Setup Required (One-Time Only)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Please follow these steps in Xcode:"
echo ""
echo "1. Open Xcode"
echo "2. File → New → Project..."
echo "3. Select: macOS → App"
echo "4. Click Next"
echo ""
echo "5. Fill in the form:"
echo "   Product Name: ${PROJECT_NAME}"
echo "   Organization Identifier: ${BUNDLE_ID}"
echo "   Interface: SwiftUI"
echo "   Language: Swift"
echo "   ☐ Use Core Data (unchecked)"
echo "   ☐ Include Tests (unchecked)"
echo ""
echo "6. Click Next"
echo ""
echo "7. Save Location:"
echo "   → Select: $(pwd)"
echo "   ⚠️  IMPORTANT: Uncheck 'Create Git repository'"
echo ""
echo "8. Click Create"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press ENTER when you've completed the above steps..."
echo ""

# Check if project was created
if [[ ! -d "${PROJECT_NAME}.xcodeproj" ]]; then
    echo "❌ Project not found. Please try again."
    exit 1
fi

echo "✓ Project created!"
echo ""
echo "Now cleaning up and organizing files..."
echo ""

# Remove auto-generated files
if [[ -d "${PROJECT_NAME}" ]]; then
    cd "${PROJECT_NAME}"

    # Remove auto-generated Swift files (we have our own)
    rm -f "${PROJECT_NAME}App.swift" 2>/dev/null || true
    rm -f ContentView.swift 2>/dev/null || true
    rm -f Assets.xcassets 2>/dev/null || true

    echo "✓ Removed auto-generated files"

    # Copy our files here
    echo ""
    echo "Copying source files..."

    # Copy the ChokeTestApp directory contents
    if [[ -d "../ChokeTestApp" ]]; then
        cp -R ../ChokeTestApp/* .
        echo "✓ Source files copied"
    fi

    cd ..
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "1. Open the project:"
echo "   open ${PROJECT_NAME}.xcodeproj"
echo ""
echo "2. In Xcode, verify all files are in the project navigator"
echo ""
echo "3. Build and run: ⌘R"
echo ""
echo "If files are missing from the project:"
echo "  • Right-click project → Add Files to '${PROJECT_NAME}'..."
echo "  • Select the ChokeTestApp folder"
echo "  • ✓ Copy items if needed"
echo "  • ✓ Create groups"
echo "  • Add"
echo ""
