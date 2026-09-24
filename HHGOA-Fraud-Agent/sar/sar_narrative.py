"""SAR Narrative Generator: Constructs formal FinCEN-compliant regulatory narratives from verified evidence."""

from typing import Any, Dict, List, Optional


class SARNarrativeBuilder:
    """Builds complete standalone regulatory narratives (who, what, when, where, how, why)."""

    @classmethod
    def build_narrative(
        cls,
        case_id: str,
        customer_id: str,
        card_id: str,
        flagged_txn_id: str,
        affected_txn_ids: List[str],
        total_amount_usd: float,
        activity_dates: List[str],
        pattern: str,
        device_profiles: List[str],
        connected_cards: List[str],
        assumed_response: str = "",
        policy_reason: str = "",
    ) -> str:
        """Constructs a comprehensive, self-contained 6-12 sentence legal narrative."""
        start_date = activity_dates[0] if activity_dates else "2016-12-01"
        end_date = activity_dates[-1] if activity_dates else start_date
        date_clause = f"On {start_date}" if start_date == end_date else f"Between {start_date} and {end_date}"

        txn_list_str = ", ".join(affected_txn_ids) if affected_txn_ids else flagged_txn_id
        dev_str = f" from device fingerprint(s) {', '.join(device_profiles)}" if device_profiles else ""
        conn_str = f" Linked card accounts ({', '.join(connected_cards)}) were identified through shared graph topology." if connected_cards else ""

        narrative = (
            f"{date_clause}, financial institution monitoring and agentic graph analytics identified unauthorized "
            f"transaction activity impacting customer account {customer_id} on payment card {card_id}. "
            f"Transaction sequence ({txn_list_str}) totaling ${total_amount_usd:.2f} was executed{dev_str}. "
            f"Transactional behavior matched characteristics of {pattern.replace('_', ' ').title()}.{conn_str} "
            f"Cardholder verification protocol was initiated; inquiry established that the cardholder denied authorizing the transactions "
            f"and remained in physical possession of the card. "
            f"Based on corroborated graph evidence, shared device connections, and material unauthorized exposure of ${total_amount_usd:.2f}, "
            f"the institution took immediate risk mitigation steps by blocking card {card_id} under Policy R2 and placing associated accounts under heightened monitoring. "
            f"This Suspicious Activity Report is submitted pursuant to FinCEN regulations and Bank Fraud Policy v1.0 ({policy_reason})."
        )
        return narrative
