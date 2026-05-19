# ZP42 Branch Protection Requirements

## Status
**BLOCKED** - Requires repository administrator access to configure

## Required Configuration

### Option 1: Repository Rulesets (Recommended)
Navigate to: `https://github.com/iQs-Group/zp42/settings/rules`

Create ruleset: "main-branch-protection"
- **Target branches:** `main`
- **Enforcement:** Active

### Option 2: Branch Protection Rules (Legacy)
Navigate to: `https://github.com/iQs-Group/zp42/settings/branches`

Add rule for branch: `main`

## Required Settings

### 1. Require Pull Request Before Merging
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (if CODEOWNERS file present)
- ✅ Require approval of the most recent reviewable push

### 2. Require Status Checks Before Merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- **Required checks:**
  - `test-suite` (pytest)
  - `prohibited-term-scan`
  - `secret-scan`
  - `python-compile`

### 3. Require Conversation Resolution
- ✅ Require conversation resolution before merging

### 4. Block Force Pushes
- ✅ Do not allow force pushes

### 5. Block Branch Deletion
- ✅ Do not allow deletions

### 6. Restrict Who Can Push
- ✅ Restrict pushes that create matching branches
- **Allowed:**
  - Repository administrators only (for emergency fixes)
  - CI/CD service accounts (if required)
- **Blocked:**
  - All other users (must use PRs)

### 7. Bypass Allowances
- **Allowed to bypass:**
  - Repository owner (emergency use only)
  - Organization admins (emergency use only)
- **NOT allowed to bypass:**
  - Automated systems
  - External contributors
  - General developers

## Verification Commands

After configuration, verify with:

```bash
# Check if branch is protected
gh api repos/iQs-Group/zp42/branches/main/protection

# List required status checks
gh api repos/iQs-Group/zp42/branches/main/protection/required_status_checks

# List bypass actors
gh api repos/iQs-Group/zp42/rulesets
```

## Compensating Controls (Until Configured)

While branch protection is being configured:
1. Manual review of all commits to main
2. Pre-push hook enforcement (see `.git/hooks/pre-push`)
3. CI validation on all branches
4. Manual verification that no direct pushes occur

## Implementation Blocker

**Action Required:** Repository owner must configure branch protection.

**Automation cannot:**
- Access repository settings
- Create rulesets
- Configure branch protection
- Grant itself permissions

**Automation can:**
- Document requirements (this file)
- Test against protection once enabled
- Enforce via pre-push hooks (see Section E compensating controls)
