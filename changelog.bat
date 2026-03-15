@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ==== SITE CHANGELOG + PUSH ====
echo.

if not exist "content\meta.md" (
    echo ERROR: content\meta.md not found
    pause
    exit /b 1
)

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not a git repository.
    pause
    exit /b 1
)

set /p COMMITNAME=Commit title: 
if "%COMMITNAME%"=="" (
    echo ERROR: Commit title required.
    pause
    exit /b 1
)

set /p CHANGELOG=Describe change: 
if "%CHANGELOG%"=="" set "CHANGELOG=%COMMITNAME%"

echo.
echo Staging files...
git add -A

git diff --cached --quiet
if not errorlevel 1 (
    echo No changes detected.
    pause
    exit /b 0
)

echo Writing changelog entry...

set "TMPPS=%TEMP%\meta_append_%RANDOM%_%RANDOM%.ps1"

> "%TMPPS%" (
    echo $file = "content/meta.md"
    echo $title = @'
    echo %COMMITNAME%
    echo '@
    echo $desc = @'
    echo %CHANGELOG%
    echo '@
    echo $time = Get-Date -Format "yyyy-MM-dd HH:mm"
    echo $entry = @(^)
    echo $entry += ""
    echo $entry += "### $time - $title"
    echo $entry += ""
    echo $entry += "$desc"
    echo $entry += ""
    echo $text = Get-Content -LiteralPath $file -Raw
    echo if ^($text -match "(?s)(# Changelog\s*)"^) ^{
    echo ^    $new = $text -replace "(?s)(# Changelog\s*)", "`$1`r`n" + ^($entry -join "`r`n"^)
    echo ^    Set-Content -LiteralPath $file -Value $new -Encoding UTF8
    echo ^} else ^{
    echo ^    Add-Content -LiteralPath $file -Value "`r`n# Changelog`r`n"
    echo ^    Add-Content -LiteralPath $file -Value ^($entry -join "`r`n"^)
    echo ^}
)

if not exist "%TMPPS%" (
    echo ERROR: Failed to create temporary PowerShell script.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%TMPPS%"
if errorlevel 1 (
    del /q "%TMPPS%" >nul 2>&1
    echo ERROR: Failed to append changelog.
    pause
    exit /b 1
)

del /q "%TMPPS%" >nul 2>&1

git add content\meta.md

echo.
echo Committing...
git commit -m "%COMMITNAME%"
if errorlevel 1 (
    echo ERROR: Commit failed.
    pause
    exit /b 1
)

echo.
echo Pushing...
git push -u origin main
if errorlevel 1 (
    echo ERROR: Push failed.
    pause
    exit /b 1
)

echo.
echo Done.
pause