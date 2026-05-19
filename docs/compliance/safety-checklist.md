# ZP42 Safety Checklist

This checklist must be completed for every pull request to ensure compliance with ZP42 safety and security requirements.

## PR Information

- **PR Title**: _____________________________________________________
- **PR Number**: #______
- **Author**: _____________________________________________________
- **Reviewer**: _____________________________________________________
- **Date**: _____________________________________________________

---

## 1. Secret Scanning

- [ ] **Gitleaks scan passes** (exit code 0)
- [ ] **No secrets in commit history** (checked with `git log -p | grep -i "github_pat_"`)
- [ ] **No secrets in tracked files** (checked with `git grep` for common patterns)
- [ ] **No auth files committed** (no `.env`, `*_token`, `*_secret`, etc.)
- [ ] **No credentials in code comments** (reviewed manually)

**Notes**: _________________________________________________________________

---

## 2. Prohibited Terms Scanning

- [ ] **Scanner passes** (exit code 0, no blocking violations)
- [ ] **No internal codenames in repo files** (checked production code and docs)
- [ ] **No blocked public terms in docs** (verified against prohibited terms list)
- [ ] **No blocked public terms in production code** (checked all .py files)
- [ ] **No explicit PRC model names in public docs** (use category language instead)

**Blocking violations found**: ______ (must be 0)  
**Allowlisted violations**: ______ (informational only)

**Notes**: _________________________________________________________________

---

## 3. Code Quality

- [ ] **Python compilation passes** (`python -m compileall .`)
- [ ] **Ruff linting passes** (`ruff check .`)
- [ ] **Mypy type checking passes or warnings only** (`mypy . --strict`)
- [ ] **All tests pass** (`pytest -q`)
- [ ] **Test coverage >= 80%** (`pytest --cov=. --cov-fail-under=80`)
- [ ] **Bandit security scan passes** (`bandit -r . -ll`)

**Test results**: ______ passed, ______ failed  
**Coverage**: ______%

**Notes**: _________________________________________________________________

---

## 4. Model Safety

- [ ] **No model downloads** (no calls to HuggingFace, model registries, etc.)
- [ ] **No model training code** (no optimizer, no training loops, no gradient computation)
- [ ] **No model inference** (no model.forward(), no model.generate(), etc.)
- [ ] **No model weights committed** (no .bin, .safetensors, .ckpt files)
- [ ] **Only approved models referenced** (AI2 OLMo 3, IBM Granite 4.1)
- [ ] **No PRC-origin models used** (checked against exclusion list)

**Models referenced**: _____________________________________________________

**Notes**: _________________________________________________________________

---

## 5. Cloud Resources

- [ ] **No cloud resources provisioned** (no AWS, Azure, GCP, etc.)
- [ ] **No infrastructure-as-code** (no Terraform, CloudFormation, etc.)
- [ ] **No container deployment** (no Dockerfiles, kubernetes manifests)
- [ ] **No serverless functions** (no Lambda, Cloud Functions, etc.)
- [ ] **No cloud storage access** (no S3, Blob Storage, etc.)

**Notes**: _________________________________________________________________

---

## 6. Offensive Code

- [ ] **No malware creation** (checked all capability implementations)
- [ ] **No credential theft** (no password harvesting, keylogging, etc.)
- [ ] **No DDoS code** (no flood generators, no amplification attacks)
- [ ] **No data exfiltration** (no unauthorized data extraction)
- [ ] **No persistence mechanisms** (no backdoors, no rootkits)
- [ ] **No evasion techniques** (no anti-debugging, no obfuscation)
- [ ] **No destructive payloads** (no file deletion, no disk wiping)
- [ ] **No exploit code** (no buffer overflows, no RCE, no privilege escalation)
- [ ] **No live targeting** (no third-party system attacks)

**Notes**: _________________________________________________________________

---

## 7. Telemetry and Tracking

- [ ] **No telemetry added** (no analytics, no tracking pixels)
- [ ] **No phone-home behavior** (no unauthorized external network calls)
- [ ] **No usage metrics collection** (unless explicitly authorized)
- [ ] **No user tracking** (no fingerprinting, no session recording)
- [ ] **No third-party integrations** (unless approved and documented)

**Notes**: _________________________________________________________________

---

## 8. Authorization and Gates

- [ ] **All gates fail closed** (checked all validation functions)
- [ ] **Lane authorization required** (all operations check lane)
- [ ] **Human gates implemented** (for Lane B and C operations)
- [ ] **No autonomous escalation** (lane changes require explicit approval)
- [ ] **ROE checks enforced** (all capabilities check against ROE)

**Notes**: _________________________________________________________________

---

## 9. Audit and Logging

- [ ] **All operations logged** (checked audit_logger calls)
- [ ] **Timestamps in ISO-8601 UTC** (verified log format)
- [ ] **Log format is JSONL** (append-only JSON lines)
- [ ] **Policy violations logged** (failed operations recorded)
- [ ] **Escalation attempts logged** (unauthorized lane changes recorded)

**Notes**: _________________________________________________________________

---

## 10. Documentation

- [ ] **Public terminology correct** (defensive, active-defense, sovereign-authorized)
- [ ] **No internal codenames** (checked all docs)
- [ ] **Model policy documented** (allowlist and exclusions clear)
- [ ] **Safety boundaries documented** (lanes, gates, prohibitions)
- [ ] **License notice present** (proprietary license declared)

**Notes**: _________________________________________________________________

---

## 11. Git History

- [ ] **No force-push to main** (verified git reflog)
- [ ] **No history rewrite** (no rebase of main, no commit --amend on main)
- [ ] **Linear history maintained** (no merge commits or fast-forward only)
- [ ] **Commit messages clean** (no secrets, no internal names)
- [ ] **Branch name appropriate** (no internal codenames)

**Notes**: _________________________________________________________________

---

## 12. Pull Request

- [ ] **PR title appropriate** (no internal codenames, no blocked terms)
- [ ] **PR body appropriate** (no secrets, no internal names)
- [ ] **Files changed reviewed** (all changes necessary and safe)
- [ ] **No unrelated changes** (scope limited to PR objective)
- [ ] **Breaking changes documented** (if any)

**Files changed**: ______  
**Lines added**: ______  
**Lines deleted**: ______

**Notes**: _________________________________________________________________

---

## Final Approval

### Pre-merge Checklist

- [ ] **All items above checked**
- [ ] **All required checks pass**
- [ ] **No blocking issues remain**
- [ ] **Reviewer approval received**
- [ ] **Ready to merge**

### Merge Recommendation

**Status**: [ ] MERGE APPROVED [ ] DO NOT MERGE

**Reviewer Signature**: _____________________________________________________

**Date**: _____________________________________________________

**Additional Notes**:

_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________

---

## Post-Merge Verification

After merging to main:

- [ ] **Main branch builds successfully**
- [ ] **All CI/CD checks pass on main**
- [ ] **No regressions detected**
- [ ] **Documentation updated** (if applicable)
- [ ] **Feature branch deleted**

**Post-merge verification completed by**: _____________________________________

**Date**: _____________________________________________________

---

**Document Version**: Foundation PR T001  
**Last Updated**: 2026-05-18  
**Owner**: ZP42 Development Team
