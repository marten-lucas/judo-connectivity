#!/bin/bash

# Source and destination directories
SOURCE_DIR="/workspaces/homeassistant-dev-core/homeassistant/components/judo_connectivity/"
DEST_DIR="/workspaces/repos/judo-connectivity/custom_components/judo_connectivity/"

# Ensure destination directory exists
mkdir -p "$DEST_DIR"

# Sync the files from source to destination
rsync -av --delete "$SOURCE_DIR" "$DEST_DIR"

# Navigate to the repo directory to stage and commit changes
cd /workspaces/repos/judo-connectivity

# Git commands to add, commit, and push changes
git add .
git commit -m "Sync judo_connectivity updates"
git push origin main
