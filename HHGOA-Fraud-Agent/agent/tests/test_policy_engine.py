"""Unit tests for deterministic Policy Rules R1-R10 and Approval Routing."""

from agent.schemas.action_schema import ActionEnum, ApprovalRouteEnum
from agent.schemas.investigation_schema import PatternEnum, VerdictEnum
from agent.policy.approval_router import ApprovalRouter
from agent.policy.action_validator import ActionValidator
from agent.policy.policy_engine import PolicyEngine


def test_approval_routing():
    # auto route tests
    assert ApprovalRouter.get_approval_route(ActionEnum.ALLOW_TRANSACTION) == ApprovalRouteEnum.AUTO
    assert ApprovalRouter.get_approval_route(ActionEnum.VERIFY_WITH_CUSTOMER) == ApprovalRouteEnum.AUTO
    assert ApprovalRouter.get_approval_route(ActionEnum.CREATE_CASE) == ApprovalRouteEnum.AUTO

    # L1 route tests
    assert ApprovalRouter.get_approval_route(ActionEnum.DECLINE_TRANSACTION) == ApprovalRouteEnum.L1
    assert ApprovalRouter.get_approval_route(ActionEnum.BLOCK_CARD, exposure_usd=500.0) == ApprovalRouteEnum.L1
    assert ApprovalRouter.get_approval_route(ActionEnum.BLOCK_CARD, exposure_usd=2500.0) == ApprovalRouteEnum.L1

    # L2 route tests
    assert ApprovalRouter.get_approval_route(ActionEnum.BLOCK_CARD, exposure_usd=2501.0) == ApprovalRouteEnum.L2
    assert ApprovalRouter.get_approval_route(ActionEnum.BLOCK_ALL_CARDS) == ApprovalRouteEnum.L2
    assert ApprovalRouter.get_approval_route(ActionEnum.FILE_REPORT) == ApprovalRouteEnum.L2


def test_policy_r1_verify_before_block():
    # If single signal with prob < 0.70, blocking is rejected under Policy R1
    context = {
        "fraud_probability": 0.61,
        "exposure_usd": 77.07,
        "num_signals": 1,
        "customer_denied": False,
    }
    allowed, action, route, rules, reason = ActionValidator.validate_action(
        ActionEnum.BLOCK_CARD, context
    )
    assert not allowed
    assert action == ActionEnum.VERIFY_WITH_CUSTOMER
    assert "R1" in reason


def test_policy_r2_customer_denial():
    context = {
        "fraud_probability": 0.88,
        "exposure_usd": 1200.0,
        "pattern": PatternEnum.CARD_NOT_PRESENT_FRAUD,
        "connected_cards": ["C11111-K2"],
        "shared_device": True,
    }
    initial_actions = PolicyEngine.evaluate_initial_actions(context)
    final_actions, what_changed = PolicyEngine.evaluate_final_actions(
        context, initial_actions, assumed_evidence_response="Customer denied transaction."
    )
    final_act_names = [a.action for a in final_actions]
    assert ActionEnum.BLOCK_CARD in final_act_names
    assert ActionEnum.CREATE_CASE in final_act_names
    assert ActionEnum.FILE_REPORT in final_act_names  # exposure > $1000 and shared device


if __name__ == "__main__":
    test_approval_routing()
    test_policy_r1_verify_before_block()
    test_policy_r2_customer_denial()
    print("test_policy_engine.py: ALL PASS")
