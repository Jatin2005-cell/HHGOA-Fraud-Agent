"""Benchmark Cases Loader: Reads 20 exam cases from dataset/raw/case_pack.csv."""

import os
import pandas as pd
from typing import List, Optional
from agent.schemas.agent_output_schema import BenchmarkTrigger


def load_benchmark_cases(csv_path: Optional[str] = None) -> List[BenchmarkTrigger]:
    """Loads all 20 benchmark triggers without hardcoding case values."""
    if not csv_path:
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "raw", "case_pack.csv")
        )

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Case pack not found at {csv_path}")

    df = pd.read_csv(csv_path)
    triggers = []
    for _, row in df.iterrows():
        score = None
        if "risk_score" in row and pd.notna(row["risk_score"]):
            try:
                score = float(row["risk_score"])
            except (ValueError, TypeError):
                score = None

        trigger = BenchmarkTrigger(
            case_id=str(row["case_id"]).strip(),
            opened_at=str(row["opened_at"]).strip(),
            trigger_type=str(row["trigger_type"]).strip(),
            trigger_text=str(row["trigger_text"]).strip(),
            flagged_txn_id=str(row["flagged_txn_id"]).strip(),
            card_id=str(row["card_id"]).strip(),
            customer_id=str(row["customer_id"]).strip(),
            risk_score=score,
        )
        triggers.append(trigger)
    return triggers
