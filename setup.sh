#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Function to display messages
function echo_message() {
    echo "-----------------------------------"
    echo "$1"
    echo "-----------------------------------"
}

# Create a virtual environment
echo_message "Creating a virtual environment..."
virtualenv venv -p python3.10

# Check if the virtual environment was created successfully
if [ $? -eq 0 ]; then
    echo_message "Virtual environment created successfully."
else
    echo_message "Failed to create virtual environment."
    exit 1
fi

# Activate the virtual environment
echo_message "Activating the virtual environment..."
source venv/bin/activate

# Navigate to the project directory
echo_message "Navigating to the project directory..."
cd code/audio_cloner/

# Install dependencies
echo_message "Installing dependencies..."
pip3 install -e .

if [ $? -eq 0 ]; then
    echo_message "Dependencies installed successfully."
else
    echo_message "Failed to install dependencies."
    exit 1
fi

echo_message "Setup complete! To run the script, execute:"
echo "source venv/bin/activate && python main.py"
