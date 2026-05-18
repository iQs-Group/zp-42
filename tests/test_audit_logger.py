"""Tests for audit logger."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from governance.audit_logger import AuditLogger


def test_audit_logger_initialization():
    """Test audit logger initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))
        assert logger.log_directory.exists()
        assert logger.log_file.parent == logger.log_directory


def test_log_event_success():
    """Test logging a successful event."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))

        event_id = logger.log_event(
            operation_type="lane_assignment",
            lane="A",
            actor_type="system",
            actor_identifier="test_system",
            result="success",
            authorization_reference="AUTH-TEST-001",
        )

        assert event_id is not None
        assert logger.log_file.exists()

        # Verify log content
        with open(logger.log_file, "r") as f:
            log_line = f.readline()
            event = json.loads(log_line)

            assert event["event_id"] == event_id
            assert event["operation_type"] == "lane_assignment"
            assert event["lane"] == "A"
            assert event["result"] == "success"
            assert event["authorization_reference"] == "AUTH-TEST-001"


def test_log_event_with_failure():
    """Test logging a failed event."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))

        event_id = logger.log_event(
            operation_type="authorization_check",
            lane="unknown",
            actor_type="system",
            actor_identifier="test_system",
            result="failure",
            failure_reason="Invalid authorization",
        )

        with open(logger.log_file, "r") as f:
            event = json.loads(f.readline())
            assert event["result"] == "failure"
            assert event["failure_reason"] == "Invalid authorization"


def test_log_event_with_escalation():
    """Test logging an escalation attempt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))

        event_id = logger.log_event(
            operation_type="escalation_attempt",
            lane="A",
            actor_type="system",
            actor_identifier="test_system",
            result="denied",
            escalation_attempt=True,
            policy_violations=["unauthorized_lane_escalation"],
        )

        with open(logger.log_file, "r") as f:
            event = json.loads(f.readline())
            assert event["escalation_attempt"] is True
            assert "unauthorized_lane_escalation" in event["policy_violations"]


def test_invalid_operation_type():
    """Test that invalid operation type raises ValueError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))

        with pytest.raises(ValueError, match="Invalid operation_type"):
            logger.log_event(
                operation_type="invalid_operation",
                lane="A",
                actor_type="system",
                actor_identifier="test_system",
                result="success",
            )


def test_invalid_lane():
    """Test that invalid lane raises ValueError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))

        with pytest.raises(ValueError, match="Invalid lane"):
            logger.log_event(
                operation_type="lane_assignment",
                lane="invalid",
                actor_type="system",
                actor_identifier="test_system",
                result="success",
            )


def test_query_logs():
    """Test querying audit logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_directory=Path(tmpdir))

        # Log multiple events
        logger.log_event(
            operation_type="lane_assignment",
            lane="A",
            actor_type="system",
            actor_identifier="system_1",
            result="success",
        )
        logger.log_event(
            operation_type="authorization_check",
            lane="B",
            actor_type="system",
            actor_identifier="system_2",
            result="success",
        )

        # Query all events
        results = logger.query_logs()
        assert len(results) == 2

        # Query by lane
        results = logger.query_logs(lane="A")
        assert len(results) == 1
        assert results[0]["lane"] == "A"

        # Query by operation type
        results = logger.query_logs(operation_type="authorization_check")
        assert len(results) == 1
        assert results[0]["operation_type"] == "authorization_check"
