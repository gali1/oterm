#!/bin/bash

# Function to find the latest Python version installed
find_latest_python_version() {
    local python_paths=("/usr/local/lib/python*/site-packages/" "$HOME/.local/lib/python*/site-packages/")
    local latest_version=""

    for base_path in "${python_paths[@]}"; do
        local paths=($(ls -d $base_path 2>/dev/null | grep -oP 'python\d+\.\d+' | sort -V))
        if [ ${#paths[@]} -gt 0 ]; then
            latest_version=${paths[-1]}
            break
        fi
    done

    echo "$latest_version"
}

# Determine the Python version
python_version=$(find_latest_python_version)

if [ -z "$python_version" ]; then
    echo "Error: Python version not found."
    exit 1
fi

echo "Detected Python version: $python_version"

# Paths based on OS
if [ "$(uname)" == "Darwin" ]; then
    # MacOS paths
    bin_path="/usr/local/bin"
    site_packages_path="/Library/Python/$python_version/site-packages"
elif [ "$(uname)" == "Linux" ]; then
    # Linux paths
    bin_path="/usr/local/bin"
    site_packages_path="/usr/local/lib/$python_version/site-packages"
elif [ -n "$WINDIR" ]; then
    # Windows paths (in WSL or native)
    bin_path="/mnt/c/ProgramData/oterm/bin"  # Adapt to actual path
    site_packages_path="/mnt/c/ProgramData/oterm/lib/python$python_version/site-packages"
else
    echo "Unsupported OS"
    exit 1
fi

# Reset Database
db_path="$HOME/.local/share/oterm/store.db"
if [ -f "$db_path" ]; then
    rm "$db_path"
fi

# Install 'uv' package globally
pip install uv

# Copy oterm executable to the bin directory
if [ -f ".usr/local/bin/oterm" ]; then
    cp .usr/local/bin/oterm "$bin_path/"
else
    echo "Error: oterm executable not found."
    exit 1
fi

# Update oterm package in the Python site-packages directory
oterm_path="$site_packages_path/oterm"
dist_info_path="$site_packages_path/oterm-0.4.0.dist-info"

if [ -d "$oterm_path" ]; then
    rm -rf "$oterm_path"
fi

if [ -d "../oterm" ]; then
    ln -s --relative "../oterm" "$oterm_path"
else
    echo "Error: oterm package not found."
    exit 1
fi

if [ -d ".oterm-0.4.0.dist-info" ]; then
    cp -r .oterm-0.4.0.dist-info "$dist_info_path"
else
    echo "Error: oterm dist-info not found."
    exit 1
fi

# Use 'uv' to install packages from requirements.txt globally
if [ -f "requirements.txt" ]; then
    uv pip install --system -r requirements.txt
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Optional: Clean up temporary files or perform any post-installation tasks
chmod +x "$bin_path/oterm"

# Run oterm
"$bin_path/oterm"
