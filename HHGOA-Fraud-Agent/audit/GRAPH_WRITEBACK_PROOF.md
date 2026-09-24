# Graph Writeback & Readback Forensic Verification Report

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Challenge:** Hacker House Goa 2026  
**Audit Reference:** Phase 6.6 Specification (Section 9 & Section 10)  
**Execution Tier:** LEVEL B (Staged Local Graph Store)  

---

## 1. The Critical Distinction: Live TigerGraph vs. Staged Store

The previous Phase 6.5 audit reported:
`GRAPH WRITEBACK: PASS (Staged Graph Store)`

In accordance with Section 9 of the Phase 6.6 specification, this finding must be stated with complete transparency:
- Writing to CSV, JSON, SQLite, or Parquet files is **NOT** equivalent to writing into a live TigerGraph graph.
- Because a live TigerGraph instance is not running, **GRAPH WRITEBACK TO LIVE TIGERGRAPH = NOT VERIFIED**.
- However, **Case Writeback to the Staged Graph Simulation Store** is fully implemented, verified, and idempotent.

---

## 2. Technical Implementation Details

### Writeback Architecture
- **Service:** `case_management/graph_writeback.py` (`CaseWritebackService`)
- **Safety Boundary:** Strict separation from the Phase 4 read-only investigation MCP layer. The agent cannot execute arbitrary GSQL or destructive mutations.
- **Validation:** Enforces regex patterns:
  - Case ID: `^(HHG-\d{3}|CASE-\d{4}-\d+)$`
  - Card ID: `^C\d{5}-K\d+$`
  - Transaction ID: `^\d{7}$`
- **Writeback Destinations (Staged Graph Store):**
  1. **DynamicCase Vertices:** Appended/updated in `dataset/processed/dynamic_cases.csv`
     - Columns: `case_id`, `opened_at`, `closed_at`, `status`, `verdict`, `fraud_probability`, `pattern`, `pattern_description`, `exposure_usd`, `stop_reason`, `sar_filed`, `summary`
  2. **CASE_INVOLVES Edges:** Appended to `dataset/processed/edges_case_involves.csv`
     - Columns: `case_id`, `txn_id`, `is_flagged`, `is_confirmed_fraud`
  3. **CASE_ON_CARD Edges:** Appended to `dataset/processed/edges_case_on_card.csv`
     - Columns: `case_id`, `card_id`

### Readback Architecture
- **Service:** `case_management/graph_readback.py` (`CaseReadbackService`)
- **Verification Protocol:**
  1. Opens `dataset/processed/dynamic_cases.csv` to confirm the case vertex exists with correct schema and non-null verdict.
  2. Opens `edges_case_involves.csv` to confirm the incident relationship `CASE_INVOLVES(case_id -> txn_id)` is persisted.
  3. Opens `edges_case_on_card.csv` to confirm the card relationship `CASE_ON_CARD(case_id -> card_id)` is persisted.
  4. Dispatches an audit event `GRAPH_READBACK_VERIFIED` to `case_management/audit.log`.

---

## 3. Empirical Verification Across Benchmark Cases

The writeback and readback lifecycle was empirically verified across benchmark cases:

| Case ID | Flagged Txn | Target Card | Status | Verdict | Staged Vertices Written | Staged Edges Written | Readback Status |
|---|---|---|---|---|---|---|---|
| **HHG-001** | 3514030 | C12382-K1 | RESOLVED | legitimate | DynamicCase:HHG-001 | CASE_INVOLVES, CASE_ON_CARD | **VERIFIED (Level B)** |
| **HHG-002** | 3478782 | C11891-K1 | RESOLVED | legitimate | DynamicCase:HHG-002 | CASE_INVOLVES, CASE_ON_CARD | **VERIFIED (Level B)** |
| **HHG-003** | 3530164 | C08623-K2 | RESOLVED | fraud | DynamicCase:HHG-003 | CASE_INVOLVES, CASE_ON_CARD | **VERIFIED (Level B)** |
| **HHG-004** | 3583227 | C08106-K1 | RESOLVED | fraud | DynamicCase:HHG-004 | CASE_INVOLVES, CASE_ON_CARD | **VERIFIED (Level B)** |
| **HHG-014** | 3478561 | C13487-K1 | RESOLVED | fraud | DynamicCase:HHG-014 | CASE_INVOLVES, CASE_ON_CARD | **VERIFIED (Level B)** |
| **HHG-020** | 3514100 | C12265-K2 | RESOLVED | legitimate | DynamicCase:HHG-020 | CASE_INVOLVES, CASE_ON_CARD | **VERIFIED (Level B)** |

### Verified Output Sample from `dataset/processed/dynamic_cases.csv`
```csv
case_id,opened_at,closed_at,status,verdict,fraud_probability,pattern,pattern_description,exposure_usd,stop_reason,sar_filed,summary
HHG-001,2026-09-20 12:49:22,2026-09-20 13:05:53,RESOLVED,legitimate,0.12,none,,0.0,sufficient_evidence_reached,False,"Investigation of alert HHG-001 (risk_score) determined a fraud probability of 0.12 consistent with None..."
HHG-003,2026-09-20 12:49:22,2026-09-20 13:05:53,RESOLVED,fraud,0.86,card_not_present_fraud,"Online transaction unauthorized dispute",3530164.0,sufficient_evidence_reached,True,"Investigation of alert HHG-003 (customer_report) determined a fraud probability of 0.86 consistent with Card Not Present Fraud..."
HHG-014,2026-09-20 12:49:22,2026-09-20 13:05:53,RESOLVED,fraud,0.94,device_fingerprint_sharing,"Shared device across 52 payment cards",3478561.0,sufficient_evidence_reached,True,"Investigation of alert HHG-014 (analyst_request) determined a fraud probability of 0.94 consistent with Device Fingerprint Sharing..."
```

---

## 4. Final Verdict

```
============================================================
GRAPH WRITEBACK TO TIGERGRAPH:  NOT VERIFIED
GRAPH READBACK FROM TIGERGRAPH: NOT VERIFIED
STAGED STORE WRITEBACK:         VERIFIED (Level B)
STAGED STORE READBACK:          VERIFIED (Level B)
============================================================
```
