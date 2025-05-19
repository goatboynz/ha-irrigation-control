# Repository Restructure Instructions

1. Make the script executable:
```bash
chmod +x git_commands.sh
```

2. Run the script to move files:
```bash
./git_commands.sh
```

3. Verify the new structure:
```
ha-irrigation-control/
├── .gitignore
├── CHANGELOG.md
├── DOCS.md
├── LICENSE
├── README.md
├── repository.yaml
└── irrigation_control_addon/
    ├── Dockerfile
    ├── README.md
    ├── apparmor.txt
    ├── build.yaml
    ├── config.yaml
    ├── irrigation_control/
    ├── requirements.txt
    ├── rootfs/
    └── run.sh
```

4. Test the repository in Home Assistant:
   - Remove the previous repository if added
   - Add the repository again: https://github.com/goatboynz/ha-irrigation-control
   - The addon should now appear in the addon store
   - Install and test the addon

If you encounter any issues:
1. Check the repository structure matches the above
2. Verify all files were moved correctly
3. Ensure repository.yaml is in the root directory
4. Make sure all files are committed and pushed to GitHub
5. Try clearing your browser cache and refreshing Home Assistant

Need to undo changes?
```bash
# Undo the restructure if needed
git reset --hard HEAD~1
git push -f origin main
