"""
ZP42 Rules of Engagement (ROE) Engine

Enforces operational rules and boundaries for all lanes.
Foundation PR #1: ROE checking skeleton with prohibited capabilities.
"""

from typing import Dict, List, Optional

from governance.audit_logger import get_audit_logger
from orchestrator.lanes.lane_policy import Lane


class ROEViolation(Exception):
    """Raised when an operation violates rules of engagement."""

    pass


class ROEEngine:
    """
    Rules of Engagement enforcement engine.

    Validates all operations against ROE before execution.
    Enforces prohibited capabilities across all lanes.
    """

    # Capabilities prohibited in ALL lanes
    GLOBALLY_PROHIBITED_CAPABILITIES = {
        "malware_creation",
        "malware_deployment",
        "credential_theft",
        "credential_harvesting",
        "ddos_generation",
        "data_exfiltration_unauthorized",
        "persistence_installation",
        "evasion_technique",
        "destructive_payload",
        "autonomous_counter_action",
        "unauthorized_response_action",
        "unauthorized_third_party_targeting",
    }

    def __init__(self):
        self.audit_logger = get_audit_logger()

    def check_roe(
        self,
        lane: Lane,
        capability_requested: str,
        operation_details: Optional[Dict] = None,
    ) -> bool:
        """
        Check if requested capability is permitted under ROE for the given lane.

        Args:
            lane: Operational lane
            capability_requested: Capability being requested
            operation_details: Optional operation details for audit

        Returns:
            True if capability is permitted

        Raises:
            ROEViolation: If capability violates ROE
        """
        # Check globally prohibited capabilities first
        if capability_requested in self.GLOBALLY_PROHIBITED_CAPABILITIES:
            self.audit_logger.log_event(
                operation_type="roe_check",
                lane=lane.value,
                actor_type="system",
                actor_identifier="roe_engine.check_roe",
                result="denied",
                failure_reason=f"Globally prohibited capability: {capability_requested}",
                operation_details=operation_details or {},
                policy_violations=[f"prohibited_capability:{capability_requested}"],
            )
            raise ROEViolation(
                f"Capability '{capability_requested}' is globally prohibited across all lanes"
            )

        # Lane-specific ROE checks
        if lane == Lane.UNKNOWN:
            self.audit_logger.log_event(
                operation_type="roe_check",
                lane=Lane.UNKNOWN.value,
                actor_type="system",
                actor_identifier="roe_engine.check_roe",
                result="denied",
                failure_reason="Cannot execute operations in unknown lane",
                operation_details=operation_details or {},
            )
            raise ROEViolation("Cannot execute operations in unknown lane")

        # Lane A: Defensive only
        if lane == Lane.A:
            prohibited_lane_a = {
                "live_exploitation",
                "deception_deployment",
                "honeypot_deployment",
                "active_engagement",
            }
            if capability_requested in prohibited_lane_a:
                self.audit_logger.log_event(
                    operation_type="roe_check",
                    lane=Lane.A.value,
                    actor_type="system",
                    actor_identifier="roe_engine.check_roe",
                    result="denied",
                    failure_reason=f"Capability requires Lane B or C: {capability_requested}",
                    operation_details=operation_details or {},
                )
                raise ROEViolation(
                    f"Capability '{capability_requested}' requires Lane B or C authorization"
                )

        # Lane B: Active-defense permitted, but no offensive operations
        if lane == Lane.B:
            prohibited_lane_b = {
                "offensive_operation",
                "unauthorized_system_access",
                "destructive_action",
            }
            if capability_requested in prohibited_lane_b:
                self.audit_logger.log_event(
                    operation_type="roe_check",
                    lane=Lane.B.value,
                    actor_type="system",
                    actor_identifier="roe_engine.check_roe",
                    result="denied",
                    failure_reason=f"Offensive capability requires Lane C: {capability_requested}",
                    operation_details=operation_details or {},
                )
                raise ROEViolation(
                    f"Capability '{capability_requested}' requires Lane C authorization"
                )

        # Lane C: Sovereign-authorized operations with human gates
        # Most permissive lane, but still bounded by global prohibitions
        if lane == Lane.C:
            # Even Lane C cannot perform globally prohibited capabilities
            pass

        # Log successful ROE check
        self.audit_logger.log_event(
            operation_type="roe_check",
            lane=lane.value,
            actor_type="system",
            actor_identifier="roe_engine.check_roe",
            result="success",
            operation_details={
                "capability_requested": capability_requested,
                **(operation_details or {}),
            },
        )

        return True

    def get_permitted_capabilities(self, lane: Lane) -> List[str]:
        """
        Get list of capabilities permitted for a given lane.

        Args:
            lane: Operational lane

        Returns:
            List of permitted capability names
        """
        # Foundation PR #1: Return capability lists per lane
        capabilities_by_lane = {
            Lane.A: [
                "vulnerability_assessment",
                "defensive_analysis",
                "security_config_review",
                "compliance_checking",
                "threat_modeling",
            ],
            Lane.B: [
                "vulnerability_assessment",
                "defensive_analysis",
                "deception_deployment",
                "honeypot_deployment",
                "threat_hunting",
                "controlled_engagement",
                "attribution_support",
            ],
            Lane.C: [
                "vulnerability_assessment",
                "defensive_analysis",
                "deception_deployment",
                "threat_hunting",
                "sovereign_authorized_operations",
            ],
            Lane.UNKNOWN: [],
        }

        return capabilities_by_lane.get(lane, [])

    def validate_escalation_attempt(
        self, current_lane: Lane, requested_lane: Lane
    ) -> bool:
        """
        Validate if escalation from current lane to requested lane is permitted.

        Foundation PR #1: All escalation attempts are denied and logged.
        Production should implement authorized escalation paths.

        Args:
            current_lane: Current operational lane
            requested_lane: Requested lane for escalation

        Returns:
            True if escalation is permitted

        Raises:
            ROEViolation: If escalation is not permitted
        """
        if current_lane == requested_lane:
            return True

        # Foundation PR #1: Deny all lane escalation attempts
        self.audit_logger.log_event(
            operation_type="escalation_attempt",
            lane=current_lane.value,
            actor_type="system",
            actor_identifier="roe_engine.validate_escalation_attempt",
            result="denied",
            failure_reason=f"Escalation from {current_lane.value} to {requested_lane.value} not permitted",
            escalation_attempt=True,
            policy_violations=["unauthorized_lane_escalation"],
        )

        raise ROEViolation(
            f"Lane escalation from {current_lane.value} to {requested_lane.value} is not permitted"
        )
