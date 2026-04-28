@echo off
echo Building ScholarshipApp Release APK...
cd android
call gradlew assembleRelease
echo.
echo Build complete! APK location:
echo android\app\build\outputs\apk\release\app-release.apk
pause
