# 🖥️ AUTOOS Desktop App - Complete Guide

Build and publish AUTOOS desktop application for Windows, macOS, and Linux.

---

## 📋 Overview

The AUTOOS desktop app is built with **Electron** and provides:
- Native desktop experience
- System tray integration
- Auto-updates
- Offline capabilities
- Native notifications
- File system access

---

## 🚀 Quick Start

```bash
# Navigate to desktop app
cd frontend/desktop

# Install dependencies
npm install

# Run in development
npm start

# Build for all platforms
npm run build
```

---

## 📦 Project Structure

```
frontend/desktop/
├── main.js              # Electron main process
├── preload.js           # Preload script (security)
├── renderer/            # UI code (React/HTML)
├── package.json         # Dependencies & build config
├── assets/              # Icons and images
│   ├── icon.png        # App icon (1024x1024)
│   ├── icon.icns       # macOS icon
│   ├── icon.ico        # Windows icon
│   └── tray-icon.png   # System tray icon
└── build/              # Build output
```

---

## 🛠️ Setup Development Environment

### 1. Install Node.js

```bash
# macOS (using Homebrew)
brew install node

# Windows (using Chocolatey)
choco install nodejs

# Linux (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be v18 or higher
npm --version
```

### 2. Install Dependencies

```bash
cd frontend/desktop
npm install
```

### 3. Configure package.json

```json
{
  "name": "autoos",
  "version": "1.0.0",
  "description": "AUTOOS - AI Automation Operating System",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build:win": "electron-builder --win",
    "build:mac": "electron-builder --mac",
    "build:linux": "electron-builder --linux",
    "build:all": "electron-builder -mwl",
    "pack": "electron-builder --dir",
    "dist": "electron-builder"
  },
  "build": {
    "appId": "com.autoos.app",
    "productName": "AUTOOS",
    "copyright": "Copyright © 2024 AUTOOS",
    "directories": {
      "output": "dist",
      "buildResources": "assets"
    },
    "files": [
      "**/*",
      "!**/*.ts",
      "!*.map",
      "!node_modules",
      "!src",
      "!dist"
    ],
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico",
      "publisherName": "AUTOOS Inc"
    },
    "mac": {
      "target": ["dmg", "zip"],
      "icon": "assets/icon.icns",
      "category": "public.app-category.productivity",
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    },
    "linux": {
      "target": ["AppImage", "deb", "rpm"],
      "icon": "assets/icon.png",
      "category": "Utility"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  },
  "dependencies": {
    "electron-store": "^8.1.0",
    "electron-updater": "^6.1.0"
  },
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.9.0"
  }
}
```

---

## 💻 Building the Desktop App

### Windows Build

#### Prerequisites
- Windows 10/11
- Node.js 18+
- Visual Studio Build Tools (optional, for native modules)

#### Build Commands

```bash
# Build Windows installer
npm run build:win

# Output files:
# dist/AUTOOS Setup 1.0.0.exe  (Installer)
# dist/AUTOOS 1.0.0.exe        (Portable)
```

#### Sign Windows Executable (Optional)

```bash
# Get code signing certificate ($100-400/year)
# From: DigiCert, Sectigo, or Comodo

# Sign the executable
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/AUTOOS-Setup-1.0.0.exe

# Verify signature
signtool verify /pa dist/AUTOOS-Setup-1.0.0.exe
```

### macOS Build

#### Prerequisites
- macOS 10.15+
- Xcode Command Line Tools
- Apple Developer Account ($99/year for distribution)

#### Build Commands

```bash
# Build macOS app
npm run build:mac

# Output files:
# dist/AUTOOS-1.0.0.dmg        (Disk Image)
# dist/AUTOOS-1.0.0-mac.zip    (ZIP Archive)
```

#### Sign macOS App

