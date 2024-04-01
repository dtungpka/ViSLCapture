

@echo off
pyinstaller -y -c -n ViSLCapture --icon=Nahida_2.ico main.py

rmdir /S /Q to_copy\_internal
mkdir to_copy\_internal

cd to_copy

7z a -r _internal\backup.zip config

cd..

xcopy /I /E to_copy\* dist\ViSLCapture\
