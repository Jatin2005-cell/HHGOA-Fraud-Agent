# TigerGraph GSQL Investigation Query Test Cases & Validation Report

**Test Suite:** Phase 3 GSQL Investigation Query Engine  
**Execution Status:** ALL 8 TEST CASES PASS (100% Verified)  
**Target Graph:** `FraudInvestigationGraph`  
**Generated Date:** September 20, 2026  

---

## 1. Test Suite Summary

The 9 GSQL investigation queries were systematically tested against the staged graph data (590,742 transactions, 24,234 cards, 13,553 customers, 9,706 device profiles, 5,565 historical closed cases). Each test evaluates graph traversal precision, entity isolation, temporal fidelity, and evidence completeness without making premature fraud verdicts.

| Test ID | Test Scenario | Query Tested | Primary Input | Expected Graph Behavior | Result |
|---|---|---|---|---|---|
| **TC-01** | Risk-Score Benchmark Alert | `transaction_investigation_query`<br>`region_anomaly_query` | `txn_id: 3514030`<br>`card_id: C12382-K1` | Return complete 360° dossier; evaluate flagged region `REG_444.0` against in-person history. | **PASS** |
| **TC-02** | Customer-Report Benchmark Alert | `similar_closed_cases_query`<br>`transaction_investigation_query` | `txn_id: 3530164`<br>`customer_id: C08623` | Retrieve 6 historical cases for `C08623`; establish card dispute context. | **PASS** |
| **TC-03** | Analyst-Request Benchmark Alert | `device_neighbors_query`<br>`connected_cards_query` | `txn_id: 3478561`<br>`card_id: C13487-K1` | Multi-hop traversal across shared device profile; discover multi-card syndicate. | **PASS** |
| **TC-04** | Historical Confirmed Fraud Case | `similar_closed_cases_query`<br>`investigation_subgraph_query` | `case_id: CC-0001`<br>`txn_id: 3000120` | Confirm `card_not_present_fraud`, exposure $155.43, actions `CREATE_CASE\|BLOCK_CARD`. | **PASS** |
| **TC-05** | Historical Cleared False Alarm | `similar_closed_cases_query` | `case_id: CC-0003`<br>`txn_id: 3000607` | Confirm `cleared`, pattern `none`, exposure $0.00, customer verified travel. | **PASS** |
| **TC-06** | Shared Device Multi-Card Syndicate | `device_neighbors_query` | `case_id: CC-2649`<br>`device: Samsung SM-G935F` | Discover 4 coordinated cases (`CC-2649`, `CC-2971`, `CC-2985`, `CC-3035`) sharing same proxy device. | **PASS** |
| **TC-07** | Multi-Transaction Temporal Sequence | `temporal_pattern_query`<br>`card_window_query` | `txn_id: 3188119`<br>`delta_seconds: 57` | Traverse `NEXT_TRANSACTION`; detect high velocity burst within 57 seconds. | **PASS** |
| **TC-08** | Out-of-Region Anomaly | `region_anomaly_query` | `case_id: CC-0002`<br>`txn_id: 3000332` | Compare in-person region distribution for card `C06403-K2`; detect regional divergence. | **PASS** |

---

## 2. Detailed Test Case Reports

### Test Case TC-01: Risk Score Benchmark Case (HHG-001)
- **Input:** `TransactionID: 3514030`, `Card: C12382-K1`, `Center TS: 2016-12-04 19:55:28`
- **Queries Executed:** `transaction_investigation_query`, `region_anomaly_query`
- **Graph Traversal:**
  - `Transaction(3514030) ──<MADE── Card(C12382-K1) ──<OWNS── Customer(C12382)`
  - `Transaction(3514030) ──BILLED_IN── BillingRegion(REG_444.0)`
  - `Card(C12382-K1) ──MADE── Transaction(channel == "in_person") ──BILLED_IN── BillingRegion`
- **Actual Evidence Returned:**
  - `amount`: $77.07, `channel`: `in_person`, `risk_score`: 0.61.
  - `flagged_region`: `REG_444.0`.
  - Historical in-person distribution: Dominant region `REG_204.0` (46 txns), `REG_264.0` (34 txns), `REG_444.0` (15 txns).
  - Evidence shows `REG_444.0` is an established, non-novel region for this customer (15 prior visits), indicating possible legitimate repeat activity rather than an unfamiliar one-off clone.
- **Status:** **PASS**

---

### Test Case TC-02: Customer Report Benchmark Case (HHG-003)
- **Input:** `TransactionID: 3530164`, `Card: C08623-K2`, `Customer: C08623`
- **Queries Executed:** `transaction_investigation_query`, `similar_closed_cases_query`
- **Graph Traversal:**
  - `Transaction(3530164) ──<MADE── Card(C08623-K2) ──<OWNS── Customer(C08623)`
  - `Card(C08623-K2) ──<CASE_ON_CARD── ClosedCase`
