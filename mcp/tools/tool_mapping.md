# TigerGraph MCP Tool Mapping & Interface Specification

**Version:** 1.0.0  
**Target MCP Server:** `tigergraph_mcp` (v1.0.1) / `pyTigerGraph[mcp]`  
**Graph:** `FraudInvestigationGraph`  
**Mode:** READ-ONLY Enforced (`TG_ALLOWED_TOOLS="query,read-only"`, `TG_BLOCKED_TOOLS="destructive"`)

---

## 1. Architectural Mapping Overview

TigerGraph MCP provides standard endpoint tools to interact with TigerGraph. In this architecture, all high-level agent investigation requests are dispatched through the official `tigergraph__run_installed_query` tool, invoking pre-compiled, optimized GSQL C++ query endpoints.

```
┌────────────────────────────────────────────────────────┐
│                   Future AI Agent                      │
└───────────────────────────┬────────────────────────────┘
                            │ Calls Tool (e.g. get_transaction_context)
                            ▼
┌────────────────────────────────────────────────────────┐
│             TigerGraph MCP Tool Layer                  │
│       Tool: tigergraph__run_installed_query            │
│       Params: query_name, params {...}                 │
└───────────────────────────┬────────────────────────────┘
                            │ Dispatches REST++ Request
                            ▼
┌────────────────────────────────────────────────────────┐
│             TigerGraph C++ Query Engine                │
│    Executes: transaction_investigation_query(3514030)   │
└───────────────────────────┬────────────────────────────┘
                            │ Evaluates Graph Accumulators
                            ▼
┌────────────────────────────────────────────────────────┐
│             Structured Evidence Packet                 │
│         (JSON returned to MCP -> LLM Agent)            │
└────────────────────────────────────────────────────────┘
```

---

## 2. GSQL Query to MCP Capability Matrix

| Conceptual Agent Tool | Underlying MCP Function | Target Installed GSQL Query | Input Parameters | Primary Evidence Returned |
|---|---|---|---|---|
| **`get_transaction_context`** | `tigergraph__run_installed_query` | `transaction_investigation_query` | `target_txn`: INT/STRING | Complete 360° dossier: Card, Customer, DeviceProfile, Region, Emails, neighboring txns, connected cases. |
| **`get_card_transaction_window`**| `tigergraph__run_installed_query` | `card_window_query` | `target_card`: STRING<br>`center_ts`: STRING<br>`window_hours`: INT ($\le 168$) | Burst txns, micro-authorizations ($< \$5$), max amount, card-testing jump flag. |
| **`find_device_neighbors`** | `tigergraph__run_installed_query` | `device_neighbors_query` | `target_txn`: INT/STRING | Device fingerprint, connected cards/customers count, shared device fraud syndicates. |
| **`find_region_anomalies`** | `tigergraph__run_installed_query` | `region_anomaly_query` | `target_card`: STRING<br>`flagged_txn`: INT/STRING | In-person billing region distribution, home region ratio, novel region flag. |
| **`find_similar_closed_cases`** | `tigergraph__run_installed_query` | `similar_closed_cases_query` | `customer_id_filter`: STRING<br>`card_id_filter`: STRING<br>`pattern_filter`: STRING<br>`min_exposure`: FLOAT<br>`max_results`: INT ($\le 50$) | Relevant historical case precedents, investigator notes, outcomes, regulatory actions. |
| **`get_customer_history`** | `tigergraph__run_installed_query` | `customer_history_query` | `target_customer`: STRING<br>`max_txns`: INT ($\le 100$) | Customer portfolio metrics, total cards, spend baseline, channel ratio, previous cases. |
| **`find_connected_cards`** | `tigergraph__run_installed_query` | `connected_cards_query` | `target_card`: STRING | Adjacent cards linked via customer ownership, shared device profiles, or case links. |
| **`analyze_temporal_pattern`** | `tigergraph__run_installed_query` | `temporal_pattern_query` | `start_txn`: INT/STRING<br>`max_forward_hops`: INT ($\le 10$) | Consecutive `NEXT_TRANSACTION` hops, `delta_seconds`, `delta_amount`, velocity bursts, structuring. |
| **`get_investigation_subgraph`** | `tigergraph__run_installed_query` | `investigation_subgraph_query` | `target_txn`: INT/STRING<br>`max_sibling_txns`: INT ($\le 10$) | Bounded local neighborhood graph nodes and links for visualization and GraphRAG serialization. |

