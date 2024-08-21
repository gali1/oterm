#!/bin/bash

# Function to find the latest Python version in /usr/local/lib/python*/site-packages/
find_latest_python_version() {
    local python_versions=("/usr/local/lib/python*/site-packages/")
    local latest_version=""

    for path in ${python_versions[@]}; do
        local versions=($(ls -1d $path | grep -oP 'python\d+\.\d+' | sort -V))
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
rm /root/.local/share/oterm/store.db

# Install 'uv' package globally
pip install uv

# Copy oterm executable to /usr/local/bin/
cp .usr/local/bin/oterm /usr/local/bin/

# Copy oterm package to the determined Python version site-packages directory
# cp -r ../oterm /usr/local/lib/$python_version/site-packages/
rm -rf /usr/local/lib/$python_version/site-packages/oterm
ln -s --relative ../oterm /usr/local/lib/$python_version/site-packages/oterm
cp -r .oterm-0.4.0.dist-info /usr/local/lib/$python_version/site-packages/oterm-0.4.0.dist-info

# Use 'uv' to install packages from requirements.txt globally
uv pip install --system -r requirements.txt

# Optional: Clean up temporary files or perform any post-installation tasks

chmod +x /usr/local/bin/oterm

oterm