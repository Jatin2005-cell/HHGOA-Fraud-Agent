"""Unit tests for SAR Generation and Validation."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sar.sar_generator import SARGenerator
from sar.sar_validator import SARValidator


def test_sar_generation_mandated():
    # Case with exposure >= 1000 and confirmed fraud
    case_data = {
        "case_id": "HHG-010",
        "customer_id": "C10434",
        "card_id": "C10434-K1",
        "flagged_txn_id": "3506725",
        "verdict": "fraud",
        "fraud_pattern": "card_not_present_fraud",
        "exposure_usd": 1000.03,
        "connected_device_profiles": ["DEV_abc123"],
        "connected_card_ids": ["C10434-K2"],
        "final_next_best_action": [{"action": "BLOCK_CARD"}, {"action": "FILE_REPORT"}],
    }

    sar = SARGenerator.generate_for_case(case_data)
    assert sar.file is True
    assert sar.status == "GENERATED"
    assert "C10434" in sar.subjects
    assert len(sar.narrative.split()) >= 40


def test_sar_generation_not_required():
    case_data = {
        "case_id": "HHG-001",
        "customer_id": "C12382",
        "card_id": "C12382-K1",
        "flagged_txn_id": "3514030",
        "verdict": "legitimate",
        "fraud_pattern": "none",
        "exposure_usd": 0.0,
        "final_next_best_action": [{"action": "CLOSE_NO_FRAUD"}],
    }

    sar = SARGenerator.generate_for_case(case_data)
    assert sar.file is False
    assert sar.status == "NOT_REQUIRED"
    assert sar.narrative == ""


def test_sar_validator_incomplete_narrative():
    bad_sar = {
        "file": True,
        "reason": "Suspicious",
        "narrative": "Too short narrative.",
        "subjects": ["C001"],
        "total_amount_usd": 500.0,
        "activity_dates": ["2016-12-01"],
    }
    val = SARValidator.validate_sar(bad_sar, {"exposure_usd": 500.0})
    assert val.is_valid is False
    assert val.status == "REVIEW_REQUIRED"


if __name__ == "__main__":
    test_sar_generation_mandated()
    test_sar_generation_not_required()
    test_sar_validator_incomplete_narrative()
    print("test_sar.py: ALL PASS")
