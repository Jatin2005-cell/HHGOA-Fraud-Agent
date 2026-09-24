"""Unit tests for Case Lifecycle State Transitions."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from case_management.case_lifecycle import (
    CaseLifecycleStatus,
    CaseLifecycleManager,
    LifecycleTransitionError,
)


def test_valid_lifecycle_transitions():
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.NEW, CaseLifecycleStatus.INVESTIGATING)
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.INVESTIGATING, CaseLifecycleStatus.EVIDENCE_PENDING)
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.EVIDENCE_PENDING, CaseLifecycleStatus.REVIEW)
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.REVIEW, CaseLifecycleStatus.ACTION_REQUIRED)
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.ACTION_REQUIRED, CaseLifecycleStatus.APPROVAL_PENDING)
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.APPROVAL_PENDING, CaseLifecycleStatus.RESOLVED)
    assert CaseLifecycleManager.validate_transition(CaseLifecycleStatus.RESOLVED, CaseLifecycleStatus.CLOSED)


def test_illegal_lifecycle_transitions():
    # Attempting to jump from NEW directly to CLOSED must fail
    try:
        CaseLifecycleManager.validate_transition(CaseLifecycleStatus.NEW, CaseLifecycleStatus.CLOSED)
        assert False, "Should have raised LifecycleTransitionError"
    except LifecycleTransitionError as e:
        assert "Invalid lifecycle transition" in str(e)

    # Attempting to jump from NEW directly to APPROVAL_PENDING must fail
    try:
        CaseLifecycleManager.validate_transition(CaseLifecycleStatus.NEW, CaseLifecycleStatus.APPROVAL_PENDING)
        assert False, "Should have raised LifecycleTransitionError"
    except LifecycleTransitionError:
        pass


if __name__ == "__main__":
    test_valid_lifecycle_transitions()
    test_illegal_lifecycle_transitions()
    print("test_case_lifecycle.py: ALL PASS")
