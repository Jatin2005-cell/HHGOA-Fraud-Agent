"""Evidence and Pattern Evaluation Engine.

Differentiates:
- Observed Evidence (factual graph/dataset observations)
- Inferences (hypotheses supported by patterns)
- Uncertainty (unknowns and missing evidence)
"""

from typing import Any, Dict, List, Tuple
from agent.schemas.investigation_schema import PatternEnum, VerdictEnum


class EvidenceManager:
    """Evaluates graph signals to determine pattern, probability, and evidence classification."""

    @classmethod
    def evaluate_pattern_and_risk(
        cls,
        state_data: Dict[str, Any],
        graph_entities: Dict[str, Any],
        tool_results: List[Dict[str, Any]],
    ) -> Tuple[PatternEnum, str, float, str, float, List[str], List[str], List[str]]:
        """
        Determines:
            pattern, pattern_description, fraud_prob, verdict, exposure, affected_txns, supporting_ev, contradicting_ev
        """
        txn = graph_entities.get("target_transaction", {})
        tid = str(txn.get("txn_id", state_data.get("flagged_txn_id", "")))
        channel = txn.get("channel", "online")
        amt = float(txn.get("amount", 0.0))
        risk_score = float(txn.get("risk_score", state_data.get("risk_score") or 0.5))
        trigger_type = state_data.get("trigger_type", "risk_score")
        trigger_text = state_data.get("trigger_text", "")

        supporting: List[str] = []
        contradicting: List[str] = []
        affected_txns: List[str] = [tid] if tid else []
        exposure = amt

        # Signals from tools
        card_window = None
        device_neighbors = None
        region_anomaly = None
        customer_hist = None

        for tc in tool_results:
            tname = tc.get("tool_name")
            res = tc.get("results", {})
            if tname == "get_card_transaction_window":
                card_window = res
            elif tname == "find_device_neighbors":
                device_neighbors = res
            elif tname == "find_region_anomalies":
                region_anomaly = res
            elif tname == "get_customer_history":
                customer_hist = res

        # 1. Pattern 1: Card Testing
        if card_window and card_window.get("card_testing_sequence_detected"):
            small_cnt = card_window.get("sub_5_dollar_auth_count", 0)
            max_amt = card_window.get("max_txn_amount", 0.0)
            supporting.append(f"Observed card testing sequence: {small_cnt} micro-authorizations (<$5) followed by larger authorization (${max_amt:.2f}).")
            pattern = PatternEnum.CARD_TESTING
            pattern_desc = ""
            fraud_prob = 0.88
            verdict = VerdictEnum.FRAUD.value
            return pattern, pattern_desc, fraud_prob, verdict, exposure, affected_txns, supporting, contradicting

        # 2. Shared Device Syndicate / Device Sharing
        if device_neighbors and device_neighbors.get("connected_cards_count", 0) >= 5:
            cards_cnt = device_neighbors.get("connected_cards_count", 0)
            txns_cnt = device_neighbors.get("connected_transactions_count", 0)
            supporting.append(f"Online transaction linked to shared device profile observed across {cards_cnt} cards and {txns_cnt} transactions.")
            pattern = PatternEnum.UNDOCUMENTED
            pattern_desc = (
                f"Shared device syndicate: Device is shared across {cards_cnt} cards spanning multiple customers, "
                f"generating coordinated high-velocity transactions across the network."
            )
            fraud_prob = 0.92
            verdict = VerdictEnum.FRAUD.value
            return pattern, pattern_desc, fraud_prob, verdict, exposure, affected_txns, supporting, contradicting

        # 3. Out of Region Use (in-person)
        if region_anomaly:
            is_new = region_anomaly.get("is_new_billing_region", False)
            prior = region_anomaly.get("flagged_region_prior_count", 0)
            reg = region_anomaly.get("flagged_region", "")
            if is_new and prior == 0:
                supporting.append(f"In-person transaction in billing region {reg} where cardholder has zero prior transaction history.")
                pattern = PatternEnum.OUT_OF_REGION_USE
                pattern_desc = ""
                # Could be a trip or clone
                fraud_prob = 0.65
                verdict = VerdictEnum.UNCERTAIN.value
                return pattern, pattern_desc, fraud_prob, verdict, exposure, affected_txns, supporting, contradicting
            else:
                contradicting.append(f"Cardholder has {prior} prior transactions in billing region {reg}, consistent with normal home or travel patterns.")
                pattern = PatternEnum.NONE
                pattern_desc = ""
                fraud_prob = 0.12
                verdict = VerdictEnum.LEGITIMATE.value
                return pattern, pattern_desc, fraud_prob, verdict, 0.0, [], supporting, contradicting

        # 4. Customer Report Disputed
        if trigger_type == "customer_report":
            supporting.append("Cardholder initiated a dispute stating they did not authorize this transaction.")
            # Check customer history
            if customer_hist:
                avg_amt = customer_hist.get("avg_amount", 0.0)
                if amt > avg_amt * 3:
                    supporting.append(f"Transaction amount ${amt:.2f} significantly exceeds customer average spend (${avg_amt:.2f}).")
            
            # If new device or online
            if channel == "online":
                pattern = PatternEnum.CARD_NOT_PRESENT_FRAUD
                pattern_desc = ""
                fraud_prob = 0.78
                verdict = VerdictEnum.FRAUD.value
            else:
                pattern = PatternEnum.UNDOCUMENTED
                pattern_desc = "Disputed in-person transaction; cardholder claims card remained in possession."
                fraud_prob = 0.72
                verdict = VerdictEnum.FRAUD.value
            return pattern, pattern_desc, fraud_prob, verdict, exposure, affected_txns, supporting, contradicting

        # 5. Risk Score Alert Alone
        if trigger_type == "risk_score":
            supporting.append(f"Bank real-time detection model flagged transaction with risk score {risk_score:.2f}.")
            if customer_hist:
                avg_amt = customer_hist.get("avg_amount", 0.0)
                if amt <= avg_amt * 1.5:
                    contradicting.append(f"Amount ${amt:.2f} is within normal spending baseline for customer (${avg_amt:.2f}).")
            
            # Policy R1: Risk score alone is a weak signal
            fraud_prob = min(0.68, risk_score)
            pattern = PatternEnum.CARD_NOT_PRESENT_FRAUD if channel == "online" else PatternEnum.NONE
            pattern_desc = ""
            verdict = VerdictEnum.UNCERTAIN.value if fraud_prob >= 0.30 else VerdictEnum.LEGITIMATE.value
            if verdict == VerdictEnum.LEGITIMATE.value:
                exposure = 0.0
                affected_txns = []
            return pattern, pattern_desc, fraud_prob, verdict, exposure, affected_txns, supporting, contradicting

        # Default fallback
        pattern = PatternEnum.NONE
        pattern_desc = ""
        fraud_prob = 0.10
        verdict = VerdictEnum.LEGITIMATE.value
        return pattern, pattern_desc, fraud_prob, verdict, 0.0, [], supporting, contradicting
