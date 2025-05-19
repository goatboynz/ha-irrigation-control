#!/bin/bash
# Commands to restructure the repository for Home Assistant addon format

# Create irrigation_control directory for addon
mkdir -p irrigation_control_addon

# Move addon files to the new directory
mv Dockerfile irrigation_control_addon/
mv requirements.txt irrigation_control_addon/
mv run.sh irrigation_control_addon/
mv apparmor.txt irrigation_control_addon/
mv build.yaml irrigation_control_addon/
mv config.yaml irrigation_control_addon/
mv irrigation_control/ irrigation_control_addon/
mv rootfs/ irrigation_control_addon/

# Create a simple README for the addon directory
echo "# Irrigation Control Add-on" > irrigation_control_addon/README.md
echo "Advanced irrigation control addon for Home Assistant with P1/P2 events and unlimited zones." >> irrigation_control_addon/README.md
echo "" >> irrigation_control_addon/README.md
echo "For full documentation, please see the [repository README](../README.md)." >> irrigation_control_addon/README.md

# Git commands to update
git add irrigation_control_addon/
git commit -m "Restructure: Move addon files to subdirectory"
git push origin main

# Done!
echo "Repository restructured for Home Assistant addon format"
