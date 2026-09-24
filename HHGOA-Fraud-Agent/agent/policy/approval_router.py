"""Approval Router: Determines governance approval level (auto, L1, L2) under Fraud Policy v1.0."""

from agent.schemas.action_schema import ActionEnum, ApprovalRouteEnum


class ApprovalRouter:
    """Assigns deterministic approval routes based on action type and exposure value."""

    AUTO_ACTIONS = {
        ActionEnum.ALLOW_TRANSACTION,
        ActionEnum.MONITOR_CARD,
        ActionEnum.MONITOR_CONNECTED_CARDS,
        ActionEnum.WARN_CUSTOMER,
        ActionEnum.VERIFY_WITH_CUSTOMER,
        ActionEnum.STEP_UP_AUTH,
        ActionEnum.GENERATE_REPORT,
        ActionEnum.CREATE_CASE,
        ActionEnum.ESCALATE_TO_ANALYST,
        ActionEnum.CLOSE_NO_FRAUD,
    }

    @classmethod
    def get_approval_route(cls, action: ActionEnum, exposure_usd: float = 0.0) -> ApprovalRouteEnum:
        """
        Determines the exact approval route:
        - auto: Agent may act autonomously
        - L1: Team lead authorization required
        - L2: Fraud manager authorization required
        """
        if action in cls.AUTO_ACTIONS:
            return ApprovalRouteEnum.AUTO

        if action == ActionEnum.DECLINE_TRANSACTION:
            return ApprovalRouteEnum.L1

        if action == ActionEnum.BLOCK_CARD:
            if exposure_usd > 2500.0:
                return ApprovalRouteEnum.L2
            return ApprovalRouteEnum.L1

        if action == ActionEnum.BLOCK_ALL_CARDS:
            return ApprovalRouteEnum.L2

        if action == ActionEnum.FILE_REPORT:
            return ApprovalRouteEnum.L2

        return ApprovalRouteEnum.L1
