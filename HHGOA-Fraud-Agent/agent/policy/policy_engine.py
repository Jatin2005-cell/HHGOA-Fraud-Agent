"""Policy Engine: Synthesizes initial and final next-best actions and SAR filings."""

from typing import Any, Dict, List, Tuple
from agent.schemas.action_schema import ActionEnum, ActionItem, ApprovalRouteEnum, NextBestActions
from agent.schemas.investigation_schema import PatternEnum, SARRecord, VerdictEnum
from .policy_rules import PolicyRuleEnum
from .approval_router import ApprovalRouter
from .action_validator import ActionValidator


class PolicyEngine:
    """Evaluates case state and generates policy-compliant actions and regulatory filings."""

    @classmethod
    def evaluate_initial_actions(cls, context: Dict[str, Any]) -> List[ActionItem]:
        """Generates initial next-best actions before requested evidence is returned."""
        actions: List[ActionItem] = []
        fraud_prob = float(context.get("fraud_probability", 0.5))
        verdict = context.get("verdict", VerdictEnum.UNCERTAIN.value)
        pattern = context.get("pattern", PatternEnum.NONE)
        exposure = float(context.get("exposure_usd", 0.0))
        connected_cards = context.get("connected_cards", [])

        # Policy R3: Legitimate alert
        if verdict == VerdictEnum.LEGITIMATE.value:
            actions.append(
                ActionItem(
                    action=ActionEnum.CLOSE_NO_FRAUD,
                    route=ApprovalRouteEnum.AUTO,
                    reason="R3: Evidence confirms activity is consistent with legitimate cardholder profile.",
                )
            )
            return actions

        # Policy R5: Card testing sequence
        if pattern == PatternEnum.CARD_TESTING:
            actions.append(
                ActionItem(
                    action=ActionEnum.DECLINE_TRANSACTION,
                    route=ApprovalRouteEnum.L1,
                    reason="R5: Card testing sequence observed; decline flagged authorization.",
                )
            )
            actions.append(
                ActionItem(
                    action=ActionEnum.STEP_UP_AUTH,
                    route=ApprovalRouteEnum.AUTO,
                    reason="R5: Require step-up authentication before allowing further authorizations.",
                )
            )
            return actions

        # Policy R1: Weak signal or uncertain verdict (< 0.70)
        if fraud_prob < 0.70 or verdict == VerdictEnum.UNCERTAIN.value:
            actions.append(
                ActionItem(
                    action=ActionEnum.VERIFY_WITH_CUSTOMER,
                    route=ApprovalRouteEnum.AUTO,
                    reason=f"R1: Probability {fraud_prob:.2f} (< 0.70) rests on single/ambiguous signal; verify before blocking.",
                )
            )
            if exposure > 500.0:
                actions.append(
                    ActionItem(
                        action=ActionEnum.ESCALATE_TO_ANALYST,
                        route=ApprovalRouteEnum.AUTO,
                        reason="R8: Exposure exceeds $500 while verdict is uncertain; escalate for human analyst review.",
                    )
                )
            return actions

        # Strong fraud signal (> 0.70)
        route_block = ApprovalRouter.get_approval_route(ActionEnum.BLOCK_CARD, exposure)
        actions.append(
            ActionItem(
                action=ActionEnum.BLOCK_CARD,
                route=route_block,
                reason=f"R2: Strong fraud probability ({fraud_prob:.2f}); block card to prevent further losses.",
            )
        )
        actions.append(
            ActionItem(
                action=ActionEnum.CREATE_CASE,
                route=ApprovalRouteEnum.AUTO,
                reason="R2: Open internal fraud investigation record and register case in graph memory.",
            )
        )
        return actions

    @classmethod
    def evaluate_final_actions(
        cls,
        context: Dict[str, Any],
        initial_actions: List[ActionItem],
        assumed_evidence_response: str = "",
    ) -> Tuple[List[ActionItem], str]:
        """Generates final next-best actions after assumed responses from evidence requests."""
        if not assumed_evidence_response:
            return initial_actions, "nothing"

        final_actions: List[ActionItem] = []
        exposure = float(context.get("exposure_usd", 0.0))
        pattern = context.get("pattern", PatternEnum.NONE)
        connected_cards = context.get("connected_cards", [])
        shared_device = bool(context.get("shared_device", False))

        is_customer_denied = "denied" in assumed_evidence_response.lower() or "did not make" in assumed_evidence_response.lower()
        is_customer_confirmed = "recognized" in assumed_evidence_response.lower() or "confirmed they" in assumed_evidence_response.lower()

        if is_customer_confirmed:
            final_actions.append(
                ActionItem(
                    action=ActionEnum.CLOSE_NO_FRAUD,
                    route=ApprovalRouteEnum.AUTO,
                    reason="R3: Customer explicitly confirmed the transaction as legitimate.",
                )
            )
            what_changed = "Customer confirmed transaction upon verification; initial hold/verification resolved and alert closed as legitimate."
            return final_actions, what_changed

        if is_customer_denied:
            route_block = ApprovalRouter.get_approval_route(ActionEnum.BLOCK_CARD, exposure)
            final_actions.append(
                ActionItem(
                    action=ActionEnum.BLOCK_CARD,
                    route=route_block,
                    reason=f"R2: Customer explicitly denied authorization; exposure ${exposure:.2f}.",
                )
            )
            final_actions.append(
                ActionItem(
                    action=ActionEnum.CREATE_CASE,
                    route=ApprovalRouteEnum.AUTO,
                    reason="R2: Open internal fraud case record with customer denial documentation.",
                )
            )

            # Check if SAR required (exposure > $1,000 OR shared device OR undocumented pattern)
            if exposure >= 1000.0 or shared_device or pattern in [PatternEnum.UNDOCUMENTED, PatternEnum.CARD_TESTING]:
                final_actions.append(
                    ActionItem(
                        action=ActionEnum.FILE_REPORT,
                        route=ApprovalRouteEnum.L2,
                        reason="R2/R6: SAR filing mandatory due to confirmed unauthorized use and exposure / syndicate connection.",
                    )
                )

            if connected_cards:
                final_actions.append(
                    ActionItem(
                        action=ActionEnum.MONITOR_CONNECTED_CARDS,
                        route=ApprovalRouteEnum.AUTO,
                        reason=f"R6: Place {len(connected_cards)} connected cards under active monitoring.",
                    )
                )

            what_changed = (
                f"Customer denial confirmed unauthorized compromise. Escalated action from verification to "
                f"card blocking ({route_block.value}), case creation, and regulatory filing."
            )
            return final_actions, what_changed

        return initial_actions, "nothing"

    @classmethod
    def generate_sar(
        cls,
        context: Dict[str, Any],
        final_actions: List[ActionItem],
    ) -> SARRecord:
        """Constructs a compliant FinCEN SAR record if FILE_REPORT is in final actions."""
        has_file_report = any(a.action == ActionEnum.FILE_REPORT for a in final_actions)
        if not has_file_report:
            return SARRecord(
                file=False,
                reason="Policy thresholds for regulatory SAR filing not met; handled via internal case record only.",
                narrative="",
                subjects=[],
                total_amount_usd=0.0,
                activity_dates=[],
            )

        cid = context.get("customer_id", "")
        card_id = context.get("card_id", "")
        tid = context.get("flagged_txn_id", "")
        amt = float(context.get("exposure_usd", 0.0))
        date_str = str(context.get("opened_at", "2016-12-01"))[:10]
        pattern = context.get("pattern", "unauthorized_activity")
        device_hash = context.get("device_hash", "")
        connected_cards = context.get("connected_cards", [])

        subjects = [s for s in [cid, card_id] + connected_cards if s]
        if device_hash:
            subjects.append(device_hash)

        narrative = (
            f"On or about {date_str}, financial institution investigation identified unauthorized transactional activity "
            f"impacting customer {cid} on payment card {card_id}. Flagged transaction {tid} totaling ${amt:.2f} "
            f"was executed under patterns characteristic of {pattern}. Graph traversal analysis identified "
            f"connections across account profiles and device entities ({device_hash or 'network profile'}), "
            f"involving an aggregate suspicious exposure of ${amt:.2f}. "
            f"Cardholder inquiry verified the activity was unauthorized. The institution has blocked card {card_id}, "
            f"placed linked cards under protective monitoring, and submitted this Suspicious Activity Report pursuant to "
            f"FinCEN guidelines and Bank Fraud Policy R2/R6."
        )

        return SARRecord(
            file=True,
            reason="R2/R6: Confirmed unauthorized transaction exceeding reporting threshold or linked to multi-card syndicate.",
            narrative=narrative,
            subjects=subjects,
            total_amount_usd=amt,
            activity_dates=[date_str, date_str],
        )
