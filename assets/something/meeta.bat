@echo off
setlocal enabledelayedexpansion

REM === Supported image extensions ===
for %%F in (*.jpg *.jpeg *.png *.webp *.tif *.tiff) do (

    REM Check if corresponding .meta file exists
    if not exist "%%F.meta" (

        echo Creating meta for %%F

        (
            echo {
            echo   "Title": "%%~nF",
            echo   "ImageDescription": "Description for %%~nF",
            echo   "Tags": ["default"],
            echo   "Rating": 0
            echo }
        ) > "%%F.meta"

    ) else (
        echo Skipping %%F (meta already exists)
    )
)

echo Done.
pause
