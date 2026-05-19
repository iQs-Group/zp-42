#!/usr/bin/env python3
"""
ZP42 Prohibited Terms Scanner

Scans repository for prohibited internal names, third-party AI/tool names,
PRC model names, and reckless public terms.

Foundation PR #1: Ensures clean public positioning.
Supports allowlist system for scanner source code and test fixtures.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Set, Tuple


class ProhibitedTermsScanner:
    """Scanner for prohibited terms in repository files."""

    # Terms that must never appear in repo files
    PROHIBITED_INTERNAL_NAMES = {
        # Redacted internal project names - replaced with placeholder
        "internal_codename_placeholder",
    }

    # Third-party AI/tool names (do not reference in repo)
    PROHIBITED_THIRD_PARTY_NAMES = {
        "chatgpt",
        "gpt-4",
        "claude",
        "anthropic",
        "gemini",
        "bard",
        "copilot",
        "midjourney",
        "stable diffusion",
        "dalle",
        "dall-e",
    }

    # PRC-origin model names
    PROHIBITED_PRC_MODEL_NAMES = {
        "qwen",
        "deepseek",
        "kimi",
        "glm",
        "chatglm",
        "minimax",
        "ernie",
        "baidu",
        "alibaba cloud",
        "moonshot",
        "zhipu",
    }

    # Reckless public terms
    PROHIBITED_PUBLIC_TERMS = {
        "hack-back",
        "hack back",
        "retaliation",
        "punishment",
        "revenge",
        "50/50 offensive",
        "private offensive action",
        "autonomous hack",
        "unauthorized access",
    }

    # File extensions to scan
    SCANNABLE_EXTENSIONS = {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".sh",
        ".rst",
    }

    # Directories to skip
    SKIP_DIRECTORIES = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        "venv",
        "env",
        ".venv",
        "build",
        "dist",
    }

    def __init__(self, root_path: Path, allowlist_path: Path | None = None):
        """
        Initialize scanner.

        Args:
            root_path: Root directory to scan
            allowlist_path: Path to allowlist JSON file (optional)
        """
        self.root_path = Path(root_path).resolve()
        self.violations: List[Tuple[Path, int, str, str]] = []
        self.allowlisted_files: Set[str] = set()
        
        # Load allowlist if provided
        if allowlist_path and allowlist_path.exists():
            self._load_allowlist(allowlist_path)

    def _load_allowlist(self, allowlist_path: Path):
        """Load allowlist from JSON file."""
        try:
            with open(allowlist_path, "r", encoding="utf-8") as f:
                allowlist_data = json.load(f)
                self.allowlisted_files = set(allowlist_data.get("allowlisted_files", []))
        except Exception as e:
            print(
                f"Warning: Could not load allowlist from {allowlist_path}: {e}",
                file=sys.stderr,
            )

    def scan(self) -> Tuple[int, int]:
        """
        Scan repository for prohibited terms.

        Returns:
            Tuple of (blocking_violations, allowlisted_violations)
        """
        self.violations = []

        for file_path in self._iter_files():
            self._scan_file(file_path)

        # Separate blocking vs allowlisted violations
        blocking = []
        allowlisted = []
        
        for violation in self.violations:
            file_path, line_num, term, category = violation
            relative_path = str(file_path.relative_to(self.root_path))
            
            if relative_path in self.allowlisted_files:
                allowlisted.append(violation)
            else:
                blocking.append(violation)
        
        return len(blocking), len(allowlisted)

    def get_blocking_violations(self) -> List[Tuple[Path, int, str, str]]:
        """Get only blocking (non-allowlisted) violations."""
        blocking = []
        for violation in self.violations:
            file_path, line_num, term, category = violation
            relative_path = str(file_path.relative_to(self.root_path))
            if relative_path not in self.allowlisted_files:
                blocking.append(violation)
        return blocking

    def get_allowlisted_violations(self) -> List[Tuple[Path, int, str, str]]:
        """Get only allowlisted violations."""
        allowlisted = []
        for violation in self.violations:
            file_path, line_num, term, category = violation
            relative_path = str(file_path.relative_to(self.root_path))
            if relative_path in self.allowlisted_files:
                allowlisted.append(violation)
        return allowlisted

    def _iter_files(self):
        """Iterate over scannable files."""
        for path in self.root_path.rglob("*"):
            # Skip directories
            if path.is_dir():
                continue

            # Skip if in excluded directory
            if any(skip in path.parts for skip in self.SKIP_DIRECTORIES):
                continue

            # Check extension
            if path.suffix.lower() in self.SCANNABLE_EXTENSIONS:
                yield path

    def _scan_file(self, file_path: Path):
        """Scan a single file for prohibited terms."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, start=1):
                    line_lower = line.lower()

                    # Check each category of prohibited terms
                    for term in self.PROHIBITED_INTERNAL_NAMES:
                        if term.lower() in line_lower:
                            self.violations.append(
                                (
                                    file_path,
                                    line_num,
                                    term,
                                    "prohibited_internal_name",
                                )
                            )

                    for term in self.PROHIBITED_THIRD_PARTY_NAMES:
                        if term.lower() in line_lower:
                            self.violations.append(
                                (
                                    file_path,
                                    line_num,
                                    term,
                                    "prohibited_third_party_name",
                                )
                            )

                    for term in self.PROHIBITED_PRC_MODEL_NAMES:
                        if term.lower() in line_lower:
                            self.violations.append(
                                (
                                    file_path,
                                    line_num,
                                    term,
                                    "prohibited_prc_model_name",
                                )
                            )

                    for term in self.PROHIBITED_PUBLIC_TERMS:
                        if term.lower() in line_lower:
                            self.violations.append(
                                (
                                    file_path,
                                    line_num,
                                    term,
                                    "prohibited_public_term",
                                )
                            )

        except Exception as e:
            # Log error but continue scanning
            print(
                f"Warning: Could not scan {file_path}: {e}",
                file=sys.stderr,
            )

    def report_violations(self) -> str:
        """
        Generate human-readable violation report.

        Returns:
            Formatted report string
        """
        blocking = self.get_blocking_violations()
        allowlisted = self.get_allowlisted_violations()
        
        report_lines = []
        
        # Report blocking violations
        if blocking:
            report_lines.append(f"✗ Found {len(blocking)} BLOCKING violation(s):\n")
            
            # Group by file type
            public_doc_violations = []
            production_code_violations = []
            other_violations = []
            
            for file_path, line_num, term, category in sorted(blocking):
                relative_path = file_path.relative_to(self.root_path)
                violation_str = f"  {relative_path}:{line_num} - '{term}' ({category})"
                
                if str(relative_path).startswith("docs/"):
                    public_doc_violations.append(violation_str)
                elif str(relative_path).endswith(".py") and not str(relative_path).startswith("tests/"):
                    production_code_violations.append(violation_str)
                else:
                    other_violations.append(violation_str)
            
            if production_code_violations:
                report_lines.append("\nPRODUCTION CODE VIOLATIONS (" + str(len(production_code_violations)) + "):")
                report_lines.extend(production_code_violations)
            
            if public_doc_violations:
                report_lines.append("\nPUBLIC DOCUMENTATION VIOLATIONS (" + str(len(public_doc_violations)) + "):")
                report_lines.extend(public_doc_violations)
            
            if other_violations:
                report_lines.append("\nOTHER VIOLATIONS (" + str(len(other_violations)) + "):")
                report_lines.extend(other_violations)
            
            report_lines.append("\n❌ SCAN FAILED: Blocking violations must be removed before commit.\n")
        
        # Report allowlisted violations (informational only)
        if allowlisted:
            report_lines.append(f"\nℹ  Found {len(allowlisted)} allowlisted violation(s) (informational only):")
            
            # Show first 10 allowlisted violations
            for file_path, line_num, term, category in sorted(allowlisted)[:10]:
                relative_path = file_path.relative_to(self.root_path)
                report_lines.append(f"  {relative_path}:{line_num} - '{term}' ({category})")
            
            if len(allowlisted) > 10:
                report_lines.append(f"  ... and {len(allowlisted) - 10} more")
            
            report_lines.append("")
        
        # Final status
        if not blocking:
            report_lines.append("✓ SCAN PASSED: No blocking violations found.\n")
        
        return "\n".join(report_lines)

    def report_json(self) -> dict:
        """
        Generate JSON violation report.

        Returns:
            Violations dictionary
        """
        blocking = self.get_blocking_violations()
        allowlisted = self.get_allowlisted_violations()
        
        return {
            "status": "failed" if blocking else "passed",
            "blocking_violation_count": len(blocking),
            "allowlisted_violation_count": len(allowlisted),
            "blocking_violations": [
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": line_num,
                    "term": term,
                    "category": category,
                }
                for file_path, line_num, term, category in blocking
            ],
            "allowlisted_violations": [
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": line_num,
                    "term": term,
                    "category": category,
                }
                for file_path, line_num, term, category in allowlisted
            ],
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scan repository for prohibited terms"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=Path("compliance/scanner_allowlist.json"),
        help="Path to allowlist file (default: compliance/scanner_allowlist.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output violations in JSON format",
    )

    args = parser.parse_args()

    scanner = ProhibitedTermsScanner(args.root, args.allowlist)
    blocking_count, allowlisted_count = scanner.scan()

    if args.json:
        print(json.dumps(scanner.report_json(), indent=2))
    else:
        print(scanner.report_violations())

    # Exit with error code if blocking violations found
    # Allowlisted violations are informational only and don't fail the scan
    sys.exit(1 if blocking_count > 0 else 0)


if __name__ == "__main__":
    main()
