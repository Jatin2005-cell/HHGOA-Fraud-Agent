# MCP Execution Trace & Tool Call Architecture

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Challenge:** Hacker House Goa 2026  
**Audit Reference:** Phase 6.6 Specification (Section 3 & Section 8)  
**Execution Runtime:** OFFLINE_STAGED_SIMULATION (Level B)  

---

## 1. Architectural Call Flow: Live Mode vs. Offline Simulation Mode

Every investigation tool follows a dual-path design. The system detects whether a live TigerGraph connection exists and switches transparently between Live Mode and Offline Staged Simulation Mode.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Autonomous AI Agent                           │
│                   (agent/core/investigation_fsm.py)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        MCPInvestigationAdapter                         │
│                       (agent/tools/mcp_tools.py)                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          TigerGraphMCPClient                           │
│               (mcp/tools/investigation_mcp_client.py)                  │
│                                                                        │
│   • Regex Input Validation                                             │
│   • Audit Logging (mcp/audit.log)                                      │
│   • Bounded Pagination & Parameter Sanitization                        │
└───────────────┬────────────────────────────────────────┬───────────────┘
                │                                        │
      [LIVE_TIGERGRAPH MODE]                   [OFFLINE_SIMULATION MODE]
                │                                        │ (CURRENTLY ACTIVE)
                ▼                                        ▼
┌───────────────────────────────┐        ┌───────────────────────────────┐
│     pyTigerGraph Client       │        │  _execute_local_query_engine  │
│  (TigerGraphConnection)       │        │  (mcp/tools/investigation_    │
└───────────────┬───────────────┘        │   mcp_client.py:L116)         │
                │                        └───────────────┬───────────────┘
                ▼                                        │
