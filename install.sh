#!/bin/bash

# Check that python is already installed or not.
function install_python() {
    if ! command -v python &>/dev/null; then
        echo "Python is not installed. Installing..."
        apt-get install -y python
    else
        echo "Python is already installed."
    fi
}

install_python
