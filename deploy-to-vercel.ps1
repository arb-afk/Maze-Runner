# PowerShell script to build and deploy to Vercel
# Usage: .\deploy-to-vercel.ps1

Write-Host "Building game for web..." -ForegroundColor Green
pip install pygbag --user --upgrade
pygbag --build main.py

if (Test-Path "build\web") {
    Write-Host "Build successful! Files are in build\web\" -ForegroundColor Green
    Write-Host ""
    Write-Host "To deploy to Vercel:" -ForegroundColor Yellow
    Write-Host "1. cd build\web" -ForegroundColor Cyan
    Write-Host "2. vercel" -ForegroundColor Cyan
    Write-Host "3. vercel --prod (for production)" -ForegroundColor Cyan
} else {
    Write-Host "Build failed! Check for errors above." -ForegroundColor Red
}





