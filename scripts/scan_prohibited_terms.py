#!/usr/bin/env python3
"""
ZP42 Prohibited Terms Scanner

Scans repository for prohibited internal names, third-party AI/tool names,
PRC model names, and reckless public terms.

Foundation PR #1: Ensures clean public positioning.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Set, Tuple, Dict, Any


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

    # Production code patterns (strict enforcement)
    PRODUCTION_CODE_PATTERNS = {
        "core/",
        "orchestrator/",
        "governance/",
        "verifiers/",
    }

    # Public documentation patterns (strict enforcement)
    PUBLIC_DOC_PATTERNS = {
        "README.md",
        "docs/FOUNDATION.md",
        "docs/API.md",
        "docs/USAGE.md",
    }

    def __init__(self, root_path: Path, allowlist_path: Path = None):
        """
        Initialize scanner.

        Args:
            root_path: Root directory to scan
            allowlist_path: Path to allowlist JSON file
        """
        self.root_path = Path(root_path).resolve()
        self.violations: List[Tuple[Path, int, str, str]] = []
        self.allowlist = self._load_allowlist(allowlist_path)

    def _load_allowlist(self, allowlist_path: Path = None) -> Dict[str, Any]:
        """Load allowlist configuration."""
        if allowlist_path is None:
            # Default path
            allowlist_path = self.root_path / "compliance" / "scanner_allowlist.json"

        if not allowlist_path.exists():
            return {"allowlist": []}

        try:
            with open(allowlist_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load allowlist: {e}", file=sys.stderr)
            return {"allowlist": []}

    def _is_allowlisted(self, file_path: Path) -> bool:
        """Check if a file is in the allowlist."""
        relative_path = str(file_path.relative_to(self.root_path))

        for allowed_item in self.allowlist.get("allowlist", []):
            pattern = allowed_item.get("file_pattern", "")
            if pattern in relative_path or relative_path == pattern:
                return True

        return False

    def _is_production_code(self, file_path: Path) -> bool:
        """Check if file is production code (strict enforcement)."""
        relative_path = str(file_path.relative_to(self.root_path))

        for pattern in self.PRODUCTION_CODE_PATTERNS:
            if relative_path.startswith(pattern):
                return True

        return False

    def _is_public_doc(self, file_path: Path) -> bool:
        """Check if file is public documentation (strict enforcement)."""
        relative_path = str(file_path.relative_to(self.root_path))

        for pattern in self.PUBLIC_DOC_PATTERNS:
            if pattern in relative_path or relative_path == pattern:
                return True

        return False

    def scan(self) -> Dict[str, int]:
        """
        Scan repository for prohibited terms.

        Returns:
            Dictionary with violation counts by category
        """
        self.violations = []

        for file_path in self._iter_files():
            self._scan_file(file_path)

        # Categorize violations
        production_violations = []
        public_doc_violations = []
        allowlisted_violations = []

        for file_path, line_num, term, category in self.violations:
            if self._is_allowlisted(file_path):
                allowlisted_violations.append((file_path, line_num, term, category))
            elif self._is_production_code(file_path):
                production_violations.append((file_path, line_num, term, category))
            elif self._is_public_doc(file_path):
                public_doc_violations.append((file_path, line_num, term, category))
            else:
                # Other files (internal docs, etc.) - less strict
                allowlisted_violations.append((file_path, line_num, term, category))

        return {
            "total": len(self.violations),
            "production_code": len(production_violations),
            "public_docs": len(public_doc_violations),
            "allowlisted": len(allowlisted_violations),
            "blocking": len(production_violations) + len(public_doc_violations),
        }

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

    def report_violations(self, counts: Dict[str, int]) -> str:
        """
        Generate human-readable violation report.

        Args:
            counts: Violation counts by category

        Returns:
            Formatted report string
        """
        if not self.violations:
            return "✓ No prohibited terms found.\n"

        # Categorize for reporting
        production_violations = []
        public_doc_violations = []
        allowlisted_violations = []

        for file_path, line_num, term, category in self.violations:
            if self._is_allowlisted(file_path):
                allowlisted_violations.append((file_path, line_num, term, category))
            elif self._is_production_code(file_path):
                production_violations.append((file_path, line_num, term, category))
            elif self._is_public_doc(file_path):
                public_doc_violations.append((file_path, line_num, term, category))
            else:
                allowlisted_violations.append((file_path, line_num, term, category))

        report_lines = []

        # Report blocking violations (production + public docs)
        blocking_count = counts["blocking"]
        if blocking_count > 0:
            report_lines.append(f"✗ Found {blocking_count} BLOCKING violation(s):\n")

            if production_violations:
                report_lines.append(f"PRODUCTION CODE VIOLATIONS ({len(production_violations)}):")
                for file_path, line_num, term, category in sorted(production_violations):
                    relative_path = file_path.relative_to(self.root_path)
                    report_lines.append(
                        f"  {relative_path}:{line_num} - '{term}' ({category})"
                    )
                report_lines.append("")

            if public_doc_violations:
                report_lines.append(f"PUBLIC DOCUMENTATION VIOLATIONS ({len(public_doc_violations)}):")
                for file_path, line_num, term, category in sorted(public_doc_violations):
                    relative_path = file_path.relative_to(self.root_path)
                    report_lines.append(
                        f"  {relative_path}:{line_num} - '{term}' ({category})"
                    )
                report_lines.append("")

            report_lines.append("❌ SCAN FAILED: Blocking violations must be removed before commit.\n")

        # Report allowlisted violations (informational only)
        if allowlisted_violations:
            report_lines.append(f"ℹ  Found {len(allowlisted_violations)} allowlisted violation(s) (informational only):")
            for file_path, line_num, term, category in sorted(allowlisted_violations)[:10]:
                relative_path = file_path.relative_to(self.root_path)
                report_lines.append(
                    f"  {relative_path}:{line_num} - '{term}' ({category})"
                )
            if len(allowlisted_violations) > 10:
                report_lines.append(f"  ... and {len(allowlisted_violations) - 10} more")
            report_lines.append("")

        if blocking_count == 0:
            report_lines.append("✓ SCAN PASSED: No blocking violations found.\n")

        return "\n".join(report_lines)

    def report_json(self, counts: Dict[str, int]) -> dict:
        """
        Generate JSON violation report.

        Args:
            counts: Violation counts by category

        Returns:
            Violations dictionary
        """
        # Categorize for JSON report
        production_violations = []
        public_doc_violations = []
        allowlisted_violations = []

        for file_path, line_num, term, category in self.violations:
            violation_dict = {
                "file": str(file_path.relative_to(self.root_path)),
                "line": line_num,
                "term": term,
                "category": category,
            }

            if self._is_allowlisted(file_path):
                allowlisted_violations.append(violation_dict)
            elif self._is_production_code(file_path):
                production_violations.append(violation_dict)
            elif self._is_public_doc(file_path):
                public_doc_violations.append(violation_dict)
            else:
                allowlisted_violations.append(violation_dict)

        return {
            "status": "failed" if counts["blocking"] > 0 else "passed",
            "summary": counts,
            "blocking_violations": {
                "production_code": production_violations,
                "public_docs": public_doc_violations,
            },
            "allowlisted_violations": allowlisted_violations,
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
        "--json",
        action="store_true",
        help="Output violations in JSON format",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        help="Path to allowlist JSON file (default: compliance/scanner_allowlist.json)",
    )

    args = parser.parse_args()

    scanner = ProhibitedTermsScanner(args.root, args.allowlist)
    counts = scanner.scan()

    if args.json:
        import json

        print(json.dumps(scanner.report_json(counts), indent=2))
    else:
        print(scanner.report_violations(counts))

    # Exit with error code if BLOCKING violations found
    # (production code or public docs violations)
    sys.exit(1 if counts["blocking"] > 0 else 0)


if __name__ == "__main__":
    main()
