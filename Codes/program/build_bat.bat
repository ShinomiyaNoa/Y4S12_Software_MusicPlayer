@echo off
set PATH=D:\Code\Y4S12Software\Scripts;%PATH%

pyinstaller --add-data "D:\Code\Y4S12Software\Codes\program;main.qss" --add-data "D:\Code\Y4S12Software\Codes\program\component;component" --add-data "D:\Code\Y4S12Software\Codes\program\playlists;playlists" --distpath D:\Code\Y4S12Software_Build main.py

pause