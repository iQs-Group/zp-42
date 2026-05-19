"""Tests for prohibited terms scanner."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scan_prohibited_terms import ProhibitedTermsScanner


def test_scanner_initialization():
    """Test scanner initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        scanner = ProhibitedTermsScanner(Path(tmpdir))
        assert scanner.root_path.exists()
        assert len(scanner.violations) == 0


def test_scanner_initialization_with_allowlist():
    """Test scanner initializes with allowlist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create allowlist file
        allowlist_file = tmpdir_path / "allowlist.json"
        allowlist_file.write_text(json.dumps({
            "allowlisted_files": ["test.py"]
        }))
        
        scanner = ProhibitedTermsScanner(tmpdir_path, allowlist_file)
        assert "test.py" in scanner.allowlisted_files


def test_scanner_clean_file():
    """Test scanner passes clean file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "clean.py"
        test_file.write_text("# This is a clean Python file\nprint('Hello ZP42')\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        blocking_count, allowlisted_count = scanner.scan()

        assert blocking_count == 0
        assert allowlisted_count == 0


def test_scanner_detects_prc_model_name():
    """Test scanner detects PRC model names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "bad.py"
        test_file.write_text("# Using Qwen model\nmodel = load_model('qwen-72b')\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        blocking_count, allowlisted_count = scanner.scan()

        assert blocking_count > 0
        blocking_violations = scanner.get_blocking_violations()
        assert any(
            "qwen" in violation[2].lower() and violation[3] == "prohibited_prc_model_name"
            for violation in blocking_violations
        )


def test_scanner_detects_third_party_name():
    """Test scanner detects third-party AI tool names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "bad.md"
        test_file.write_text("# Using ChatGPT\nWe used ChatGPT to generate this.\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        blocking_count, allowlisted_count = scanner.scan()

        assert blocking_count > 0
        blocking_violations = scanner.get_blocking_violations()
        assert any(
            "chatgpt" in violation[2].lower()
            and violation[3] == "prohibited_third_party_name"
            for violation in blocking_violations
        )


def test_scanner_detects_public_term():
    """Test scanner detects prohibited public terms."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "bad.txt"
        test_file.write_text("We will implement hack-back capabilities.\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        blocking_count, allowlisted_count = scanner.scan()

        assert blocking_count > 0
        blocking_violations = scanner.get_blocking_violations()
        assert any(
            "hack-back" in violation[2].lower() and violation[3] == "prohibited_public_term"
            for violation in blocking_violations
        )


def test_scanner_allowlist_functionality():
    """Test scanner allowlist functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a file with violations
        test_file = tmpdir_path / "scanner.py"
        test_file.write_text("# Scanner source: qwen\n")
        
        # Create allowlist
        allowlist_file = tmpdir_path / "allowlist.json"
        allowlist_file.write_text(json.dumps({
            "allowlisted_files": ["scanner.py"]
        }))
        
        scanner = ProhibitedTermsScanner(tmpdir_path, allowlist_file)
        blocking_count, allowlisted_count = scanner.scan()
        
        # Should be allowlisted, not blocking
        assert blocking_count == 0
        assert allowlisted_count > 0


def test_scanner_skips_directories():
    """Test scanner skips excluded directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create file in excluded directory
        excluded_dir = tmpdir_path / "__pycache__"
        excluded_dir.mkdir()
        (excluded_dir / "bad.py").write_text("# Contains chatgpt reference\n")

        # Create clean file in scanned location
        (tmpdir_path / "clean.py").write_text("# Clean file\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        blocking_count, allowlisted_count = scanner.scan()

        # Should not detect violation in __pycache__
        assert blocking_count == 0


def test_scanner_report_json():
    """Test JSON report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "bad.py"
        test_file.write_text("# Using qwen model\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        scanner.scan()

        report = scanner.report_json()

        assert report["status"] == "failed"
        assert report["blocking_violation_count"] > 0
        assert len(report["blocking_violations"]) > 0
        assert report["blocking_violations"][0]["category"] == "prohibited_prc_model_name"


def test_scanner_report_violations_clean():
    """Test human-readable report for clean files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "clean.py"
        test_file.write_text("# Clean file\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        scanner.scan()

        report = scanner.report_violations()

        assert "SCAN PASSED" in report


def test_scanner_report_violations_with_blocking():
    """Test human-readable report with blocking violations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "bad.py"
        test_file.write_text("# Using qwen\n")

        scanner = ProhibitedTermsScanner(tmpdir_path)
        scanner.scan()

        report = scanner.report_violations()

        assert "BLOCKING violation" in report
        assert "SCAN FAILED" in report


def test_scanner_multiple_violations():
    """Test scanner detects multiple violations in one file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        test_file = tmpdir_path / "bad.py"
        test_file.write_text(
            "# Using ChatGPT and Qwen\n"
            "model1 = 'chatgpt'\n"
            "model2 = 'qwen-72b'\n"
        )

        scanner = ProhibitedTermsScanner(tmpdir_path)
        blocking_count, allowlisted_count = scanner.scan()

        assert blocking_count >= 2
