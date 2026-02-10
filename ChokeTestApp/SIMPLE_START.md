# Easiest Way to Get Started

## Option 1: Simple Xcode Project (Recommended)

### Step-by-Step

1. **Open Xcode** (don't create a project yet)

2. **File → New → Project**

3. **Select**: macOS → App → Next

4. **Fill in**:
   - Product Name: `ChokeTest`
   - Team: (your team)
   - Organization Identifier: `com.yourname`
   - Interface: `SwiftUI`
   - Language: `Swift`
   - ☐ Use Core Data: **unchecked**
   - ☐ Include Tests: **unchecked**

5. **Save to**: Desktop (or anywhere temporary)

6. **Now Xcode has created**:
   ```
   ChokeTest/
   ├── ChokeTest.xcodeproj
   └── ChokeTest/
       ├── ChokeTestApp.swift
       ├── ContentView.swift
       └── Assets.xcassets
   ```

7. **Delete the auto-generated source files**:
   - In Xcode Project Navigator, select:
     - `ChokeTestApp.swift`
     - `ContentView.swift`
   - Right-click → Delete → Move to Trash

8. **Add our files**:
   - Right-click on `ChokeTest` folder (the yellow one)
   - "Add Files to ChokeTest..."
   - Navigate to: `ChokeTestApp/ChokeTestApp/`
   - Select ALL folders: `Models`, `Views`, `Services`
   - Select the file: `ChokeTestAppApp.swift`
   - **Important**:
     - ✅ Check "Copy items if needed"
     - ✅ Check "Create groups"
   - Click Add

9. **Add Info.plist and entitlements**:
   - Same process, add:
     - `Info.plist`
     - `ChokeTestApp.entitlements`

10. **Update project settings**:
    - Click project in navigator (blue icon)
    - Select ChokeTest target
    - General tab:
      - Bundle Identifier: should auto-fill
    - Signing & Capabilities:
      - Select your team
    - Info tab:
      - Custom macOS Application Target Properties
      - Find "Info.plist File"
      - Set to: `ChokeTest/Info.plist`

11. **Build**: ⌘B

12. **Run**: ⌘R

## Option 2: Even Simpler - Single File Build

### Quick Test Build

Create a single-file version for testing:

1. Create `test.swift`:

```bash
cd ChokeTestApp
cat > test_build.swift << 'EOF'
import SwiftUI

@main
struct SimpleApp: App {
    var body: some Scene {
        WindowGroup {
            Text("ChokeTest - Building...")
                .frame(width: 400, height: 300)
        }
    }
}
EOF
```

2. Build it:

```bash
swiftc test_build.swift -o ChokeTest
./ChokeTest
```

This confirms Swift is working, then tackle the full app.

## Option 3: Use My Pre-Configured Structure

I'll create a flattened structure that's easier:

```bash
cd ChokeTestApp

# Flatten the structure
mkdir -p Flat
cp ChokeTestApp/ChokeTestAppApp.swift Flat/
cp ChokeTestApp/Models/*.swift Flat/
cp ChokeTestApp/Views/*.swift Flat/
cp ChokeTestApp/Services/*.swift Flat/
```

Now in Xcode:
1. New Project → ChokeTest
2. Delete auto-files
3. Add all files from `Flat/` folder
4. Build!

## Troubleshooting

### "Cannot find type X in scope"
- Make sure ALL Swift files are added to the target
- Check: File Inspector (⌘⌥1) → Target Membership → ✅ ChokeTest

### "Entry point not found"
- Make sure `ChokeTestAppApp.swift` is included
- It has the `@main` attribute

### Files won't add
- Try: Project → Add Files to "ChokeTest"
- Select files individually if batch fails

## What You Should See

When it works:
- Clean, minimal window
- Drop zone saying "Drop 3D Models Here"
- No errors in Xcode

---

**Still stuck?** Let me know and I'll create an even simpler approach!