---

## 3. Strict Input Validation & Safety Rules

To prevent query injection, excessive graph scans, and unauthorized traversal, every MCP tool call is validated against the following schema before dispatch:

```
+-------------------+----------------------------+-----------------------+---------------------------------------+
| Parameter Name    | Target Entity              | Validation Pattern    | Allowable Range / Constraint          |
+-------------------+----------------------------+-----------------------+---------------------------------------+
| `target_txn`      | Transaction                | `^\d{7}$`             | Integer between 3000001 and 3590742   |
| `target_card`     | Card                       | `^C\d{5}-K\d+$`       | Valid customer card code              |
| `target_customer` | Customer                   | `^C\d{5}$`            | Valid customer account code           |
| `device_hash`     | DeviceProfile              | `^DEV_[a-f0-9]{16}$`  | Canonical 16-hex MD5 device hash      |
| `window_hours`    | Temporal Window            | Integer               | $1 \le \text{window\_hours} \le 168$  |
| `max_results`     | Pagination / Limit         | Integer               | $1 \le \text{max\_results} \le 50$    |
| `max_txns`        | Pagination / Limit         | Integer               | $1 \le \text{max\_txns} \le 100$      |
| `max_forward_hops`| Sequential Path Traversal  | Integer               | $1 \le \text{max\_forward\_hops} \le 10$ |
+-------------------+----------------------------+-----------------------+---------------------------------------+
```

### Prohibited Operations:
1. **Destructive Operations:** `CLEAR_GRAPH_DATA`, `DROP_GRAPH`, `DELETE_NODE`, `DELETE_NODES`, `DELETE_EDGE`, `DROP_QUERY` are explicitly blocked by MCP server configuration (`TG_BLOCKED_TOOLS=destructive`).
2. **Dynamic GSQL Modification:** The agent cannot execute raw DDL or ad-hoc GSQL query creation through MCP.
3. **Unbounded Traversals:** Queries without root anchor or depth bounds are rejected.

---

## 4. MCP Query Dispatch Payloads

### 4.1 Tool Call: `get_transaction_context`
```json
{
  "name": "tigergraph__run_installed_query",
  "arguments": {
    "query_name": "transaction_investigation_query",
    "params": {
      "target_txn": "3514030"
    }
  }
}
```

### 4.2 Tool Call: `get_card_transaction_window`
```json
{
  "name": "tigergraph__run_installed_query",
  "arguments": {
    "query_name": "card_window_query",
    "params": {
      "target_card": "C12382-K1",
      "center_ts": "2016-12-04 19:55:28",
      "window_hours": 24
    }
  }
}
```

### 4.3 Tool Call: `find_device_neighbors`
```json
{
  "name": "tigergraph__run_installed_query",
  "arguments": {
    "query_name": "device_neighbors_query",
    "params": {
      "target_txn": "3478561"
    }
  }
}
```

### 4.4 Tool Call: `find_region_anomalies`
```json
{
  "name": "tigergraph__run_installed_query",
  "arguments": {
    "query_name": "region_anomaly_query",
    "params": {
      "target_card": "C06403-K2",
      "flagged_txn": "3000332"
    }
  }
}
```

### 4.5 Tool Call: `find_similar_closed_cases`
```json
{
  "name": "tigergraph__run_installed_query",
  "arguments": {
    "query_name": "similar_closed_cases_query",
    "params": {
      "customer_id_filter": "C08623",
      "pattern_filter": "",
      "max_results": 10
    }
  }
}
```

---

## 5. Result Structure & Size Control

Responses returned by the MCP layer are strictly normalized JSON objects:

```json
{
  "error": false,
  "message": "",
  "results": [
    {
      "target_txn_id": "3514030",
      "entities": {
        "customer": {"customer_id": "C12382", "total_cards": 1},
        "card": {"card_id": "C12382-K1", "card4": "visa", "card6": "debit"},
        "device": null,
        "region": {"region_id": "REG_444.0", "region_code": 444.0, "country_code": 87.0}
      },
      "evidence": {
        "amount": 77.07,
        "channel": "in_person",
        "risk_score": 0.61,
        "is_out_of_region": false,
        "prior_visits_to_region": 15
      }
    }
  ]
}
```

All collections (`ConnectedTxns`, `SiblingCardTxns`) have strict `LIMIT` clauses ($5$ to $50$ items) to guarantee that context window utilization remains within token budgets for Phase 5 agent reasoning.
