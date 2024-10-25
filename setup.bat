@echo off
setlocal enabledelayedexpansion

REM Function to display messages
set "divider=-----------------------------------"
set "message="

:display_message
echo !divider!
echo !message!
echo !divider!
goto :eof

REM Create a virtual environment
set message=Creating a virtual environment...
call :display_message
virtualenv venv -p python3.10

REM Check if the virtual environment was created successfully
if %ERRORLEVEL% neq 0 (
    set message=Failed to create virtual environment.
    call :display_message
    exit /b 1
) else (
    set message=Virtual environment created successfully.
    call :display_message
)

REM Activate the virtual environment
set message=Activating the virtual environment...
call :display_message
call venv\Scripts\activate

REM Navigate to the project directory
set message=Navigating to the project directory...
call :display_message
cd code\audio_cloner\

REM Install dependencies
set message=Installing dependencies...
call :display_message
pip install -e .

if %ERRORLEVEL% neq 0 (
    set message=Failed to install dependencies.
    call :display_message
    exit /b 1
) else (
    set message=Dependencies installed successfully.
    call :display_message
)

set message=Setup complete! To run the script, execute:
call :display_message
echo call venv\Scripts\activate && python main.py
