rmdir /s build /Q
rmdir /s dist /Q
del *.spec

pyinstaller main.py ^
    --name Algae ^
    --add-data "res/*.png;res/" ^
    --noconsole ^
    --icon "res/icon.ico"