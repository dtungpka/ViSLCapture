

pyinstaller -c -n ViSLCapture --icon=Nahida_2.ico main.py

rmdir /S /Q to_copy\_internal
mkdir to_copy\_internal
7z a -r to_copy\backup.zip to_copy\config


xcopy /E /I to_copy dist\ViSLCapture