# Phase 5: AI Agent + GraphRAG + Investigation Orchestrator Specification

**Document Version:** 1.0.0  
**Project:** Hacker House Goa 2026 — `HHGOA_IEEE` Fraud Investigation  
**Component:** `agent/`  
**Status:** Validated on all 20 Benchmark Cases (`HHG-001` through `HHG-020`) — 100% Pass  

---

## 1. Executive Summary & Architecture

Phase 5 establishes an autonomous, evidence-driven Fraud Investigation Agent that operates on top of the TigerGraph Model Context Protocol (MCP) layer delivered in Phase 4.

Rather than allowing an LLM to generate unrestrained database queries or execute destructive financial operations, the agent architecture enforces a strict separation of concerns:
1. **TigerGraph** is the immutable source of truth for graph topology and transactional evidence.
2. **TigerGraph MCP** exposes pre-compiled, security-vetted GSQL investigation queries.
3. **GraphRAG & Case Memory** retrieves relevant subgraphs, previous closed case precedents, and policy typologies.
4. **Finite State Machine** enforces a deterministic 17-state investigation loop.
5. **Deterministic Policy Engine** evaluates Bank Fraud Policy v1.0 (Rules R1 to R10) and determines approval hierarchy (`auto`, `L1`, `L2`).

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        INVESTIGATION TRIGGER                               │
│         (Risk Score Alert / Customer Dispute / Analyst Request)            │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    INVESTIGATION STATE MACHINE (17 States)                 │
│                                                                            │
│  TRIGGERED ──► INITIALIZED ──► EVIDENCE_COLLECTION ──► GRAPH_ANALYSIS      │
│                                                                │           │
│  RISK_ASSESSMENT ◄── CASE_MEMORY_RETRIEVAL ◄───────────────────┘           │
│        │                                                                   │
│        ▼                                                                   │
│  PATTERN_ASSESSMENT ──► UNCERTAINTY_ASSESSMENT ──► EVIDENCE_DECISION       │
│                                                          │                 │
│      ┌───────────────── REQUEST_MORE_EVIDENCE ◄──────────┤                 │
│      │                            │                      │                 │
│      │                            ▼                      ▼                 │
│      │                   EVIDENCE_COLLECTION    SUFFICIENT_EVIDENCE        │
│      │                                                   │                 │
│      └───────────────────────────────────────────► NEXT_BEST_ACTION        │
│                                                          │                 │
│  COMPLETED ◄── MEMORY_UPDATE ◄── CASE_SUMMARY ◄── APPROVAL_ROUTING         │
└───────────────────────────────────────────────────────────▲────────────────┘
                                                            │
┌───────────────────────────────────────────────────────────┴────────────────┐
│                        TIGERGRAPH MCP TOOL LAYER                           │
│  - get_transaction_context           - get_customer_history                │
│  - get_card_transaction_window       - find_connected_cards                │
│  - find_device_neighbors             - analyze_temporal_pattern            │
│  - find_region_anomalies             - get_investigation_subgraph          │
│  - find_similar_closed_cases                                               │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Investigation State Machine

The agent enforces an explicit state machine with strict transition guards:

