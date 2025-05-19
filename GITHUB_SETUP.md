# GitHub Repository Setup Instructions

1. First, create a Personal Access Token (PAT):
   - Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Give it a descriptive name (e.g., "Irrigation Control Addon")
   - Select scopes: `repo`, `workflow`
   - Copy the generated token (you'll only see it once)

2. Create the repository on GitHub:
   - Go to https://github.com/new
   - Repository name: `ha-irrigation-control`
   - Description: "Home Assistant addon for advanced irrigation control with P1/P2 events"
   - Make it Public
   - Don't initialize with any files
   - Click "Create repository"

3. Configure local repository:
```bash
# Remove existing remote if any
git remote remove origin

# Add the new remote with your token
# Replace YOUR_PAT with your personal access token
git remote add origin https://goatboynz:YOUR_PAT@github.com/goatboynz/ha-irrigation-control.git

# Verify the remote
git remote -v

# Add all files if not already done
git add .

# Create initial commit
git commit -m "Initial commit: Home Assistant Irrigation Control Addon"

# Push to GitHub
git push -u origin main
```

4. Verify the repository:
   - Go to https://github.com/goatboynz/ha-irrigation-control
   - You should see all your files there

5. Enable GitHub features:
   - Go to repository Settings
   - Enable Discussions (optional)
   - Configure branch protection (optional)
   - Enable GitHub Pages if you want to host documentation
