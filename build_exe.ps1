# PowerShell Build Script for Google Maps Scraper
# Creates a standalone Windows executable

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host " Google Maps Scraper - Build to EXE" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan

# Step 1: Activate virtual environment
Write-Host "`nStep 1: Activating virtual environment..." -ForegroundColor Cyan
& .\env\Scripts\Activate.ps1

# Step 2: Install PyInstaller if not already installed
Write-Host "`nStep 2: Installing PyInstaller..." -ForegroundColor Cyan
pip install pyinstaller

# Step 3: Clean previous builds
Write-Host "`nStep 3: Cleaning previous builds..." -ForegroundColor Cyan
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "   Removed dist/ folder" -ForegroundColor Gray
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "   Removed build/ folder" -ForegroundColor Gray
}

# Step 4: Check for icon file
Write-Host "`nStep 4: Checking for icon file..." -ForegroundColor Cyan
if (-not (Test-Path "assets/icon.ico")) {
    Write-Host "   WARNING: assets/icon.ico not found!" -ForegroundColor Yellow
    Write-Host "   Will build without custom icon" -ForegroundColor Yellow
    Write-Host "   Run 'python create_icon.py' to generate icon" -ForegroundColor Yellow
} else {
    Write-Host "   Found icon: assets/icon.ico" -ForegroundColor Green
}

# Step 5: Build executable
Write-Host "`nStep 5: Building executable with PyInstaller..." -ForegroundColor Cyan
Write-Host "   This may take 5-10 minutes..." -ForegroundColor Gray
pyinstaller build_exe.spec

# Step 6: Check if build succeeded
Write-Host "`nStep 6: Checking build results..." -ForegroundColor Cyan
if (Test-Path "dist/GoogleMapsScraper/GoogleMapsScraper.exe") {
    Write-Host "   " -NoNewline
    Write-Host "SUCCESS!" -ForegroundColor Green
    
    # Get file size
    $fileSize = (Get-Item "dist/GoogleMapsScraper/GoogleMapsScraper.exe").Length / 1MB
    Write-Host "   Executable size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    
    Write-Host "`n" -NoNewline
    Write-Host "=" -ForegroundColor Green -NoNewline
    Write-Host ("=" * 69) -ForegroundColor Green
    Write-Host " Build Complete!" -ForegroundColor Yellow
    Write-Host "=" -ForegroundColor Green -NoNewline
    Write-Host ("=" * 69) -ForegroundColor Green
    
    Write-Host "`nYour executable is ready:" -ForegroundColor Green
    Write-Host "   Location: dist\GoogleMapsScraper\" -ForegroundColor White
    Write-Host "   File: GoogleMapsScraper.exe" -ForegroundColor White
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "   1. Copy the entire 'dist\GoogleMapsScraper' folder" -ForegroundColor White
    Write-Host "   2. Paste it anywhere you want" -ForegroundColor White
    Write-Host "   3. Double-click GoogleMapsScraper.exe to run" -ForegroundColor White
    
    Write-Host "`nNote:" -ForegroundColor Yellow
    Write-Host "   - The entire folder is needed (not just the .exe)" -ForegroundColor Gray
    Write-Host "   - Chromium browser is bundled (~746 MB total)" -ForegroundColor Gray
    Write-Host "   - Ready to run immediately - no installation needed!" -ForegroundColor Gray
    
} else {
    Write-Host "   " -NoNewline
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "`nCheck the error messages above" -ForegroundColor Yellow
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "   - Missing dependencies (run: pip install -r requirements.txt)" -ForegroundColor Gray
    Write-Host "   - Virtual environment not activated" -ForegroundColor Gray
    Write-Host "   - Antivirus blocking PyInstaller" -ForegroundColor Gray
}

Write-Host ""