| State | Purpose | Allowed Next States |
|---|---|---|
| `TRIGGERED` | Case alert ingested from `case_pack.csv`. | `INITIALIZED`, `FAILED` |
| `INITIALIZED` | Anchors loaded (`flagged_txn_id`, `customer_id`, `card_id`). | `EVIDENCE_COLLECTION`, `FAILED` |
| `EVIDENCE_COLLECTION` | Dynamic execution of TigerGraph MCP investigation queries. | `GRAPH_ANALYSIS`, `FAILED` |
| `GRAPH_ANALYSIS` | Entity extraction and graph relationship normalization. | `CASE_MEMORY_RETRIEVAL`, `FAILED` |
| `CASE_MEMORY_RETRIEVAL` | Precedent search across 5,565 closed cases. | `RISK_ASSESSMENT`, `FAILED` |
| `RISK_ASSESSMENT` | Separates alert signal from graph-grounded probability. | `PATTERN_ASSESSMENT`, `FAILED` |
| `PATTERN_ASSESSMENT` | Identifies pattern (e.g. `card_testing`, shared device ring). | `UNCERTAINTY_ASSESSMENT`, `FAILED` |
| `UNCERTAINTY_ASSESSMENT`| Evaluates evidence completeness and conflicting signals. | `EVIDENCE_DECISION`, `FAILED` |
| `EVIDENCE_DECISION` | Assesses if additional evidence is required under Policy R1. | `REQUEST_MORE_EVIDENCE`, `SUFFICIENT_EVIDENCE`, `ESCALATED`, `FAILED` |
| `REQUEST_MORE_EVIDENCE` | Issues simulated customer/analyst inquiry. | `EVIDENCE_COLLECTION`, `SUFFICIENT_EVIDENCE`, `NEXT_BEST_ACTION`, `FAILED` |
| `SUFFICIENT_EVIDENCE` | Transitions to action formulation. | `NEXT_BEST_ACTION`, `FAILED` |
| `NEXT_BEST_ACTION` | Synthesizes initial and final action recommendations. | `POLICY_VALIDATION`, `FAILED` |
| `POLICY_VALIDATION` | Validates recommendations against Policy Rules R1–R10. | `APPROVAL_ROUTING`, `FAILED` |
| `APPROVAL_ROUTING` | Assigns governance level: `auto`, `L1`, or `L2`. | `CASE_SUMMARY`, `FAILED` |
| `CASE_SUMMARY` | Compiles 2–6 sentence analyst summary and FinCEN SAR narrative.| `MEMORY_UPDATE`, `FAILED` |
| `MEMORY_UPDATE` | Writes `DynamicCase` vertex record into TigerGraph memory. | `COMPLETED`, `ESCALATED`, `FAILED` |
| `COMPLETED` | Generates final compliant 3-part JSON output. | Terminal state |

---

## 3. Tool Selection Logic

Rather than calling all 9 tools blindly, `ToolSelector` applies evidence-driven heuristics:

1. **Step 1 (Mandatory Anchor):** Always call `get_transaction_context(flagged_txn_id)` to establish customer, card, channel, and direct case links.
2. **Online Channel Branch:**
   * If online transaction, call `find_device_neighbors(flagged_txn_id)` to check for shared device syndicates.
   * Call `get_card_transaction_window(card_id, center_ts, window_hours=24)` to evaluate velocity and micro-authorizations (<$5).
3. **In-Person Channel Branch:**
   * Call `find_region_anomalies(card_id, flagged_txn_id)` to compare the flagged billing region against home distribution.
4. **Customer Profile & Connected Cards:**
   * Call `get_customer_history(customer_id)` if spend exceeds $100 or alert is disputed.
   * Call `find_connected_cards(card_id)` to check multi-card exposure.
5. **Memory Retrieval:**
   * Call `find_similar_closed_cases(customer_id, pattern)` to ground reasoning in historical precedents.

Average tool calls per case across benchmark: **5.65 tools**.

---

## 4. GraphRAG & Case Memory Implementation

The GraphRAG subsystem (`agent/graph_rag/`) bridges structured graph analytics with LLM reasoning:

* **`document_store.py`:** Knowledge store encoding Bank Fraud Policy v1.0, pattern typologies, and FinCEN SAR filing standards.
* **`case_memory.py`:** Searches 5,565 closed cases (July–October 2016) for matching customers, cards, and patterns. Converts case precedents into provenanced evidence claims.
* **`evidence_ranker.py`:** Weights and ranks evidence claims (Graph: 1.0, Customer: 0.95, Document: 0.85). Deduplicates claims and enforces that every claim references verified entity IDs.
* **`graph_context_builder.py`:** Normalizes MCP query outputs into compact, structured entity packets without raw data dumps.

---

## 5. Fraud Policy Engine & Approval Routing

The policy engine enforces deterministic governance over agent recommendations:

