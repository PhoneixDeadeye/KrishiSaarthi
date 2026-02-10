# Assets Note

## Logo

The `logo.svg` file is the source logo. To generate required formats:

### Generate PNG (512x512):

**Option 1: Online Converter**
1. Go to https://cloudconvert.com/svg-to-png
2. Upload logo.svg
3. Set size to 512x512
4. Download as logo.png

**Option 2: Using ImageMagick** (if installed)
```bash
magick convert logo.svg -resize 512x512 logo.png
```

**Option 3: Using Inkscape** (if installed)
```bash
inkscape logo.svg --export-type=png --export-width=512 --export-height=512 --export-filename=logo.png
```

### Generate Favicon:

**Option 1: Online Generator**
1. Go to https://www.favicon-generator.org/
2. Upload logo.png or logo.svg
3. Download the generated favicon.ico
4. Place in this directory

**Option 2: Using ImageMagick**
```bash
magick convert logo.png -define icon:auto-resize=16,32,48,64,256 favicon.ico
```

## Current Status

- ✅ logo.svg created
- ⏳ logo.png (needs to be generated)
- ⏳ favicon.ico (needs to be generated)

For now, the browser will use logo.svg as the favicon, but .ico format is recommended for better compatibility.
