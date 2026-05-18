#!/usr/bin/env python3
"""
ZP42 Prohibited Terms Scanner

Scans repository for prohibited internal names, third-party AI/tool names,
PRC model names, and reckless public terms.

Foundation PR #1: Ensures clean public positioning.
"""

import argparse
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

    def __init__(self, root_path: Path):
        """
        Initialize scanner.

        Args:
            root_path: Root directory to scan
        """
        self.root_path = Path(root_path).resolve()
        self.violations: List[Tuple[Path, int, str, str]] = []

    def scan(self) -> int:
        """
        Scan repository for prohibited terms.

        Returns:
            Number of violations found
        """
        self.violations = []

        for file_path in self._iter_files():
            self._scan_file(file_path)

        return len(self.violations)

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
        if not self.violations:
            return "✓ No prohibited terms found.\n"

        report_lines = [
            f"✗ Found {len(self.violations)} prohibited term violation(s):\n"
        ]

        for file_path, line_num, term, category in sorted(self.violations):
            relative_path = file_path.relative_to(self.root_path)
            report_lines.append(
                f"  {relative_path}:{line_num} - '{term}' ({category})"
            )

        report_lines.append(
            "\nProhibited terms must be removed before commit.\n"
        )

        return "\n".join(report_lines)

    def report_json(self) -> dict:
        """
        Generate JSON violation report.

        Returns:
            Violations dictionary
        """
        return {
            "status": "failed" if self.violations else "passed",
            "violation_count": len(self.violations),
            "violations": [
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": line_num,
                    "term": term,
                    "category": category,
                }
                for file_path, line_num, term, category in self.violations
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
        "--json",
        action="store_true",
        help="Output violations in JSON format",
    )

    args = parser.parse_args()

    scanner = ProhibitedTermsScanner(args.root)
    violation_count = scanner.scan()

    if args.json:
        import json

        print(json.dumps(scanner.report_json(), indent=2))
    else:
        print(scanner.report_violations())

    # Exit with error code if violations found
    sys.exit(1 if violation_count > 0 else 0)


if __name__ == "__main__":
    main()
