@echo off
REM Navigate to the main directory where the executable is located
cd main

REM Install the dependencies from requirements.txt
pip install -r requirements.txt

REM Run the executable
Fynoxium.py

REM Return to the original directory
cd ..