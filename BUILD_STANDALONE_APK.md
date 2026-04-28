# Building Standalone APK with Azure Backend

## Changes Made

1. **Hardcoded Azure Backend URL**: Both apps now always connect to `http://eduro.eastasia.cloudapp.azure.com`
2. **Removed Dev Mode Detection**: No more switching between local and production backends
3. **Enabled Cleartext Traffic**: Allows HTTP connections (required for non-HTTPS Azure endpoint)
4. **Cleaned Up Imports**: Removed unused Metro bundler dependencies

## Build Instructions

### Option 1: Using Build Script (Recommended)
```bash
cd ScholarshipApp
build-release.bat
```
or
```bash
cd EduroApp
build-release.bat
```

### Option 2: Manual Build
```bash
cd ScholarshipApp/android
gradlew assembleRelease
```

## APK Location
After build completes, find your APK at:
- `ScholarshipApp/android/app/build/outputs/apk/release/app-release.apk`
- `EduroApp/android/app/build/outputs/apk/release/app-release.apk`

## Installation
1. Transfer the APK to your Android device
2. Enable "Install from Unknown Sources" in device settings
3. Install the APK
4. The app will work standalone without USB connection
5. It will always connect to Azure backend

## Testing
1. Install the APK on your device
2. Disconnect USB cable
3. Open the app
4. It should load the Azure backend successfully

## Notes
- No Metro bundler required for release builds
- App bundles all JavaScript code internally
- Works completely offline from development machine
- Always connects to Azure backend regardless of build type
