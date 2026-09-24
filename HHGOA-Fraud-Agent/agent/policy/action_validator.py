"""Action Validator: Validates recommended actions against deterministic policy rules."""

from typing import Any, Dict, List, Tuple
from agent.schemas.action_schema import ActionEnum, ActionItem, ApprovalRouteEnum
from .policy_rules import PolicyRuleEnum
from .approval_router import ApprovalRouter


class ActionValidator:
    """Enforces policy constraints and prevents unauthorized or policy-breaching action recommendations."""

    @classmethod
    def validate_action(
        cls,
        candidate_action: ActionEnum,
        context: Dict[str, Any],
    ) -> Tuple[bool, ActionEnum, ApprovalRouteEnum, List[PolicyRuleEnum], str]:
        """
        Validates candidate action against context.
        Returns:
            Tuple of (allowed, validated_action, route, triggered_rules, reason)
        """
        fraud_prob = float(context.get("fraud_probability", 0.5))
        exposure = float(context.get("exposure_usd", 0.0))
        num_signals = int(context.get("num_signals", 1))
        customer_confirmed = bool(context.get("customer_confirmed", False))
        customer_denied = bool(context.get("customer_denied", False))
        confirmed_compromised_cards = int(context.get("confirmed_compromised_cards", 1))

        triggered_rules: List[PolicyRuleEnum] = []

        # Policy R3: Customer confirmed transaction
        if customer_confirmed:
            triggered_rules.append(PolicyRuleEnum.R3)
            return (
                True,
                ActionEnum.CLOSE_NO_FRAUD,
                ApprovalRouteEnum.AUTO,
                triggered_rules,
                "R3: Customer confirmed transaction; closed as legitimate.",
            )

        # Policy R1: Verify before you block on a weak signal
        if candidate_action in [ActionEnum.BLOCK_CARD, ActionEnum.BLOCK_ALL_CARDS]:
            if num_signals <= 1 and fraud_prob < 0.70 and not customer_denied:
                triggered_rules.append(PolicyRuleEnum.R1)
                route = ApprovalRouter.get_approval_route(ActionEnum.VERIFY_WITH_CUSTOMER, exposure)
                return (
                    False,
                    ActionEnum.VERIFY_WITH_CUSTOMER,
                    route,
                    triggered_rules,
                    f"R1: Blocking on a single signal with probability {fraud_prob:.2f} (< 0.70) is a policy breach. Replaced with VERIFY_WITH_CUSTOMER.",
                )

        # Policy R10: Never BLOCK_ALL_CARDS unless multiple cards compromised
        if candidate_action == ActionEnum.BLOCK_ALL_CARDS:
            if confirmed_compromised_cards < 2:
                triggered_rules.append(PolicyRuleEnum.R10)
                route = ApprovalRouter.get_approval_route(ActionEnum.BLOCK_CARD, exposure)
                return (
                    False,
                    ActionEnum.BLOCK_CARD,
                    route,
                    triggered_rules,
                    "R10: BLOCK_ALL_CARDS prohibited without multiple confirmed compromised cards. Downscoped to BLOCK_CARD.",
                )

        # Normal validation
        route = ApprovalRouter.get_approval_route(candidate_action, exposure)
        return True, candidate_action, route, triggered_rules, "Permitted under Fraud Policy v1.0."
