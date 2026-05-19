#!/usr/bin/env bash
# Secret Kill Switch - Blocks commands containing credential patterns
# Returns: 0 if allowed, 1 if blocked

set -euo pipefail

COMMAND="${1:-}"

if [[ -z "$COMMAND" ]]; then
    echo '{"status": "ERROR", "reason": "No command provided", "matched_rule": "none", "secret_value_printed": false}'
    exit 1
fi

# Blocked patterns
declare -A BLOCKED_PATTERNS=(
    ["github_pat_"]="GitHub Personal Access Token pattern"
    ["x-access-token"]="Git credential URL pattern"
    ["Authorization: token"]="Authorization header with token"
    ["Authorization: Bearer"]="Authorization header with bearer token"
    ["TOKEN="]="Environment variable token assignment"
    ["GH_TOKEN="]="GitHub token environment variable"
    ["GITHUB_TOKEN="]="GitHub token environment variable"
    ["cat.*secret"]="Reading secret file with cat"
    ["tail.*secret"]="Reading secret file with tail"
    ["less.*secret"]="Reading secret file with less"
    ["more.*secret"]="Reading secret file with more"
    ["printenv"]="Printing all environment variables"
    ["^env$"]="Printing all environment variables"
    ["/auth_secrets"]="Accessing auth secrets file"
    [".config.*secret"]="Accessing config secret file"
    ["git remote set-url.*x-access-token"]="Setting git remote with token"
    ["curl.*Authorization"]="Curl with Authorization header"
    ["gh auth token"]="GitHub CLI token retrieval"
    ["python.*print.*token"]="Python printing token"
    ["jq.*token"]="JQ processing token"
    ["grep.*token"]="Grepping for token"
)

# Check each pattern
for pattern in "${!BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        cat <<EOF
{
  "status": "BLOCKED",
  "reason": "${BLOCKED_PATTERNS[$pattern]}",
  "matched_rule": "$pattern",
  "secret_value_printed": false
}
EOF
        exit 1
    fi
done

# Command is allowed
cat <<EOF
{
  "status": "ALLOWED",
  "reason": "No blocked patterns detected",
  "matched_rule": "none",
  "secret_value_printed": false
}
EOF
exit 0