### Policy Rules Implemented:
* **R1:** Verify before blocking on weak signals (probability < 0.70). Blocking on a single signal is rejected and replaced with `VERIFY_WITH_CUSTOMER`.
* **R2:** Customer denial triggers `BLOCK_CARD` and `CREATE_CASE`. If exposure > $1,000 or shared device ring, add `FILE_REPORT`.
* **R3:** Customer confirmation triggers `CLOSE_NO_FRAUD`.
* **R4:** No customer reply within 24h triggers `MONITOR_CARD` and `DECLINE_TRANSACTION`.
* **R5:** Card testing sequence (3+ small auths < $5 followed by larger purchase) triggers `DECLINE_TRANSACTION` and `STEP_UP_AUTH`. If cleared > $100, trigger `BLOCK_CARD`.
* **R6:** Shared device or regional origin across cards triggers `CREATE_CASE`, `FILE_REPORT`, and `MONITOR_CONNECTED_CARDS`.
* **R7:** Disputed charges matching recurring customer history trigger `CREATE_CASE`, `VERIFY_WITH_CUSTOMER`, and `WARN_CUSTOMER` (no block).
* **R8:** Uncertain verdict with exposure > $500 triggers `ESCALATE_TO_ANALYST`.
* **R9:** Undocumented patterns with coordinated abuse trigger `CREATE_CASE`, `FILE_REPORT`, and `ESCALATE_TO_ANALYST`.
* **R10:** Never `BLOCK_ALL_CARDS` unless multiple customer cards show confirmed compromise.

### Approval Routing Matrix:
* `auto`: `ALLOW_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`, `GENERATE_REPORT`, `CREATE_CASE`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`
* `L1` (Team Lead): `DECLINE_TRANSACTION`, `BLOCK_CARD` when exposure $\le \$2,500$
* `L2` (Fraud Manager): `BLOCK_CARD` when exposure $> \$2,500$, `BLOCK_ALL_CARDS` always, `FILE_REPORT` always

---

## 6. Controlled Additional Evidence Requests

In compliance with hackathon regulations:
* No real customers are contacted.
* No real financial transactions are executed.
* When additional evidence is required under Policy R1 or R2, the agent generates an `EvidenceRequest` with an explicit assumed response:
  * Example: `"SIMULATED TEST EVIDENCE: Customer confirmed dispute, stating they did not make this $49.00 purchase and remained in possession of the card."`
* The request is recorded in `evidence_requests` with `asked_after_step` and `assumed_response`.
* The policy engine evaluates both `initial` and `final` next best actions, recording the transition in `what_changed`.

---

## 7. Stop Conditions

The agent terminates investigation deterministically using 7 conditions (`agent/core/stop_manager.py`):
1. **Definitive Fraud:** Fraud probability $\ge 0.85$ supported by $\ge 2$ independent graph signals (`sufficient_evidence_for_action`).
2. **Definitive Legitimate:** Fraud probability $\le 0.15$ supported by $\ge 2$ signals (`sufficient_evidence_for_action`).
3. **Verification Settled:** Direct customer verification received (`verification_response_settled`).
4. **Ceiling Limit:** Maximum investigation steps (10) reached (`maximum_steps_reached`).
5. **Tool Failure:** Communication error with database terminates safely without corrupting memory (`tool_failure`).

---

## 8. Benchmark Evaluation & Results

The benchmark suite was executed across all 20 exam cases (`HHG-001` to `HHG-020`) loaded directly from `dataset/raw/case_pack.csv`:

```
==================================================
BENCHMARK EVALUATION SUMMARY (20/20 PASS)
==================================================
Total Cases:                    20
Completion Rate:                100.0%
Schema Validity:                100.0%
Evidence Provenance Coverage:   100.0%
Unsupported Evidence Count:     0
Policy Validation Success:      100.0%
Action-Route Consistency:       100.0%
Average Latency per Case:       3.108s
Average Tool Calls per Case:    5.65
==================================================
```

All 20 answer files are formatted in strict accordance with the official 3-part specification and stored in:
- `cases/HHG-001.json` through `cases/HHG-020.json`
- `agent/evaluation/results/`

---

## 9. Quickstart & Commands (Windows PowerShell)

### 1. Environment Setup
```powershell
# Copy configuration
copy agent\config\example.env agent\config\.env
```

### 2. Run Automated Test Suite (13 Tests)
```powershell
python agent/tests/run_all_tests.py
```
*Expected Output: `TEST RESULTS: 13 PASSED, 0 FAILED (TOTAL 13)`*

### 3. Run Benchmark Evaluation (All 20 Cases)
```powershell
python -m agent.evaluation.benchmark_runner
```

### 4. View Evaluation Report
```powershell
Get-Content agent\evaluation\results\BENCHMARK_EVALUATION_REPORT.md
```
