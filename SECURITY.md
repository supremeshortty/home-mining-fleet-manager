# Security Guidelines

## Credential Management

### What's Protected

This repository uses `.gitignore` to prevent sensitive information from being committed to GitHub:

**Files excluded from git:**
- `pi-config.sh` - Contains your Raspberry Pi credentials
- `*.db` - Database files (may contain sensitive miner data)
- `.env` - Environment variables
- `*.log` - Log files
- `*.backup` - Backup files

### Setting Up Credentials (First Time)

**Step 1: Create your local credentials file**
```bash
cp pi-config.sh.template pi-config.sh
```

**Step 2: Edit with your actual credentials**
```bash
nano pi-config.sh
```

Add your Raspberry Pi information:
```bash
PI_USER="your_username"
PI_HOST="your_pi_ip_address"
PI_PASSWORD="your_password"
PI_DIR="~/home-mining-fleet-manager"
```

**Step 3: Verify it's excluded from git**
```bash
git status
# pi-config.sh should NOT appear in the list
```

### Important Security Notes

1. **Never commit `pi-config.sh`** - It's in `.gitignore` for a reason
2. **Never hardcode credentials** - Always use the config file
3. **Use strong passwords** - Especially if your Pi is internet-facing
4. **Keep backups private** - Don't store database backups in public places
5. **Review before committing** - Always check `git diff` before pushing

### Verifying No Credentials in Repository

Before pushing to GitHub, verify no sensitive data:

```bash
# Check what will be committed
git status

# Review changes
git diff

# Search for potential credentials
grep -r "password" --exclude-dir=".git" --exclude="*.md" --exclude="*.template"
```

### If You Accidentally Committed Credentials

If you've already committed credentials to git:

**Option 1: Remove from latest commit (if not pushed yet)**
```bash
# Remove file from git but keep locally
git rm --cached pi-config.sh

# Amend the commit
git commit --amend

# Force push (only if you haven't shared the commit)
git push --force
```

**Option 2: Use BFG Repo-Cleaner (if already pushed)**
```bash
# Install BFG
brew install bfg

# Clone a fresh copy
git clone --mirror https://github.com/USERNAME/dirtysats.git

# Remove passwords from all commits
cd dirtysats.git
bfg --replace-text passwords.txt

# Push cleaned history
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push
```

**Option 3: Start fresh (nuclear option)**
```bash
# Delete the GitHub repository
# Create a new repository
# Push clean code without history
```

**After cleaning git history:**
- Change your Pi password immediately
- Update pi-config.sh with the new password

### Best Practices

1. **Local Development**
   - Keep `pi-config.sh` on your development machine only
   - Use different passwords for different environments
   - Don't share your `pi-config.sh` file

2. **SSH Keys Instead of Passwords (Recommended)**
   Consider using SSH keys instead of password authentication:
   ```bash
   # Generate SSH key on Mac
   ssh-keygen -t ed25519

   # Copy to Pi
   ssh-copy-id USERNAME@PI_IP

   # Update update-pi.sh to use keys instead of password
   ```

3. **Network Security**
   - Keep your Pi on a private network
   - Use firewall rules to limit access
   - Consider VPN for remote access instead of exposing SSH

4. **Regular Audits**
   - Periodically check what's being committed: `git log --stat`
   - Review `.gitignore` to ensure it's up to date
   - Monitor GitHub for any accidentally committed secrets

### Environment Variables

For additional security, you can use environment variables:

```bash
# In ~/.zshrc or ~/.bashrc
export PI_PASSWORD="your_password"
```

Then update `pi-config.sh`:
```bash
PI_PASSWORD="${PI_PASSWORD:-default_value}"
```

This way the password is never stored in a file.

### Reporting Security Issues

If you find a security vulnerability, please:
1. Do NOT create a public GitHub issue
2. Contact the repository owner directly
3. Allow time for the issue to be patched before public disclosure

---

## Summary Checklist

- [ ] `pi-config.sh` is in `.gitignore`
- [ ] Never hardcode credentials in any file
- [ ] Use `pi-config.sh.template` for examples only
- [ ] Review commits before pushing
- [ ] Change passwords if accidentally exposed
- [ ] Consider SSH keys instead of passwords
- [ ] Keep backups secure and private
