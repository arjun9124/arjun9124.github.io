@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

echo.
echo ==== SITE CHANGELOG + PUSH ====
echo.

if not exist content\meta.md (
    echo ERROR: content\meta.md not found
    pause
    exit /b 1
)

set /p COMMITNAME=Commit title: 
if "%COMMITNAME%"=="" (
    echo Commit title required.
    pause
    exit /b 1
)

set /p CHANGELOG=Describe change: 
if "%CHANGELOG%"=="" (
    set "CHANGELOG=%COMMITNAME%"
)

echo.
echo Staging files...
git add -A

for /f "delims=" %%i in ('git diff --cached --name-only') do (
    set HASCHANGES=1
)

if not defined HASCHANGES (
    echo No changes detected.
    pause
    exit /b 0
)

echo Writing changelog entry...

set TMPPS=%TEMP%\meta_append_%RANDOM%.ps1

(
echo $file = "content/meta.md"
echo $title = @'
echo %COMMITNAME%
echo '@
echo $desc = @'
echo %CHANGELOG%
echo '@
echo $time = Get-Date -Format "yyyy-MM-dd HH:mm"
echo $entry = @()
echo $entry += ""
echo $entry += "### $time — $title"
echo $entry += ""
echo $entry += "$desc"
echo $entry += ""
echo $text = Get-Content $file -Raw
echo if ($text -match "(?s)(# Changelog\s*)") ^{
echo ^  $new = $text -replace "(?s)(# Changelog\s*)", "`$1`r`n" + ($entry -join "`r`n")
echo ^  Set-Content $file $new -Encoding UTF8
echo ^} else ^{
echo ^  Add-Content $file "`r`n# Changelog`r`n"
echo ^  Add-Content $file ($entry -join "`r`n")
echo ^}
) > "%TMPPS%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%TMPPS%"
del "%TMPPS%"

echo.
echo Committing...
git commit -m "%COMMITNAME%"
if errorlevel 1 (
    echo Commit failed.
    pause
    exit /b 1
)

echo.
echo Pushing...
git push -u origin main
if errorlevel 1 (
    echo Push failed.
    pause
    exit /b 1
)

echo.
echo Done.
pause