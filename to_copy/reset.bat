@echo off

REM Step 1: Kill ViSLCapture.exe process
taskkill /F /IM ViSLCapture.exe > nul 2>&1

REM Step 2: Delete config and output folders
rmdir /S /Q config > nul 2>&1
rmdir /S /Q output > nul 2>&1

REM Step 3: Unzip backup.zip file
powershell -Command "Expand-Archive -Path '_internal\backup.zip' -DestinationPath '.'"

REM Turn off echo command
@echo off

REM Echo every step made and prepare to made
echo Killing ViSLCapture.exe process...
echo Deleting config and output folders...
echo Unzipping backup.zip file...

REM Echo a Done message
echo Done.

REM Exit the batch file
exit