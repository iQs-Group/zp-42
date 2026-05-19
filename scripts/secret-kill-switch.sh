#!/bin/bash
#
# ZP42 Secret Kill Switch
# Command-level secret exposure prevention guard
#
# Blocks shell commands that may expose credentials, tokens, or auth material.
# This script is designed to be sourced in interactive shells or CI/CD environments.
#
# Usage:
#   source scripts/secret-kill-switch.sh
#
# Foundation PR #1: Prevents accidental secret exposure in shell commands

set -euo pipefail

# Blocked patterns (command substrings that indicate potential secret exposure)
declare -A BLOCKED_PATTERNS=(
    ["github_pat_"]="GitHub Personal Access Token pattern"
    ["x-access-token"]="Git credential URL pattern"
    ["Authorization: token"]="Authorization header with token"
    ["Authorization: Bearer"]="Authorization header with bearer token"
    ["export.*TOKEN"]="Environment variable token export"
    ["export.*SECRET"]="Environment variable secret export"
    ["export.*KEY"]="Environment variable key export"
    ["export.*PASSWORD"]="Environment variable password export"
    ["echo.*github_pat_"]="Echoing GitHub PAT"
    ["echo.*TOKEN"]="Echoing token variable"
    ["echo.*SECRET"]="Echoing secret variable"
    ["echo.*PASSWORD"]="Echoing password variable"
    ["cat.*auth"]="Reading auth file"
    ["cat.*secret"]="Reading secret file"
    ["cat.*token"]="Reading token file"
    ["tail.*auth"]="Tailing auth file"
    ["tail.*secret"]="Tailing secret file"
    ["/auth_secrets"]="Accessing auth secrets file"
    [".config.*secret"]="Accessing config secret file"
    ["git remote set-url.*x-access-token"]="Setting git remote with token"
    ["curl.*Authorization"]="Curl with Authorization header"
    ["gh auth token"]="GitHub CLI token retrieval"
)

# Function to check command against blocked patterns
check_command() {
    local cmd="$1"
    
    for pattern in "${!BLOCKED_PATTERNS[@]}"; do
        if [[ "$cmd" =~ $pattern ]]; then
            echo "❌ BLOCKED: ${BLOCKED_PATTERNS[$pattern]}"
            echo "Command contains potentially sensitive pattern: $pattern"
            echo "Command: $cmd"
            echo ""
            echo "If this is a false positive, please update the allowlist."
            return 1
        fi
    done
    
    return 0
}

# Export function for use in subshells
export -f check_command

echo "✅ ZP42 Secret Kill Switch loaded"
echo "   Monitoring commands for credential exposure patterns"
