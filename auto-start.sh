#!/bin/bash

# Function to find the latest Python version installed
find_latest_python_version() {
    local python_versions=($(ls -d /usr/local/lib/python*/site-packages/ 2>/dev/null))
    local latest_version=""

    for path in "${python_versions[@]}"; do
        local versions=($(echo $path | grep -oP 'python\d+\.\d+' | sort -V))
        if [ ${#versions[@]} -gt 0 ]; then
            latest_version=${versions[-1]}
            break
        fi
    done

    echo "$latest_version"
}

# Determine the Python version installed in /usr/local/lib/python*/site-packages/
python_version=$(find_latest_python_version)

if [ -z "$python_version" ]; then
    echo "Error: Python version not found in /usr/local/lib/python*/site-packages/"
    exit 1
fi

echo "Detected Python version: $python_version"

# Reset Database
# Ensure the correct path is used based on the operating system
if [ -f /root/.local/share/oterm/store.db ]; then
    rm /root/.local/share/oterm/store.db
fi

# Install 'uv' package globally
pip install uv

# Copy oterm executable to /usr/local/bin/
# Ensure the correct path is used
if [ -f .usr/local/bin/oterm ]; then
    cp .usr/local/bin/oterm /usr/local/bin/
else
    echo "Error: oterm executable not found in .usr/local/bin/"
    exit 1
fi

# Copy oterm package to the determined Python version site-packages directory
# Ensure the correct path is used
if [ -d ../oterm ] && [ -d .oterm-0.4.0.dist-info ]; then
    cp -r ../oterm /usr/local/lib/$python_version/site-packages/
    cp -r .oterm-0.4.0.dist-info /usr/local/lib/$python_version/site-packages/oterm-0.4.0.dist-info
else
    echo "Error: oterm package or dist-info not found"
    exit 1
fi

# Use 'uv' to install packages from requirements.txt globally
if [ -f requirements.txt ]; then
    uv pip install --system -r requirements.txt
else
    echo "Error: requirements.txt not found"
    exit 1
fi

# Optional: Clean up temporary files or perform any post-installation tasks
# Ensure the correct permissions
chmod +x /usr/local/bin/oterm

# Run oterm
oterm
