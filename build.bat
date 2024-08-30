

@echo off
pyinstaller -y -c -n ViSLCapture --icon=Nahida_2.ico main.py





xcopy /I /E to_copy\* dist\ViSLCapture\
