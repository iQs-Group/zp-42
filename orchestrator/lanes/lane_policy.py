"""
ZP42 Lane Policy Engine

Enforces lane-based authorization for all operations.
Foundation PR #1: Authorization checking and lane assignment logic.
"""

from enum import Enum
from typing import Optional

from governance.audit_logger import get_audit_logger


class Lane(Enum):
    """Operational lanes with increasing authorization requirements."""

    A = "A"  # Defensive - customer/system authorization required
    B = "B"  # Active-defense - written authorization required
    C = "C"  # Sovereign-authorized - sovereign auth + human signoff required
    UNKNOWN = "unknown"  # Unassigned - fail closed


class LanePolicy:
    """
    Lane-based authorization policy engine.

    Enforces fail-closed authorization model:
    - Lane A: Requires customer or system authorization reference
    - Lane B: Requires written authorization document reference
    - Lane C: Requires sovereign authorization reference + human signoff
    - Unknown lane: Fails closed
    """

    def __init__(self):
        self.audit_logger = get_audit_logger()

    def assign_lane(
        self,
        operation_description: str,
        authorization_reference: Optional[str] = None,
        sovereign_authorization: bool = False,
        human_signoff: bool = False,
    ) -> Lane:
        """
        Assign operational lane based on authorization and operation type.

        Args:
            operation_description: Description of the operation
            authorization_reference: Reference to authorization document/ID
            sovereign_authorization: Whether sovereign authorization exists
            human_signoff: Whether human signoff has been obtained

        Returns:
            Assigned Lane

        Raises:
            ValueError: If authorization is insufficient or invalid
        """
        # Fail closed if no authorization reference
        if not authorization_reference:
            self.audit_logger.log_event(
                operation_type="lane_assignment",
                lane=Lane.UNKNOWN.value,
                actor_type="system",
                actor_identifier="lane_policy.assign_lane",
                result="denied",
                failure_reason="No authorization reference provided",
                operation_details={"operation_description": operation_description},
            )
            raise ValueError("Authorization reference required. Failing closed.")

        # Determine lane based on authorization type
        lane = None

        if sovereign_authorization and human_signoff:
            # Lane C: Sovereign-authorized with human signoff
            lane = Lane.C
        elif sovereign_authorization and not human_signoff:
            # Sovereign auth without human signoff - fail closed
            self.audit_logger.log_event(
                operation_type="lane_assignment",
                lane=Lane.UNKNOWN.value,
                actor_type="system",
                actor_identifier="lane_policy.assign_lane",
                result="denied",
                failure_reason="Sovereign authorization requires human signoff",
                authorization_reference=authorization_reference,
                operation_details={"operation_description": operation_description},
            )
            raise ValueError("Lane C requires both sovereign authorization AND human signoff")
        elif self._is_active_defense_operation(operation_description):
            # Lane B: Active-defense operations require written authorization
            if not self._validate_written_authorization(authorization_reference):
                self.audit_logger.log_event(
                    operation_type="lane_assignment",
                    lane=Lane.UNKNOWN.value,
                    actor_type="system",
                    actor_identifier="lane_policy.assign_lane",
                    result="denied",
                    failure_reason="Active-defense operation requires written authorization",
                    authorization_reference=authorization_reference,
                    operation_details={"operation_description": operation_description},
                )
                raise ValueError("Active-defense operations require written authorization")
            lane = Lane.B
        else:
            # Lane A: Defensive operations with customer/system authorization
            lane = Lane.A

        # Log successful lane assignment
        self.audit_logger.log_event(
            operation_type="lane_assignment",
            lane=lane.value,
            actor_type="system",
            actor_identifier="lane_policy.assign_lane",
            result="success",
            authorization_reference=authorization_reference,
            operation_details={
                "operation_description": operation_description,
                "sovereign_authorization": sovereign_authorization,
                "human_signoff": human_signoff,
            },
        )

        return lane

    def validate_lane_authorization(
        self, lane: Lane, authorization_reference: str
    ) -> bool:
        """
        Validate that authorization is sufficient for the assigned lane.

        Args:
            lane: Assigned lane
            authorization_reference: Authorization reference to validate

        Returns:
            True if authorization is valid for the lane

        Raises:
            ValueError: If authorization is invalid
        """
        if lane == Lane.UNKNOWN:
            self.audit_logger.log_event(
                operation_type="authorization_check",
                lane=Lane.UNKNOWN.value,
                actor_type="system",
                actor_identifier="lane_policy.validate_lane_authorization",
                result="denied",
                failure_reason="Cannot validate authorization for unknown lane",
                authorization_reference=authorization_reference,
            )
            raise ValueError("Cannot validate authorization for unknown lane")

        # Log authorization check
        self.audit_logger.log_event(
            operation_type="authorization_check",
            lane=lane.value,
            actor_type="system",
            actor_identifier="lane_policy.validate_lane_authorization",
            result="success",
            authorization_reference=authorization_reference,
        )

        return True

    def _is_active_defense_operation(self, operation_description: str) -> bool:
        """
        Determine if operation is active-defense (Lane B) vs defensive (Lane A).

        Foundation PR #1: Simple keyword matching.
        Production should use more sophisticated classification.
        """
        active_defense_keywords = [
            "deception",
            "honeypot",
            "honeytoken",
            "threat_hunting",
            "controlled_engagement",
            "attribution",
        ]

        operation_lower = operation_description.lower()
        return any(keyword in operation_lower for keyword in active_defense_keywords)

    def _validate_written_authorization(self, authorization_reference: str) -> bool:
        """
        Validate that authorization reference is a written document.

        Foundation PR #1: Basic format checking.
        Production should verify against authorization database.
        """
        # Require specific format for written authorization
        # Example: AUTH-2026-05-18-001 or similar
        if not authorization_reference or len(authorization_reference) < 10:
            return False

        # Check for common written authorization prefixes
        valid_prefixes = ["AUTH-", "WRITTEN-AUTH-", "CONTRACT-", "SOW-"]
        return any(authorization_reference.startswith(prefix) for prefix in valid_prefixes)
