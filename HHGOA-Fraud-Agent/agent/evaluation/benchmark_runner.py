"""Benchmark Runner: Executes the AI Agent across all 20 HHGOA exam cases."""

import os
import json
import time
from typing import List, Optional
from agent.schemas.agent_output_schema import AgentOutputSchema
from agent.core.investigation_orchestrator import InvestigationOrchestrator
from .benchmark_cases import load_benchmark_cases
from .evaluation_metrics import evaluate_benchmark_results


class BenchmarkRunner:
    """Orchestrates benchmark evaluation on HHG-001 through HHG-020."""

    def __init__(self, orchestrator: Optional[InvestigationOrchestrator] = None):
        self.orchestrator = orchestrator or InvestigationOrchestrator()

    def run_all(
        self,
        output_dir: Optional[str] = None,
        official_cases_dir: Optional[str] = None,
    ) -> List[AgentOutputSchema]:
        """Runs all 20 cases, serializes answers, and computes evaluation report."""
        if not output_dir:
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "results"))
        os.makedirs(output_dir, exist_ok=True)

        if not official_cases_dir:
            official_cases_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "cases")
            )
        os.makedirs(official_cases_dir, exist_ok=True)

        triggers = load_benchmark_cases()
        print(f"Loaded {len(triggers)} benchmark cases from case_pack.csv.")

        results: List[AgentOutputSchema] = []
        all_cases_dict = {}

        for idx, trigger in enumerate(triggers, 1):
            print(f"[{idx:02d}/20] Investigating {trigger.case_id} ({trigger.trigger_type})...", end="", flush=True)
            res = self.orchestrator.investigate(trigger)
            results.append(res)

            res_dict = res.model_dump()
            all_cases_dict[trigger.case_id] = res_dict

            # Write to official cases/ folder
            case_path = os.path.join(official_cases_dir, f"{trigger.case_id}.json")
            with open(case_path, "w", encoding="utf-8") as f:
                json.dump(res_dict, f, indent=2)

            # Write to evaluation results folder
            eval_case_path = os.path.join(output_dir, f"{trigger.case_id}.json")
            with open(eval_case_path, "w", encoding="utf-8") as f:
                json.dump(res_dict, f, indent=2)

            print(f" Done ({res.latency_s:.2f}s, {res.tool_calls} tools, verdict: {res.case.verdict.value})")

        # Write aggregated results
        all_cases_path = os.path.join(output_dir, "all_cases.json")
        with open(all_cases_path, "w", encoding="utf-8") as f:
            json.dump(all_cases_dict, f, indent=2)

        # Compute evaluation metrics
        metrics = evaluate_benchmark_results(results)
        metrics_path = os.path.join(output_dir, "benchmark_report.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics.model_dump(), f, indent=2)

        print("\n" + "=" * 50)
        print("BENCHMARK EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Total Cases: {metrics.total_cases}")
        print(f"Completion Rate: {metrics.completion_rate_pct}%")
        print(f"Schema Validity: {metrics.schema_validity_pct}%")
        print(f"Evidence Provenance: {metrics.evidence_provenance_coverage_pct}%")
        print(f"Unsupported Evidence Count: {metrics.unsupported_evidence_count}")
        print(f"Action-Route Consistency: {metrics.action_route_consistency_pct}%")
        print(f"Average Latency: {metrics.avg_latency_s}s")
        print(f"Average Tool Calls: {metrics.avg_tool_calls_per_case}")
        print("=" * 50)

        return results


if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run_all()
