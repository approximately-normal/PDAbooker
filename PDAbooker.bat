echo off
title My Test Batch File 
:: See the title at the top. And this comment will not appear in the command prompt.

echo 'False' >C:\Users\allan\Documents\pythonStuff\PDAbooker\booked_bool.txt

:while
start "my_booking_script" python.exe C:\Users\allan\Documents\pythonStuff\PDAbooker\PDAbooker2.py
timeout /t 60
taskkill /f /FI "WINDOWTITLE eq my_booking_script"

timeout /t 240
goto :while

