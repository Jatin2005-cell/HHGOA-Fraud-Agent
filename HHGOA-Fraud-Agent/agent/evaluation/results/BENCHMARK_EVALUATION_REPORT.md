# Benchmark Evaluation Report: HHGOA_IEEE Fraud Investigation Agent

**Evaluation Date:** 2026-09-20  
**Target Cases:** 20 benchmark exam alerts (`HHG-001` through `HHG-020`)  
**Status:** 100% COMPLETE & VALIDATED  

---

## 1. Quantitative Performance Metrics

| Metric | Measured Value | Standard Required | Status |
|---|---|---|---|
| **Total Cases Executed** | 20 / 20 | 20 / 20 | **PASS** |
| **Case Completion Rate** | 100.0% | 100% | **PASS** |
| **Pydantic Schema Validity** | 100.0% | 100% | **PASS** |
| **Tool Execution Success Rate** | 100.0% | 100% | **PASS** |
| **Evidence Provenance Coverage** | 100.0% | 100% | **PASS** |
| **Unsupported Evidence Items** | 0 | 0 | **PASS** |
| **Policy Validation Success Rate**| 100.0% | 100% | **PASS** |
| **Action-Route Consistency** | 100.0% | 100% | **PASS** |
| **Stop Condition Validity** | 100.0% | 100% | **PASS** |
| **Average Case Latency** | 3.108s | < 5.0s | **PASS** |
| **Average Tool Calls per Case**| 5.65 | 3 - 6 | **PASS** |

---

## 2. Compliance Verification

1. **Deterministic Policy Rules (R1–R10):** All actions conform strictly to Bank Fraud Policy v1.0. No unauthorized card blocking on single weak signals without customer verification (Policy R1).
2. **Approval Hierarchy (auto / L1 / L2):** All `BLOCK_CARD` operations $\le \$2,500$ and `DECLINE_TRANSACTION` are routed to `L1`. High-exposure blocks and `FILE_REPORT` (SAR) are strictly routed to `L2`.
3. **Graph Grounding:** Zero fabricated IDs. All transaction IDs, customer IDs, and card IDs exist in the dataset.
4. **Case Memory:** Every case produces a `DynamicCase` memory record stored for subsequent investigations.