```bash
# 1. Get Apple Developer certificate
# Sign up at developer.apple.com

# 2. Install certificate in Keychain

# 3. Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/mac/AUTOOS.app

# 4. Verify signature
codesign --verify --deep --strict --verbose=2 dist/mac/AUTOOS.app

# 5. Notarize with Apple (required for macOS 10.15+)
xcrun altool --notarize-app \
  --primary-bundle-id "com.autoos.app" \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file dist/AUTOOS-1.0.0.dmg

# 6. Check notarization status
xcrun altool --notarization-info <RequestUUID> \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD"

# 7. Staple notarization ticket
xcrun stapler staple dist/AUTOOS-1.0.0.dmg

# 8. Verify stapling
xcrun stapler validate dist/AUTOOS-1.0.0.dmg
```

### Linux Build

#### Prerequisites
- Linux (Ubuntu, Debian, Fedora, etc.)
- Node.js 18+
- Build tools: `sudo apt install build-essential`

#### Build Commands

```bash
# Build Linux packages
npm run build:linux

# Output files:
# dist/AUTOOS-1.0.0.AppImage    (Universal)
# dist/autoos_1.0.0_amd64.deb   (Debian/Ubuntu)
# dist/autoos-1.0.0.x86_64.rpm  (Fedora/RHEL)
```

#### Build All Platforms (from any OS)

```bash
# Build for all platforms at once
npm run build:all

# Note: Building macOS requires macOS
# Use CI/CD (GitHub Actions) to build all platforms
```

---

## 🎨 Creating App Icons

### Icon Requirements

| Platform | Format | Sizes |
|----------|--------|-------|
| Windows | .ico | 16, 32, 48, 64, 128, 256 |
| macOS | .icns | 16, 32, 64, 128, 256, 512, 1024 |
| Linux | .png | 512, 1024 |

### Generate Icons

```bash
# 1. Create master icon (1024x1024 PNG)
# Use design tool: Figma, Sketch, Photoshop

# 2. Install icon generator
npm install -g electron-icon-maker

# 3. Generate all icon formats
electron-icon-maker --input=icon.png --output=./assets

# This creates:
# - icon.ico (Windows)
# - icon.icns (macOS)
# - icon.png (Linux)
```

### Online Icon Generators (Free)

- **iConvert Icons**: iconverticons.com/online
- **CloudConvert**: cloudconvert.com
- **AConvert**: aconvert.com/icon

---

## 📤 Publishing Desktop App

### Option 1: GitHub Releases (FREE)

```bash
# 1. Build all platforms
npm run build:all

# 2. Create GitHub release
# Go to: github.com/yourusername/autoos/releases/new

# 3. Upload files:
# - AUTOOS-Setup-1.0.0.exe (Windows)
# - AUTOOS-1.0.0.dmg (macOS)
# - AUTOOS-1.0.0.AppImage (Linux)
# - autoos_1.0.0_amd64.deb (Linux)

# 4. Write release notes

# 5. Publish release

# Download URL:
# https://github.com/yourusername/autoos/releases/download/v1.0.0/AUTOOS-Setup-1.0.0.exe
```

**Cost**: FREE forever

### Option 2: Your Website (FREE)

```bash
# 1. Build apps
npm run build:all

# 2. Upload to your server
scp dist/* user@yourserver.com:/var/www/autoos/downloads/

# 3. Create download page
# https://autoos.com/download

# Download links:
# https://autoos.com/downloads/AUTOOS-Setup-1.0.0.exe
# https://autoos.com/downloads/AUTOOS-1.0.0.dmg
# https://autoos.com/downloads/AUTOOS-1.0.0.AppImage
```

**Cost**: FREE (if you have hosting)

### Option 3: Microsoft Store (Windows)

#### Prerequisites
- Microsoft Partner Center account ($19 one-time)
- Windows 10/11 app package

#### Steps

```bash
# 1. Create MSIX package
npm install -g electron-windows-store

# 2. Convert to MSIX
electron-windows-store \
  --input-directory dist/win-unpacked \
  --output-directory dist/msix \
  --package-version 1.0.0.0 \
  --package-name AUTOOS \
  --publisher-display-name "AUTOOS Inc"

# 3. Sign MSIX
signtool sign /f certificate.pfx /p password dist/msix/AUTOOS.msix

# 4. Upload to Microsoft Partner Center
# - Go to partner.microsoft.com
# - Create new app submission
# - Upload MSIX package
# - Fill out store listing
# - Submit for certification

# Review time: 1-3 days
```