┌───────────────────────────────┐                        ▼
│  TigerGraph RESTPP (:443/9000)│        ┌───────────────────────────────┐
│  /restpp/query/FraudInvest... │        │      Pandas In-Memory Engine  │
└───────────────┬───────────────┘        │  Reads dataset/processed/*.csv│
                │                        └───────────────┬───────────────┘
                ▼                                        │
┌───────────────────────────────┐                        │
│ Compiled GSQL on Active Graph │                        │
└───────────────┬───────────────┘                        │
                │                                        │
                ▼                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Normalized Evidence Extraction                      │
│             (agent/graph_rag/graph_context_builder.py)                 │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> Because live TigerGraph cluster credentials have not been configured on this host, all tool executions currently route through the **OFFLINE_SIMULATION MODE** (`_execute_local_query_engine`).  
> **This engine reads pre-processed CSV tables from `dataset/processed/` using Pandas. It is NOT executing GSQL bytecode on a TigerGraph daemon.**

---

## 2. Detailed Execution Trace for the 9 Investigation Tools

---

### Tool 1: `get_transaction_context`
- **Target GSQL Query:** `transaction_investigation_query.gsql`
- **Primary Input:** `transaction_id: int` (Validated by `^\d{7}$`)
- **Live Path:** `TigerGraphMCPClient._conn.runInstalledQuery("transaction_investigation_query", {"target_txn": "3478561"})` -> RESTPP -> TigerGraph
- **Offline Simulation Path:**
  1. Opens `dataset/processed/transactions.csv`, matches `txn_id == target_txn`.
  2. Extracts `card_id` and derives `customer_id`.
  3. Joins `dataset/processed/edges_from_device.csv` -> `dataset/processed/devices.csv` to retrieve device hardware profile.
  4. Joins `dataset/processed/edges_case_involves.csv` to identify historical linked cases.
- **Output Schema:**
  ```json
  {
    "target_transaction": [{ "txn_id": 3478561, "amount": 292.36, "channel": "online", "risk_score": 0.61 }],
    "target_card": [{ "card_id": "C13487-K1", "customer_id": "C13487" }],
    "target_customer": [{ "customer_id": "C13487" }],
    "device_profile": [{ "device_hash": "DEV_c72bd41105eb39dd", "os": "Windows 10", "browser": "Chrome 54.0" }],
    "connected_cases": ["CC-2649", "CC-2971", "CC-2985", "HHG-014"]
  }
  ```

---

### Tool 2: `get_card_transaction_window`
- **Target GSQL Query:** `card_window_query.gsql`
- **Primary Input:** `card_id: str`, `center_ts: str`, `window_hours: int`
- **Live Path:** `TigerGraphMCPClient._conn.runInstalledQuery("card_window_query", {...})`
- **Offline Simulation Path:**
  1. Computes `start_ts = center_ts - window_hours` and `end_ts = center_ts + window_hours`.
  2. Filters `dataset/processed/transactions.csv` for `card_id == target_card` within time window.
  3. Counts sub-$5 online micro-authorizations (`amount <= 5.0 and channel == 'online'`).
  4. Detects card-testing pattern: `small_auths >= 3 and max_amt >= 50.0`.
- **Output Schema:**
  ```json
  {
    "card_id": "C08623-K2",
    "window_txn_count": 5,
    "window_total_amount": 345.50,
    "sub_5_dollar_auth_count": 3,
    "max_txn_amount": 180.00,
    "card_testing_sequence_detected": true,
    "transactions": [...]
  }
  ```

---

### Tool 3: `find_device_neighbors`
- **Target GSQL Query:** `device_neighbors_query.gsql`
- **Primary Input:** `transaction_id: int`
- **Live Path:** Traverses `Transaction -(FROM_DEVICE)-> DeviceProfile <-(FROM_DEVICE)- Transaction -(MADE)-> Card`
- **Offline Simulation Path:**
  1. Looks up `target_txn` in `dataset/processed/edges_from_device.csv` to find `device_hash`.
  2. Finds all other `txn_id`s originating from that `device_hash`.
  3. Joins `dataset/processed/transactions.csv` to collect distinct `card_id`s and `customer_id`s.
  4. Joins `dataset/processed/edges_case_involves.csv` for any cases tied to those transactions.
- **Output Schema:**
  ```json
  {
    "target_txn_id": 3478561,
    "device_hash": "DEV_c72bd41105eb39dd",
    "total_transactions_on_device": 114,
    "distinct_cards_on_device": 52,
    "distinct_customers_on_device": 48,
    "historical_cases_on_device": ["CC-2649", "CC-2971", "CC-2985", "CC-3035"]
  }
  ```

---

### Tool 4: `find_region_anomalies`
- **Target GSQL Query:** `region_anomaly_query.gsql`
- **Primary Input:** `card_id: str`, `transaction_id: int`
- **Live Path:** Traverses `Transaction -(BILLED_IN)-> BillingRegion` and computes historical frequency distribution.
- **Offline Simulation Path:**
  1. Matches `flagged_txn` in `dataset/processed/edges_billed_in.csv` to get `flagged_region_id`.
  2. Finds all prior in-person transactions for `card_id` in `dataset/processed/transactions.csv`.
  3. Joins with `edges_billed_in.csv` to compute cardholder's historical billing region distribution.
  4. Computes whether `flagged_region_prior_count == 0` (new/anomalous billing region).
- **Output Schema:**
  ```json
  {
    "flagged_txn_id": 3514030,
    "card_id": "C12382-K1",
    "flagged_region_id": "REG_444.0",
    "dominant_home_region": "REG_204.0",
    "total_in_person_history_count": 487,
    "flagged_region_prior_count": 15,
    "is_new_billing_region": false
  }
  ```

---

### Tool 5: `find_similar_closed_cases`
- **Target GSQL Query:** `similar_closed_cases_query.gsql`
- **Primary Input:** `customer_id: Optional[str]`, `card_id: Optional[str]`, `pattern: Optional[str]`, `max_results: int`
- **Live Path:** Queries `ClosedCase` vertices filtered by customer/card/pattern attributes.
- **Offline Simulation Path:**
  1. Loads `dataset/processed/closed_cases.csv` (5,565 historical closed cases).
  2. Filters rows matching `customer_id`, `card_id`, and/or `pattern`.
  3. Returns top `max_results` cases with outcome, exposure, and investigator notes.
- **Output Schema:**
  ```json
  {
    "matched_cases": [
      {
        "case_id": "CC-2277",
        "customer_id": "C12265",
        "card_id": "C12265-K2",
        "outcome": "confirmed_fraud",
        "pattern": "account_takeover",
        "exposure_usd": 81.93,
        "analyst_notes": "Cardholder reported unrecognized activity..."
      }
    ],
    "total_matched": 1
  }
  ```

---

### Tool 6: `get_customer_history`
- **Target GSQL Query:** `customer_history_query.gsql`
- **Primary Input:** `customer_id: str`, `max_txns: int`
- **Live Path:** Traverses `Customer -(OWNS)-> Card -(MADE)-> Transaction`
- **Offline Simulation Path:**
  1. Filters `dataset/processed/transactions.csv` for `customer_id == target_customer`.
  2. Extracts distinct `card_id`s owned by customer.
  3. Computes `total_spend`, `avg_amount`, and recent transaction history.
- **Output Schema:**
  ```json
  {
    "customer_id": "C12382",
    "total_cards_count": 1,
    "total_transaction_count": 512,
    "total_spend": 39420.15,
    "avg_amount": 76.99,
    "cards": ["C12382-K1"]
  }
  ```

---

### Tool 7: `find_connected_cards`
- **Target GSQL Query:** `connected_cards_query.gsql`
- **Primary Input:** `card_id: str`
- **Live Path:** Traverses `Card <-(OWNS)- Customer -(OWNS)-> Card`
- **Offline Simulation Path:**
  1. Derives `customer_id` from `card_id` prefix.
  2. Filters `dataset/processed/cards.csv` for cards sharing same `customer_id` where `card_id != target_card`.
- **Output Schema:**
  ```json
  {
    "target_card": "C12265-K2",
    "same_customer_cards": ["C12265-K1", "C12265-K3", "C12265-K4"],
    "same_customer_cards_count": 3
  }
  ```

---

### Tool 8: `analyze_temporal_pattern`
- **Target GSQL Query:** `temporal_pattern_query.gsql`
- **Primary Input:** `start_txn_id: int`, `max_hops: int`
- **Live Path:** Traverses `NEXT_TRANSACTION` edges forward up to `max_hops`.
- **Offline Simulation Path:**
  1. Opens `dataset/processed/edges_next_transaction.csv`.
  2. Follows `from_txn_id -> to_txn_id` hops iteratively.
  3. Records `delta_seconds`, `delta_amount`, and `same_region` for each hop.
- **Output Schema:**
  ```json
  {
    "start_txn_id": 3188119,
    "chain_length": 1,
    "hops": [
      {
        "from_txn_id": 3188119,
        "to_txn_id": 3188122,
        "delta_seconds": 57,
        "delta_amount": 0.0,
        "same_region": true
      }
    ]
  }
  ```

---

### Tool 9: `get_investigation_subgraph`
- **Target GSQL Query:** `investigation_subgraph_query.gsql`
- **Primary Input:** `transaction_id: int`, `max_siblings: int`
- **Live Path:** Retrieves 2-hop neighborhood of vertices and edges surrounding `target_txn`.
- **Offline Simulation Path:**
  - Invokes `_execute_local_query_engine("transaction_investigation_query")` to return the complete entity-relationship neighborhood.
- **Output Schema:** Full graph dossier including transaction, card, customer, device, and connected case entities.

---

## 3. Summary of Execution Verification

| Tool # | Name | Live GSQL Ready? | Offline Simulation Working? | Data Source |
|---|---|---|---|---|
| **1** | `get_transaction_context` | Yes | Yes (Tested: Txn 3478561) | `transactions.csv`, `edges_from_device.csv` |
| **2** | `get_card_transaction_window` | Yes | Yes (Tested: C08623-K2) | `transactions.csv` |
| **3** | `find_device_neighbors` | Yes | Yes (Tested: DEV_c72bd41105eb39dd) | `edges_from_device.csv`, `transactions.csv` |
| **4** | `find_region_anomalies` | Yes | Yes (Tested: Txn 3514030) | `edges_billed_in.csv`, `transactions.csv` |
| **5** | `find_similar_closed_cases` | Yes | Yes (Tested: CC-0001, CC-2649) | `closed_cases.csv` |
| **6** | `get_customer_history` | Yes | Yes (Tested: C12382) | `transactions.csv`, `cards.csv` |
| **7** | `find_connected_cards` | Yes | Yes (Tested: C12265-K2) | `cards.csv` |
| **8** | `analyze_temporal_pattern` | Yes | Yes (Tested: Txn 3188119) | `edges_next_transaction.csv` |
| **9** | `get_investigation_subgraph` | Yes | Yes (Tested: Txn 3478561) | Combined processed CSV tables |
