"""
ZP42 Human Authorization Gate

Enforces human-in-the-loop approval for sensitive operations.
Foundation PR #1: Human gate request/approval/denial tracking.
"""

from enum import Enum
from typing import Dict, Optional
from uuid import uuid4

from governance.audit_logger import get_audit_logger
from orchestrator.lanes.lane_policy import Lane


class ApprovalStatus(Enum):
    """Status of human gate approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class HumanGate:
    """
    Human authorization gate for sensitive operations.

    Enforces human approval requirements:
    - Lane A: No human gate required for routine defensive operations
    - Lane B: Human review required for active-defense deployment
    - Lane C: Human approval required for every operation
    """

    def __init__(self):
        self.audit_logger = get_audit_logger()
        # Foundation PR #1: In-memory approval tracking
        # Production should use persistent storage
        self._pending_approvals: Dict[str, Dict] = {}

    def requires_human_approval(
        self, lane: Lane, operation_type: str
    ) -> bool:
        """
        Determine if operation requires human approval.

        Args:
            lane: Operational lane
            operation_type: Type of operation

        Returns:
            True if human approval is required
        """
        # Lane A: Most defensive operations don't require approval
        if lane == Lane.A:
            # Require approval for sensitive defensive operations
            sensitive_operations = {
                "live_vulnerability_scan",
                "configuration_change",
                "access_customer_data",
            }
            return operation_type in sensitive_operations

        # Lane B: All active-defense deployments require review
        if lane == Lane.B:
            return True

        # Lane C: Every operation requires approval
        if lane == Lane.C:
            return True

        # Unknown lane: Fail closed, require approval
        if lane == Lane.UNKNOWN:
            return True

        return False

    def request_approval(
        self,
        lane: Lane,
        operation_type: str,
        operation_description: str,
        authorization_reference: str,
        requestor_identifier: str,
        operation_details: Optional[Dict] = None,
    ) -> str:
        """
        Request human approval for an operation.

        Args:
            lane: Operational lane
            operation_type: Type of operation
            operation_description: Human-readable operation description
            authorization_reference: Authorization reference
            requestor_identifier: Identifier of requesting actor
            operation_details: Optional operation details

        Returns:
            approval_request_id: Unique ID for this approval request
        """
        approval_request_id = str(uuid4())

        approval_request = {
            "approval_request_id": approval_request_id,
            "lane": lane.value,
            "operation_type": operation_type,
            "operation_description": operation_description,
            "authorization_reference": authorization_reference,
            "requestor_identifier": requestor_identifier,
            "operation_details": operation_details or {},
            "status": ApprovalStatus.PENDING.value,
        }

        self._pending_approvals[approval_request_id] = approval_request

        # Log approval request
        self.audit_logger.log_event(
            operation_type="human_gate_request",
            lane=lane.value,
            actor_type="system",
            actor_identifier=requestor_identifier,
            result="pending",
            authorization_reference=authorization_reference,
            operation_details={
                "approval_request_id": approval_request_id,
                "operation_type": operation_type,
                "operation_description": operation_description,
                **(operation_details or {}),
            },
        )

        return approval_request_id

    def approve_operation(
        self,
        approval_request_id: str,
        approver_identifier: str,
        approval_notes: Optional[str] = None,
    ) -> bool:
        """
        Approve a pending operation.

        Args:
            approval_request_id: ID of approval request
            approver_identifier: Identifier of approving human
            approval_notes: Optional approval notes

        Returns:
            True if approval was successful

        Raises:
            ValueError: If approval request not found or already processed
        """
        if approval_request_id not in self._pending_approvals:
            raise ValueError(f"Approval request {approval_request_id} not found")

        request = self._pending_approvals[approval_request_id]

        if request["status"] != ApprovalStatus.PENDING.value:
            raise ValueError(
                f"Approval request {approval_request_id} already processed: {request['status']}"
            )

        # Update status
        request["status"] = ApprovalStatus.APPROVED.value
        request["approver_identifier"] = approver_identifier
        request["approval_notes"] = approval_notes

        # Log approval
        self.audit_logger.log_event(
            operation_type="human_gate_approval",
            lane=request["lane"],
            actor_type="human",
            actor_identifier=approver_identifier,
            result="success",
            authorization_reference=request["authorization_reference"],
            operation_details={
                "approval_request_id": approval_request_id,
                "operation_type": request["operation_type"],
                "approval_notes": approval_notes,
            },
        )

        return True

    def deny_operation(
        self,
        approval_request_id: str,
        denier_identifier: str,
        denial_reason: str,
    ) -> bool:
        """
        Deny a pending operation.

        Args:
            approval_request_id: ID of approval request
            denier_identifier: Identifier of denying human
            denial_reason: Reason for denial

        Returns:
            True if denial was successful

        Raises:
            ValueError: If approval request not found or already processed
        """
        if approval_request_id not in self._pending_approvals:
            raise ValueError(f"Approval request {approval_request_id} not found")

        request = self._pending_approvals[approval_request_id]

        if request["status"] != ApprovalStatus.PENDING.value:
            raise ValueError(
                f"Approval request {approval_request_id} already processed: {request['status']}"
            )

        # Update status
        request["status"] = ApprovalStatus.DENIED.value
        request["denier_identifier"] = denier_identifier
        request["denial_reason"] = denial_reason

        # Log denial
        self.audit_logger.log_event(
            operation_type="human_gate_denial",
            lane=request["lane"],
            actor_type="human",
            actor_identifier=denier_identifier,
            result="denied",
            failure_reason=denial_reason,
            authorization_reference=request["authorization_reference"],
            operation_details={
                "approval_request_id": approval_request_id,
                "operation_type": request["operation_type"],
                "denial_reason": denial_reason,
            },
        )

        return True

    def get_approval_status(self, approval_request_id: str) -> ApprovalStatus:
        """
        Get current status of approval request.

        Args:
            approval_request_id: ID of approval request

        Returns:
            Current approval status

        Raises:
            ValueError: If approval request not found
        """
        if approval_request_id not in self._pending_approvals:
            raise ValueError(f"Approval request {approval_request_id} not found")

        status_str = self._pending_approvals[approval_request_id]["status"]
        return ApprovalStatus(status_str)
