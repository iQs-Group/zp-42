# ZP42 Branch Protection Requirements

This document specifies the required branch protection rules for the ZP42 repository.

## Main Branch Protection

The `main` branch must be protected with the following settings:

### Required Status Checks

Before merging to `main`, the following checks must pass:

1. **Gitleaks Secret Scan** - No secrets detected
2. **Prohibited Terms Scan** - No blocking violations
3. **Python Compilation** - All modules compile successfully
4. **Test Suite** - All tests pass (pytest)
5. **Code Quality** - Ruff linting passes
6. **Type Checking** - Mypy passes (or warnings only)
7. **Security Scan** - Bandit security scan passes (medium/high severity)
8. **Coverage** - Test coverage >= 80%

### Pull Request Requirements

- **Require pull request reviews before merging**: Enabled
  - Required approvals: 1
  - Dismiss stale pull request approvals when new commits are pushed: Enabled
  - Require review from Code Owners: Enabled (when CODEOWNERS file exists)

- **Require status checks to pass before merging**: Enabled
  - Require branches to be up to date before merging: Enabled
  - Status checks that are required (see above)

- **Require conversation resolution before merging**: Enabled

### Additional Protections

- **Require signed commits**: Recommended (not enforced by default)
- **Require linear history**: Enabled
  - This prevents merge commits and requires rebase or squash merging

- **Include administrators**: Disabled
  - Administrators can override protections in emergency situations

- **Restrict who can push to matching branches**: Enabled
  - Only designated maintainers can push directly to main (emergency only)

- **Allow force pushes**: Disabled
  - Force pushes to main are never permitted

- **Allow deletions**: Disabled
  - The main branch cannot be deleted

## Feature Branch Guidelines

Feature branches (e.g., `feature/*`, `security/*`, `fix/*`) should follow these guidelines:

- Branch from `main`
- Keep branches short-lived (merge within 1 week if possible)
- Squash commits when merging to keep main history clean
- Delete branch after merge

## Emergency Procedures

In case of emergency (e.g., security incident, production outage):

1. Create an emergency branch from `main`
2. Apply the critical fix
3. Create PR with `[EMERGENCY]` prefix in title
4. Request immediate review from available maintainer
5. Merge with administrator override if necessary
6. Document the emergency procedure in post-incident review

## Enforcement

Branch protection rules are enforced at the GitHub repository level. To configure:

1. Go to repository Settings
2. Navigate to Branches section
3. Add or edit branch protection rule for `main`
4. Apply the settings specified above

## Compensating Controls

If branch protection cannot be enabled at the repository level:

1. **Manual Review**: All PRs must be reviewed by at least one other developer
2. **Pre-merge Checklist**: Use PR template with mandatory checklist
3. **Post-merge Audit**: Review all main branch commits weekly
4. **Rollback Plan**: Maintain rollback procedure for each merge

## Validation

To validate branch protection is correctly configured:

```bash
# Check if main branch is protected (requires GitHub CLI)
gh api repos/:owner/:repo/branches/main/protection | jq .

# Verify required status checks
gh api repos/:owner/:repo/branches/main/protection/required_status_checks | jq .
```

---

**Document Version**: Foundation PR T001  
**Last Updated**: 2026-05-18  
**Owner**: ZP42 Development Team
