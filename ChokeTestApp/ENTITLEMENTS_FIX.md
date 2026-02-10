# Fixing Entitlements in Xcode

If you see: **"Unable to display save panel: your app has the User Selected File Read entitlement but it needs User Selected File Read/Write"**

## Quick Fix

### Step 1: Check Entitlements File is Linked

1. **Select your project** (blue icon) in Project Navigator
2. **Select ChokeTest target**
3. Go to **Build Settings** tab
4. Search for: `Code Signing Entitlements`
5. Make sure it's set to: `ChokeTest/ChokeTestApp.entitlements`
   - If blank, set it to the path of your entitlements file

### Step 2: Verify Entitlements Content

The entitlements file should have:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-only</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

### Step 3: Alternative - Use Xcode UI

1. **Select project** → **ChokeTest target**
2. Go to **Signing & Capabilities** tab
3. Click **+ Capability**
4. Add **App Sandbox**
5. Under **File Access**:
   - ✅ Check **User Selected File** → **Read/Write**

### Step 4: Clean and Rebuild

```bash
⌘⇧K  # Clean
⌘B   # Build
⌘R   # Run
```

## Why This Happens

macOS sandboxed apps need explicit permission to:
- Read files the user selects (Read)
- Save files where the user chooses (Read/Write)

The error means Xcode isn't applying the entitlements file correctly.

## Verify It Works

After fixing, try:
1. Open a file - should work
2. Export PDF Report - should show save panel
3. No error about entitlements

---

If still not working, check that the entitlements file is in the project and properly referenced in Build Settings.