**Cost**: $19 one-time registration

### Option 4: Mac App Store

#### Prerequisites
- Apple Developer Account ($99/year)
- Mac with Xcode
- App Store Connect account

#### Steps

```bash
# 1. Build for Mac App Store
npm run build:mac -- --mac mas

# 2. Sign with Mac App Store certificate
codesign --deep --force --verify --verbose \
  --sign "3rd Party Mac Developer Application: Your Name" \
  --entitlements build/entitlements.mas.plist \
  dist/mas/AUTOOS.app

# 3. Create installer package
productbuild --component dist/mas/AUTOOS.app /Applications \
  --sign "3rd Party Mac Developer Installer: Your Name" \
  dist/AUTOOS-1.0.0.pkg

# 4. Upload to App Store Connect
# Use Transporter app or altool

xcrun altool --upload-app \
  --type macos \
  --file dist/AUTOOS-1.0.0.pkg \
  --username "your@email.com" \
  --password "@keychain:AC_PASSWORD"

# 5. Fill out App Store listing
# 6. Submit for review

# Review time: 1-3 days
```

**Cost**: $99/year

### Option 5: Snap Store (Linux)

```bash
# 1. Create snapcraft.yaml
cat > snapcraft.yaml << EOF
name: autoos
version: '1.0.0'
summary: AUTOOS - AI Automation
description: |
  AUTOOS is an enterprise-grade Automation Operating System
  for intelligent workflow orchestration.
grade: stable
confinement: strict
base: core20

apps:
  autoos:
    command: autoos
    plugs: [network, home, desktop]

parts:
  autoos:
    plugin: dump
    source: dist/linux-unpacked
EOF

# 2. Build snap
snapcraft

# 3. Test snap
sudo snap install autoos_1.0.0_amd64.snap --dangerous

# 4. Publish to Snap Store
snapcraft login
snapcraft upload autoos_1.0.0_amd64.snap --release=stable

# Your app: https://snapcraft.io/autoos
```

**Cost**: FREE

---

## 🔄 Auto-Updates

### Implement Auto-Updates

```javascript
// main.js
const { app, autoUpdater } = require('electron');
const { autoUpdater } = require('electron-updater');

// Configure auto-updater
autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'yourusername',
  repo: 'autoos'
});

// Check for updates on startup
app.on('ready', () => {
  autoUpdater.checkForUpdatesAndNotify();
});

// Check for updates every hour
setInterval(() => {
  autoUpdater.checkForUpdatesAndNotify();
}, 3600000);

// Handle update events
autoUpdater.on('update-available', () => {
  console.log('Update available');
});

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});
```

### Publish Updates

```bash
# 1. Increment version in package.json
# "version": "1.0.1"

# 2. Build new version
npm run build:all

# 3. Create GitHub release with new version
# Tag: v1.0.1

# 4. Upload new installers

# Users will auto-update!
```

---

## 🎯 Distribution Checklist

### Before Publishing

- [ ] Test on Windows 10/11
- [ ] Test on macOS 10.15+
- [ ] Test on Ubuntu/Debian
- [ ] Test on Fedora/RHEL
- [ ] Verify all features work
- [ ] Test auto-update mechanism
- [ ] Check app icon displays correctly
- [ ] Verify system tray integration
- [ ] Test notifications
- [ ] Check file permissions
- [ ] Verify network connectivity
- [ ] Test offline mode
- [ ] Check memory usage
- [ ] Verify CPU usage is reasonable

### Publishing

- [ ] Build for all platforms
- [ ] Sign Windows executable
- [ ] Sign and notarize macOS app
- [ ] Create GitHub release
- [ ] Upload all installers
- [ ] Write release notes
- [ ] Update download page
- [ ] Announce on social media
- [ ] Submit to app stores (optional)
- [ ] Update documentation

---

