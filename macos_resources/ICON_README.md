# macOS App Icon

## Quick Start

1. **Create your app icon** (1024x1024 PNG recommended)
   - Design a simple, recognizable icon for your app
   - Save as `icon_source.png` in this directory

2. **Generate the .icns file** (on macOS):
   ```bash
   python generate_icons.py icon_source.png
   ```

   This will create `AppIcon.icns` which is used by the build process.

## Manual Icon Creation (macOS)

If you prefer to create icons manually:

1. Create a folder named `AppIcon.iconset`

2. Add PNG files with these exact names:
   - icon_16x16.png (16×16)
   - icon_16x16@2x.png (32×32)
   - icon_32x32.png (32×32)
   - icon_32x32@2x.png (64×64)
   - icon_128x128.png (128×128)
   - icon_128x128@2x.png (256×256)
   - icon_256x256.png (256×256)
   - icon_256x256@2x.png (512×512)
   - icon_512x512.png (512×512)
   - icon_512x512@2x.png (1024×1024)

3. Convert to .icns:
   ```bash
   iconutil -c icns AppIcon.iconset -o AppIcon.icns
   ```

## Default Icon

If no icon is provided, the app will use the system default icon. For a professional app, you should create a custom icon.

## Icon Design Tips

- Use simple, bold shapes that are recognizable at small sizes
- Consider using a safety/warning theme (shield, check mark, warning triangle)
- Use colors that stand out: #2196F3 (blue), #FFC107 (amber), #4CAF50 (green)
- Test at multiple sizes (16px to 512px) to ensure clarity
- Avoid text in icons (hard to read at small sizes)

## Resources

- [Apple Human Interface Guidelines - Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [SF Symbols](https://developer.apple.com/sf-symbols/) - Apple's icon library for inspiration
