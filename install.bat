echo off
cls
color 0a
cd D:\Users\cypoo\Python\PyngPong
python -m PyInstaller --onefile -w --icon=D:\Users\cypoo\Python\PyngPong\assets\images\icon.ico main.pyw
move "D:\Users\cypoo\Python\PyngPong\dist\main.exe" "D:\Users\cypoo\Python\PyngPong"
del "D:\Users\cypoo\Python\PyngPong\main.spec"
rmdir /s /q "D:\Users\cypoo\Python\PyngPong\__pycache__"
rmdir /s /q "D:\Users\cypoo\Python\PyngPong\build"
rmdir /s /q "D:\Users\cypoo\Python\PyngPong\dist"
