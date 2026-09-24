"""Document Store holding policy rules, pattern typologies, and regulatory standards."""

from typing import Any, Dict, List, Optional


class DocumentStore:
    """Stores and serves textual knowledge for Fraud Policy, Typologies, and FinCEN Guidance."""

    POLICY_RULES: Dict[str, Dict[str, Any]] = {
        "R1": {
            "title": "Verify before you block on a weak signal",
            "text": "If the case rests on a single signal (including a risk score alone) and your assessed fraud probability is below 0.70, recommend VERIFY_WITH_CUSTOMER or STEP_UP_AUTH before any block. Blocking a legitimate customer on one signal is a policy breach.",
            "threshold_prob": 0.70,
            "actions": ["VERIFY_WITH_CUSTOMER", "STEP_UP_AUTH"],
        },
        "R2": {
            "title": "Customer denies the transaction",
            "text": "Recommend BLOCK_CARD and CREATE_CASE. Add FILE_REPORT if exposure exceeds $1,000 or the case connects to a shared device profile or another card's fraud.",
            "actions": ["BLOCK_CARD", "CREATE_CASE", "FILE_REPORT"],
        },
        "R3": {
            "title": "Customer confirms the transaction",
            "text": "Recommend CLOSE_NO_FRAUD. Note the confirmation in the case file.",
            "actions": ["CLOSE_NO_FRAUD"],
        },
        "R4": {
            "title": "No reply within 24 hours",
            "text": "Recommend MONITOR_CARD and DECLINE_TRANSACTION for pending authorizations. Escalate if exposure exceeds $500.",
            "actions": ["MONITOR_CARD", "DECLINE_TRANSACTION", "ESCALATE_TO_ANALYST"],
        },
        "R5": {
            "title": "Card testing",
            "text": "Three or more small online authorizations on one card within an hour, followed by a larger purchase: recommend DECLINE_TRANSACTION and STEP_UP_AUTH. If a purchase over $100 has already cleared, recommend BLOCK_CARD.",
            "actions": ["DECLINE_TRANSACTION", "STEP_UP_AUTH", "BLOCK_CARD"],
        },
        "R6": {
            "title": "Shared origin",
            "text": "When several cards show fraud from the same device profile, the same billing region, or the same recipient email in one window, name the shared element, recommend CREATE_CASE and FILE_REPORT, and MONITOR_CONNECTED_CARDS for every card that shares it.",
            "actions": ["CREATE_CASE", "FILE_REPORT", "MONITOR_CONNECTED_CARDS"],
        },
        "R7": {
            "title": "Disputed but legitimate",
            "text": "When the customer disputes a charge that matches their own recurring pattern (same merchant, same amount, monthly), recommend CREATE_CASE, VERIFY_WITH_CUSTOMER, and WARN_CUSTOMER. Do not block.",
            "actions": ["CREATE_CASE", "VERIFY_WITH_CUSTOMER", "WARN_CUSTOMER"],
        },
        "R8": {
            "title": "Escalate when uncertain and exposed",
            "text": "If the verdict is uncertain and exposure exceeds $500, or the evidence conflicts, recommend ESCALATE_TO_ANALYST.",
            "actions": ["ESCALATE_TO_ANALYST"],
        },
        "R9": {
            "title": "Undocumented patterns",
            "text": "When activity fits none of the known patterns but the evidence shows coordinated or repeated abuse across customers, recommend CREATE_CASE, FILE_REPORT, and ESCALATE_TO_ANALYST, and describe the pattern in your own words. Do not force it into a known category.",
            "actions": ["CREATE_CASE", "FILE_REPORT", "ESCALATE_TO_ANALYST"],
        },
        "R10": {
            "title": "Never BLOCK_ALL_CARDS unless multiple compromises",
            "text": "Never BLOCK_ALL_CARDS unless at least two of the customer's cards show confirmed fraud or the customer's credentials are confirmed compromised.",
            "actions": ["BLOCK_ALL_CARDS"],
        },
    }

    PATTERNS: Dict[str, Dict[str, str]] = {
        "card_testing": {
            "name": "Card Testing",
            "description": "A stolen card number is checked before use: three or more tiny online authorizations, often under $5, then a larger purchase. Confirmed by the sequence itself. Governed by Policy R5.",
        },
        "card_not_present_fraud": {
            "name": "Card-Not-Present Fraud",
            "description": "The card number is used online without the card. Amounts and products that don't fit the cardholder's history, often in a burst of two to four within 48 hours. Ambiguous on its own; requires verification under Policy R1-R4.",
        },
        "card_not_present_new_device": {
            "name": "Card-Not-Present from New Device",
            "description": "Online card-not-present transaction where the device profile is marked New for this account, occasionally behind an anonymous proxy.",
        },
        "out_of_region_use": {
            "name": "Out-of-Region Use",
            "description": "Card-present in-person purchases in a billing region where cardholder has zero history, while normal activity continues at home. Multiple days in a single novel region may indicate travel. Governed by Policy R2, R3.",
        },
        "account_takeover": {
            "name": "Account Takeover",
            "description": "Mixed-channel activity inconsistent with cardholder profile, accompanied by device changes, contact updates, or credential resets.",
        },
        "undocumented": {
            "name": "Undocumented Fraud Pattern",
            "description": "Novel or coordinated abuse not fitting standard categories (e.g. shared device syndicates spanning dozens of cards, or threshold avoidance structuring under $500). Governed by Policy R6, R9.",
        },
    }

    SAR_GUIDANCE: Dict[str, str] = {
        "filing_standard": "FinCEN guidance requires SAR filing when transactions involve aggregate funds >= $1,000 and the institution knows, suspects, or has reason to suspect unauthorized use, insider abuse, or structuring.",
        "narrative_structure": "A sufficient narrative must explain who, what, when, where, how, and why the activity is suspicious. It must stand independently as a complete legal record for regulatory review.",
    }

    @classmethod
    def get_policy_rule(cls, rule_id: str) -> Optional[Dict[str, Any]]:
        return cls.POLICY_RULES.get(rule_id)

    @classmethod
    def get_all_policy_rules(cls) -> Dict[str, Dict[str, Any]]:
        return cls.POLICY_RULES

    @classmethod
    def get_pattern_info(cls, pattern_id: str) -> Optional[Dict[str, str]]:
        return cls.PATTERNS.get(pattern_id)