## 📊 Platform-Specific Features

### Windows

```javascript
// Windows-specific features
const { app } = require('electron');

// Add to Windows Start Menu
app.setAppUserModelId('com.autoos.app');

// Windows notifications
const { Notification } = require('electron');
new Notification({
  title: 'AUTOOS',
  body: 'Workflow completed!',
  icon: 'assets/icon.ico'
}).show();

// Windows taskbar progress
mainWindow.setProgressBar(0.5); // 50%
```

### macOS

```javascript
// macOS-specific features
const { app } = require('electron');

// macOS dock badge
app.dock.setBadge('5');

// macOS dock menu
app.dock.setMenu(Menu.buildFromTemplate([
  { label: 'New Workflow', click: () => {} },
  { label: 'View Dashboard', click: () => {} }
]));

// macOS Touch Bar
const { TouchBar } = require('electron');
const touchBar = new TouchBar({
  items: [
    new TouchBar.TouchBarButton({
      label: 'New Workflow',
      click: () => {}
    })
  ]
});
mainWindow.setTouchBar(touchBar);
```

### Linux

```javascript
// Linux-specific features
const { app } = require('electron');

// Linux system tray
const { Tray, Menu } = require('electron');
const tray = new Tray('assets/tray-icon.png');
tray.setContextMenu(Menu.buildFromTemplate([
  { label: 'Show AUTOOS', click: () => {} },
  { label: 'Quit', click: () => app.quit() }
]));

// Linux desktop notifications
const { Notification } = require('electron');
new Notification({
  title: 'AUTOOS',
  body: 'Workflow completed!',
  urgency: 'normal'
}).show();
```

---

## 🐛 Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### App Won't Start

```bash
# Check logs
# Windows: %APPDATA%\AUTOOS\logs
# macOS: ~/Library/Logs/AUTOOS
# Linux: ~/.config/AUTOOS/logs
```

### Code Signing Issues

```bash
# Windows: Verify certificate
certutil -dump certificate.pfx

# macOS: List certificates
security find-identity -v -p codesigning

# macOS: Check notarization
xcrun stapler validate AUTOOS.dmg
```

---

## 💡 Pro Tips

### 1. Use CI/CD for Builds

```yaml
# .github/workflows/build.yml
name: Build Desktop App

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: dist/*
```

### 2. Reduce App Size

```bash
# Remove unnecessary files
# Add to package.json build.files
"files": [
  "!**/*.map",
  "!**/node_modules/*/{CHANGELOG.md,README.md}",
  "!**/node_modules/.bin"
]

# Use asar to package app
"asar": true
```

### 3. Improve Performance

```javascript
// Use lazy loading
const module = require('electron').remote.require('./heavy-module');

// Enable hardware acceleration
app.commandLine.appendSwitch('enable-gpu-rasterization');

// Optimize memory
app.commandLine.appendSwitch('js-flags', '--max-old-space-size=4096');
```

---

## 📈 Analytics & Crash Reporting

### Add Sentry

```bash
npm install @sentry/electron
```

```javascript
// main.js
const Sentry = require('@sentry/electron');

Sentry.init({
  dsn: 'your-sentry-dsn'
});
```

### Add Google Analytics

```javascript
// renderer.js
const { ipcRenderer } = require('electron');

// Track events
ipcRenderer.send('analytics-event', {
  category: 'Workflow',
  action: 'Created',
  label: 'Automation'
});
```

---

## 🎉 You're Ready to Publish!

Your desktop app is now ready for distribution across Windows, macOS, and Linux!

**Quick Recap:**
1. Build for all platforms: `npm run build:all`
2. Sign executables (Windows/macOS)
3. Upload to GitHub Releases (FREE)
4. Or submit to app stores (optional)
5. Enable auto-updates
6. Monitor with analytics

**Total Cost:**
- **FREE**: GitHub Releases distribution
- **$19**: Microsoft Store (optional)
- **$99/year**: Mac App Store (optional)

Start with free GitHub distribution, then add app stores as you grow!

**Good luck! 🚀**