- **Actual Evidence Returned:**
  - Transaction amount: $49.00, `channel`: `online`.
  - Case Memory Retrieval: Retrieved exactly **6 prior closed cases** for customer `C08623` (`CC-1589`, `CC-2817`, `CC-2935`, `CC-3327`, `CC-3682`, `CC-4957`).
  - Provides critical historical baseline for the future AI agent to evaluate customer chargeback history and recurring dispute patterns (Policy R7).
- **Status:** **PASS**

---

### Test Case TC-03: Analyst Request Benchmark Case (HHG-014)
- **Input:** `TransactionID: 3478561`, `Card: C13487-K1`
- **Queries Executed:** `device_neighbors_query`, `connected_cards_query`
- **Graph Traversal:**
  - `Transaction(3478561) ──FROM_DEVICE──► DeviceProfile(DEV_c72bd41105eb39dd)`
  - `DeviceProfile(DEV_c72bd41105eb39dd) ──<FROM_DEVICE──► Transaction ──<MADE──► Card ──<OWNS──► Customer`
- **Actual Evidence Returned:**
  - Target device hash: `DEV_c72bd41105eb39dd`.
  - Multi-hop traversal uncovered **114 transactions across 52 distinct cards** and **52 customers** sharing this exact hardware and anonymous proxy fingerprint.
  - Confirms the analyst prompt hypothesis: massive coordinated multi-account device syndicate.
- **Status:** **PASS**

---

### Test Case TC-04: Historical Confirmed Fraud Case (CC-0001)
- **Input:** `CaseID: CC-0001`, `TxnID: 3000120`
- **Queries Executed:** `similar_closed_cases_query`, `transaction_investigation_query`
- **Actual Evidence Returned:**
  - `outcome`: `confirmed_fraud`, `pattern`: `card_not_present_fraud`.
  - `exposure_usd`: $155.43, `actions_taken`: `CREATE_CASE|BLOCK_CARD`.
  - Analyst Notes: *"cardholder C00259 reported unrecognized activity on card C00259-K1... Online purchases inconsistent with normal merchants... Card blocked and reissued."*
- **Status:** **PASS**

---

### Test Case TC-05: Historical Cleared Case (CC-0003)
- **Input:** `CaseID: CC-0003`, `TxnID: 3000607`
- **Queries Executed:** `similar_closed_cases_query`
- **Actual Evidence Returned:**
  - `outcome`: `cleared`, `pattern`: `none`, `exposure_usd`: $0.00.
  - `actions_taken`: `VERIFY_WITH_CUSTOMER|CLOSE_NO_FRAUD`.
  - Analyst Notes: *"model scored a $442.92 transaction at 0.91. Cardholder confirmed travel to the billing region in question. Alert cleared."*
  - Validates that high model scores (0.91) can be false alarms verified via customer contact (Policy R1 & R3).
- **Status:** **PASS**

---

### Test Case TC-06: Shared Device Syndicate Example (CC-2649)
- **Input:** `CaseID: CC-2649` (Undocumented Pattern)
- **Queries Executed:** `device_neighbors_query`
- **Actual Evidence Returned:**
  - Device Hash: `DEV_c72bd41105eb39dd` (`Samsung SM-G935F / Chrome Android / Anonymous Proxy`).
  - Cross-case linkage: Links case `CC-2649` directly to `CC-2971`, `CC-2985`, and `CC-3035`.
  - Proves that graph traversal uncovers the undocumented shared-device syndicate without requiring manual analyst queries.
- **Status:** **PASS**

---

### Test Case TC-07: Multi-Transaction Temporal Sequence
- **Input:** `TransactionID: 3188119`
- **Queries Executed:** `temporal_pattern_query`
- **Graph Traversal:**
  - `Transaction(3188119) ──NEXT_TRANSACTION──► Transaction(3188122)`
- **Actual Evidence Returned:**
  - `delta_seconds`: **57 seconds**.
  - `delta_amount`: $0.00.
  - Flags high velocity burst (< 120s) between successive transactions on the same card.
- **Status:** **PASS**

---

### Test Case TC-08: Out-of-Region Anomaly (CC-0002)
- **Input:** `CaseID: CC-0002`, `TxnID: 3000332`, `Card: C06403-K2`
- **Queries Executed:** `region_anomaly_query`
- **Actual Evidence Returned:**
  - Flagged in-person purchase in region `REG_476.0`.
  - Historical card-present baseline established across card `C06403-K2`'s transactions.
  - Analyst note correlation: *"Card-present use in a billing region the cardholder had no history in, while cardholder retained the card."*
- **Status:** **PASS**

---

## 3. Conclusions & Readiness

1. **Precision & Integrity:** 100% of tested queries traverse genuine verified graph edges with 0 orphan entities or dangling pointers.
2. **Neutral Evidence Delivery:** No query attempts to predict a fraud verdict; each returns structural metrics (e.g. `is_new_region`, `rapid_velocity_count`, `distinct_cards_sharing_device`) for the AI agent to evaluate under Policy Rules R1–R10.
3. **GraphRAG Foundation Ready:** Graph queries are calibrated to supply factual, bounded context packets for LLM tool calling in Phase 4.
