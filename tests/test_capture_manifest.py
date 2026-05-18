"""Tests for manifest capture."""

import tempfile
from pathlib import Path

import pytest

from core.snapshot.capture_manifest import ManifestCapture


def test_hash_file():
    """Test file hashing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Test content for hashing")
        temp_path = Path(f.name)

    try:
        capture = ManifestCapture()
        file_hash = capture.hash_file(temp_path)

        assert file_hash is not None
        assert len(file_hash) == 64  # SHA256 produces 64 hex chars
    finally:
        temp_path.unlink()


def test_hash_nonexistent_file_fails():
    """Test that hashing nonexistent file raises FileNotFoundError."""
    capture = ManifestCapture()

    with pytest.raises(FileNotFoundError):
        capture.hash_file(Path("/nonexistent/file.txt"))


def test_capture_directory_manifest():
    """Test capturing directory manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        (tmpdir_path / "file1.txt").write_text("Content 1")
        (tmpdir_path / "file2.txt").write_text("Content 2")
        (tmpdir_path / "subdir").mkdir()
        (tmpdir_path / "subdir" / "file3.txt").write_text("Content 3")

        capture = ManifestCapture()
        manifest = capture.capture_directory_manifest(tmpdir_path)

        assert manifest["manifest_version"] == "1.0.0"
        assert manifest["algorithm"] == "sha256"
        assert len(manifest["files"]) == 3
        assert "file1.txt" in manifest["files"]
        assert "file2.txt" in manifest["files"]
        assert "subdir/file3.txt" in manifest["files"]


def test_capture_directory_manifest_with_output():
    """Test capturing manifest and writing to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        (tmpdir_path / "test.txt").write_text("Test")

        output_path = tmpdir_path / "manifest.json"

        capture = ManifestCapture()
        capture.capture_directory_manifest(tmpdir_path, output_manifest_path=output_path)

        assert output_path.exists()


def test_verify_manifest_success():
    """Test successful manifest verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        (tmpdir_path / "file1.txt").write_text("Content")

        capture = ManifestCapture()
        manifest_path = tmpdir_path / "manifest.json"
        capture.capture_directory_manifest(
            tmpdir_path, output_manifest_path=manifest_path
        )

        verification = capture.verify_manifest(manifest_path, tmpdir_path)

        assert verification["status"] == "verified"
        assert len(verification["mismatches"]) == 0
        assert len(verification["missing_files"]) == 0


def test_verify_manifest_mismatch():
    """Test manifest verification with mismatch."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        file_path = tmpdir_path / "file1.txt"
        file_path.write_text("Original content")

        capture = ManifestCapture()
        manifest_path = tmpdir_path / "manifest.json"
        capture.capture_directory_manifest(
            tmpdir_path, output_manifest_path=manifest_path
        )

        # Modify file after manifest capture
        file_path.write_text("Modified content")

        verification = capture.verify_manifest(manifest_path, tmpdir_path)

        assert verification["status"] == "failed"
        assert len(verification["mismatches"]) == 1


def test_capture_model_manifest_stub():
    """Test model manifest stub (not implemented in Foundation PR #1)."""
    capture = ManifestCapture()
    manifest = capture.capture_model_manifest_stub("allenai/OLMo-3-32B")

    assert manifest["status"] == "not_implemented"
    assert manifest["model_identifier"] == "allenai/OLMo-3-32B"
