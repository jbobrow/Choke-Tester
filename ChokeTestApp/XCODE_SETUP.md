# Setting Up the Xcode Project

## Quick Solution: Use Swift Package Manager

The easiest way to build without Xcode project hassles:

```bash
cd ChokeTestApp

# Build
swift build

# Run (note: GUI apps need special handling with SPM)
swift run
```

## Proper Xcode Setup

### Option 1: Let Xcode Generate, Then Replace

1. **Create New Xcode Project:**
   ```bash
   # Start in ChokeTestApp directory
   cd ChokeTestApp
   ```

2. **In Xcode:**
   - File → New → Project
   - Choose: **macOS** → **App**
   - Product Name: **ChokeTest** (without "App" suffix)
   - Organization Identifier: `com.bambuchoke`
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Save in: `ChokeTestApp` folder (one level up from where you are)

3. **Xcode will create:**
   ```
   ChokeTest/
   ├── ChokeTestApp.swift  (their generated file)
   └── ContentView.swift
   ```

4. **Delete the auto-generated files:**
   - Right-click `ChokeTestApp.swift` → Delete → Move to Trash
   - Right-click `ContentView.swift` → Delete → Move to Trash

5. **Add our files:**
   - Right-click `ChokeTest` folder in Project Navigator
   - Add Files to "ChokeTest"...
   - Select all files from `ChokeTestApp/` directory
   - ✅ Check "Copy items if needed"
   - ✅ Check "Create groups"
   - Add

### Option 2: Rename Our Main File

Simpler approach - rename our file to match Xcode's convention:

```bash
cd ChokeTestApp/ChokeTestApp
mv ChokeTestApp.swift ChokeTestAppApp.swift
```

Then create a standard Xcode project and it will recognize this file.

### Option 3: Use the Script (Recommended)

I'll create a setup script that does this automatically:

