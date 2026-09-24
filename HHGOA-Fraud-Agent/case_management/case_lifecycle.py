"""Case Lifecycle State Machine with deterministic transition validation."""

from enum import Enum
from typing import Dict, List, Set


class CaseLifecycleStatus(str, Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    REVIEW = "REVIEW"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class LifecycleTransitionError(ValueError):
    """Raised when an illegal case lifecycle transition is attempted."""
    pass


# Valid lifecycle state transitions
VALID_LIFECYCLE_TRANSITIONS: Dict[CaseLifecycleStatus, Set[CaseLifecycleStatus]] = {
    CaseLifecycleStatus.NEW: {
        CaseLifecycleStatus.INVESTIGATING,
        CaseLifecycleStatus.CANCELLED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.INVESTIGATING: {
        CaseLifecycleStatus.EVIDENCE_PENDING,
        CaseLifecycleStatus.REVIEW,
        CaseLifecycleStatus.ACTION_REQUIRED,
        CaseLifecycleStatus.APPROVAL_PENDING,
        CaseLifecycleStatus.RESOLVED,
        CaseLifecycleStatus.ESCALATED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.EVIDENCE_PENDING: {
        CaseLifecycleStatus.REVIEW,
        CaseLifecycleStatus.INVESTIGATING,
        CaseLifecycleStatus.ESCALATED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.REVIEW: {
        CaseLifecycleStatus.ACTION_REQUIRED,
        CaseLifecycleStatus.APPROVAL_PENDING,
        CaseLifecycleStatus.RESOLVED,
        CaseLifecycleStatus.ESCALATED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.ACTION_REQUIRED: {
        CaseLifecycleStatus.APPROVAL_PENDING,
        CaseLifecycleStatus.RESOLVED,
        CaseLifecycleStatus.ESCALATED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.APPROVAL_PENDING: {
        CaseLifecycleStatus.INVESTIGATING,
        CaseLifecycleStatus.RESOLVED,
        CaseLifecycleStatus.ESCALATED,
        CaseLifecycleStatus.CANCELLED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.RESOLVED: {
        CaseLifecycleStatus.CLOSED,
        CaseLifecycleStatus.ESCALATED,
    },
    CaseLifecycleStatus.ESCALATED: {
        CaseLifecycleStatus.INVESTIGATING,
        CaseLifecycleStatus.RESOLVED,
        CaseLifecycleStatus.CLOSED,
        CaseLifecycleStatus.FAILED,
    },
    CaseLifecycleStatus.CLOSED: set(),
    CaseLifecycleStatus.FAILED: {CaseLifecycleStatus.INVESTIGATING},
    CaseLifecycleStatus.CANCELLED: set(),
}


class CaseLifecycleManager:
    """Manages lifecycle transitions for DynamicCase records."""

    @classmethod
    def validate_transition(
        cls, current_status: CaseLifecycleStatus, new_status: CaseLifecycleStatus
    ) -> bool:
        """Checks if a transition between two lifecycle states is permissible."""
        if current_status == new_status:
            return True  # Idempotent state transition
        allowed = VALID_LIFECYCLE_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise LifecycleTransitionError(
                f"Invalid lifecycle transition from {current_status.value} to {new_status.value}. "
                f"Permissible transitions: {[s.value for s in allowed]}"
            )
        return True
