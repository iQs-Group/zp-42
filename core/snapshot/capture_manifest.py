"""
ZP42 Snapshot Manifest Capture

Captures manifests and checksums for local files and folders.
Foundation PR #1: Local file hashing only, no Hugging Face downloads.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional


class ManifestCapture:
    """
    Capture manifests with checksums for reproducibility and verification.

    Foundation PR #1: Local file/folder hashing only.
    Future PRs will add Hugging Face model manifest capture.
    """

    def __init__(self):
        pass

    def hash_file(self, file_path: Path, algorithm: str = "sha256") -> str:
        """
        Compute hash of a single file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, sha512)

        Returns:
            Hexadecimal hash digest

        Raises:
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        hasher = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()

    def capture_directory_manifest(
        self,
        directory_path: Path,
        output_manifest_path: Optional[Path] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict:
        """
        Capture manifest of all files in a directory.

        Args:
            directory_path: Path to directory
            output_manifest_path: Optional path to write manifest JSON
            include_patterns: Optional list of glob patterns to include
            exclude_patterns: Optional list of glob patterns to exclude

        Returns:
            Manifest dictionary with file paths and checksums
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not directory_path.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")

        manifest = {
            "manifest_version": "1.0.0",
            "directory": str(directory_path.resolve()),
            "algorithm": "sha256",
            "files": {},
        }

        # Get all files
        if include_patterns:
            files = []
            for pattern in include_patterns:
                files.extend(directory_path.rglob(pattern))
        else:
            files = list(directory_path.rglob("*"))

        # Filter out excluded patterns
        if exclude_patterns:
            excluded_files = set()
            for pattern in exclude_patterns:
                excluded_files.update(directory_path.rglob(pattern))
            files = [f for f in files if f not in excluded_files]

        # Hash each file
        for file_path in sorted(files):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(directory_path))
                try:
                    file_hash = self.hash_file(file_path)
                    manifest["files"][relative_path] = {
                        "sha256": file_hash,
                        "size_bytes": file_path.stat().st_size,
                    }
                except Exception as e:
                    # Log error but continue
                    manifest["files"][relative_path] = {
                        "error": str(e),
                    }

        # Write manifest if output path provided
        if output_manifest_path:
            output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, sort_keys=True)

        return manifest

    def verify_manifest(
        self, manifest_path: Path, directory_path: Optional[Path] = None
    ) -> Dict:
        """
        Verify files against a manifest.

        Args:
            manifest_path: Path to manifest JSON file
            directory_path: Optional directory path (uses manifest directory if not provided)

        Returns:
            Verification results dictionary with status and mismatches
        """
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if directory_path is None:
            directory_path = Path(manifest["directory"])

        verification = {
            "status": "verified",
            "mismatches": [],
            "missing_files": [],
            "extra_files": [],
        }

        # Check each file in manifest
        for relative_path, file_info in manifest["files"].items():
            file_path = directory_path / relative_path

            if not file_path.exists():
                verification["missing_files"].append(relative_path)
                verification["status"] = "failed"
                continue

            if "error" in file_info:
                # Skip files that had errors during capture
                continue

            # Verify hash
            try:
                current_hash = self.hash_file(file_path)
                if current_hash != file_info["sha256"]:
                    verification["mismatches"].append(
                        {
                            "file": relative_path,
                            "expected": file_info["sha256"],
                            "actual": current_hash,
                        }
                    )
                    verification["status"] = "failed"
            except Exception as e:
                verification["mismatches"].append(
                    {
                        "file": relative_path,
                        "error": str(e),
                    }
                )
                verification["status"] = "failed"

        return verification

    def capture_model_manifest_stub(self, model_identifier: str) -> Dict:
        """
        Stub for model manifest capture.

        Foundation PR #1: Does not download from Hugging Face.
        Returns metadata-only stub.

        Args:
            model_identifier: Model identifier (e.g., allenai/OLMo-3-32B)

        Returns:
            Stub manifest dictionary
        """
        return {
            "manifest_version": "1.0.0",
            "model_identifier": model_identifier,
            "status": "not_implemented",
            "note": "Model download not implemented in Foundation PR #1",
            "future_implementation": "Will support Hugging Face manifest capture in future PR",
        }
