"""
ZP42 Audit Logger

Append-only JSONL audit logging for all ZP42 operations.
Foundation PR #1: Local file-based logging only.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """
    Append-only audit logger for ZP42 operations.

    All operations are logged to JSONL format with immutable audit trail.
    Logs are written synchronously to ensure durability.
    """

    def __init__(self, log_directory: Optional[Path] = None):
        """
        Initialize audit logger.

        Args:
            log_directory: Directory for audit logs. Defaults to governance/logs/
        """
        if log_directory is None:
            log_directory = Path(__file__).parent / "logs"

        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Use daily log files for Foundation PR #1
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.log_file = self.log_directory / f"audit_{today}.jsonl"

    def log_event(
        self,
        operation_type: str,
        lane: str,
        actor_type: str,
        actor_identifier: str,
        result: str,
        authorization_reference: Optional[str] = None,
        operation_details: Optional[Dict[str, Any]] = None,
        failure_reason: Optional[str] = None,
        escalation_attempt: bool = False,
        policy_violations: Optional[List[str]] = None,
    ) -> str:
        """
        Log an audit event.

        Args:
            operation_type: Type of operation (see audit_schema.json for valid values)
            lane: Operational lane (A, B, C, or unknown)
            actor_type: Type of actor (system, human, api)
            actor_identifier: Unique identifier for the actor
            result: Operation result (success, failure, denied, pending)
            authorization_reference: Optional authorization reference
            operation_details: Optional operation-specific details
            failure_reason: Optional failure reason
            escalation_attempt: Whether unauthorized escalation was attempted
            policy_violations: Optional list of policy violations

        Returns:
            event_id: UUID of the logged event

        Raises:
            ValueError: If required fields are invalid
        """
        # Validate required enums
        valid_operation_types = {
            "lane_assignment",
            "authorization_check",
            "human_gate_request",
            "human_gate_approval",
            "human_gate_denial",
            "model_reference",
            "model_download_attempt",
            "inference_request",
            "escalation_attempt",
            "policy_violation",
            "roe_check",
            "capability_request",
            "operation_start",
            "operation_complete",
            "operation_failed",
        }
        if operation_type not in valid_operation_types:
            raise ValueError(f"Invalid operation_type: {operation_type}")

        valid_lanes = {"A", "B", "C", "unknown"}
        if lane not in valid_lanes:
            raise ValueError(f"Invalid lane: {lane}")

        valid_actor_types = {"system", "human", "api"}
        if actor_type not in valid_actor_types:
            raise ValueError(f"Invalid actor_type: {actor_type}")

        valid_results = {"success", "failure", "denied", "pending"}
        if result not in valid_results:
            raise ValueError(f"Invalid result: {result}")

        # Generate event
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        event = {
            "timestamp": timestamp,
            "event_id": event_id,
            "operation_type": operation_type,
            "lane": lane,
            "actor": {"type": actor_type, "identifier": actor_identifier},
            "result": result,
            "escalation_attempt": escalation_attempt,
        }

        # Add optional fields
        if authorization_reference:
            event["authorization_reference"] = authorization_reference
        if operation_details:
            event["operation_details"] = operation_details
        if failure_reason:
            event["failure_reason"] = failure_reason
        if policy_violations:
            event["policy_violations"] = policy_violations

        # Append to log file (atomic write)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        return event_id

    def query_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        lane: Optional[str] = None,
        operation_type: Optional[str] = None,
        actor_identifier: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with filters.

        Foundation PR #1: Simple file-based query. Production should use database.

        Args:
            start_time: Filter events after this time
            end_time: Filter events before this time
            lane: Filter by lane
            operation_type: Filter by operation type
            actor_identifier: Filter by actor identifier

        Returns:
            List of matching audit events
        """
        results = []

        # Iterate through all JSONL log files
        for log_file in sorted(self.log_directory.glob("audit_*.jsonl")):
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    event = json.loads(line.strip())

                    # Apply filters
                    if start_time and datetime.fromisoformat(event["timestamp"]) < start_time:
                        continue
                    if end_time and datetime.fromisoformat(event["timestamp"]) > end_time:
                        continue
                    if lane and event.get("lane") != lane:
                        continue
                    if operation_type and event.get("operation_type") != operation_type:
                        continue
                    if (
                        actor_identifier
                        and event.get("actor", {}).get("identifier") != actor_identifier
                    ):
                        continue

                    results.append(event)

        return results


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
