"""Tests for lane policy engine."""

import tempfile
from pathlib import Path

import pytest

from governance.audit_logger import AuditLogger
from orchestrator.lanes.lane_policy import Lane, LanePolicy


def test_assign_lane_defensive():
    """Test assignment to Lane A (defensive)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        lane = policy.assign_lane(
            operation_description="Vulnerability assessment of customer system",
            authorization_reference="CUST-AUTH-001",
        )

        assert lane == Lane.A


def test_assign_lane_active_defense():
    """Test assignment to Lane B (active-defense)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        lane = policy.assign_lane(
            operation_description="Deploy honeypot for threat detection",
            authorization_reference="AUTH-2026-05-18-001",
        )

        assert lane == Lane.B


def test_assign_lane_sovereign():
    """Test assignment to Lane C (sovereign-authorized)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        lane = policy.assign_lane(
            operation_description="Sovereign-authorized operation",
            authorization_reference="SOV-AUTH-001",
            sovereign_authorization=True,
            human_signoff=True,
        )

        assert lane == Lane.C


def test_assign_lane_no_authorization_fails():
    """Test that missing authorization fails closed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        with pytest.raises(ValueError, match="Authorization reference required"):
            policy.assign_lane(
                operation_description="Some operation",
                authorization_reference=None,
            )


def test_assign_lane_sovereign_without_human_signoff_fails():
    """Test that sovereign auth without human signoff fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        with pytest.raises(
            ValueError, match="Lane C requires both sovereign authorization AND human signoff"
        ):
            policy.assign_lane(
                operation_description="Sovereign operation",
                authorization_reference="SOV-AUTH-001",
                sovereign_authorization=True,
                human_signoff=False,
            )


def test_assign_lane_active_defense_invalid_auth_fails():
    """Test that active-defense with invalid auth format fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        with pytest.raises(ValueError, match="Active-defense operations require written authorization"):
            policy.assign_lane(
                operation_description="Deploy honeypot for threat detection",
                authorization_reference="SHORT",  # Too short
            )


def test_validate_lane_authorization():
    """Test lane authorization validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        assert policy.validate_lane_authorization(
            lane=Lane.A, authorization_reference="AUTH-001"
        )


def test_validate_unknown_lane_fails():
    """Test that unknown lane validation fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        policy = LanePolicy()
        policy.audit_logger = AuditLogger(log_directory=Path(tmpdir))

        with pytest.raises(ValueError, match="Cannot validate authorization for unknown lane"):
            policy.validate_lane_authorization(
                lane=Lane.UNKNOWN, authorization_reference="AUTH-001"
            )
