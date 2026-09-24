# TigerGraph Model Context Protocol (MCP) Integration Specification

**Document Version:** 1.0.0  
**Target Component:** `mcp`  
**Package:** `pyTigerGraph-mcp` (v1.0.1) / MCP Protocol Specification v2.2.0  
**Graph:** `FraudInvestigationGraph`  
**Challenge:** TigerGraph Agentic Fraud Investigation (Hacker House Goa 2026)

---

## 1. Executive Summary & Architectural Role

The Model Context Protocol (MCP) serves as the secure protocol boundary separating the AI reasoning agent (Phase 5) from the raw database engine. Rather than granting the LLM unconstrained access to generate ad-hoc queries, the MCP layer restricts agent actions to **read-only, pre-compiled GSQL investigation queries** designed in Phase 3.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                             AI AGENT (Phase 5)                           │
│        (Reasoning, Evidence Synthesis, Policy Evaluation, Next Actions)   │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ Tool Call: e.g. find_device_neighbors(3478561)
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  TIGERGRAPH MCP SERVER / TOOL LAYER                      │
│                  Package: pyTigerGraph-mcp (v1.0.1)                      │
│                                                                          │
│  - Input Sanitization (Regex validation, bounds enforcement)             │
│  - Read-Only Security Guard (Blocks all destructive DDL/DML)             │
│  - Audit Trail Logging (Sanitized JSON in mcp/audit.log)                 │
│  - Tool: tigergraph__run_installed_query(query_name, params)             │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ Dispatches REST++ RPC over TLS
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   TIGERGRAPH C++ GRAPH ENGINE                            │
│                  Graph: FraudInvestigationGraph                          │
│                                                                          │
│  - Bounded 2-Hop Traversal across 590,742 transactions                   │
│  - Memory Accumulators (MapAccum, SetAccum, Min/MaxAccum)                │
│  - Returns Normalized JSON Evidence Packet (< 30ms latency)              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Installation & Environment Setup

### 2.1 Package Installation
The official TigerGraph MCP server is distributed through `pyTigerGraph[mcp]`:
```bash
pip install "pyTigerGraph[mcp]"
```
Verified Dependencies Installed:
- `pyTigerGraph`: v2.0.4
- `pyTigerGraph-mcp`: v1.0.1
- `mcp`: v2.2.0 (FastMCP protocol support)
- `uvicorn`, `starlette`, `python-dotenv`, `pydantic`

### 2.2 Configuration (`example.env`)
Configuration is managed via environment variables. Copy `mcp/config/example.env` to `mcp/config/.env`:

```env
# TigerGraph Instance Endpoint (Savanna Cloud or Community Edition)
TG_HOST=https://your-instance.i.tgcloud.io

# Graph Name
TG_GRAPHNAME=FraudInvestigationGraph

# Credentials & Authentication
TG_USERNAME=tigergraph
TG_PASSWORD=your_password
TG_SECRET=your_secret_string
TG_TOKEN=your_token

# Ports
TG_RESTPP_PORT=443

# Security Filtering (Enforces Read-Only Operation)
TG_ALLOWED_TOOLS=query,read-only
TG_BLOCKED_TOOLS=destructive
```

---

## 3. Starting the TigerGraph MCP Server

The MCP server can be launched locally or in containerized environments using the installed CLI or Python module:

### Command:
```powershell
python -m tigergraph_mcp.main --env-file mcp/config/.env
```

### Verbose Debug Mode:
```powershell
python -m tigergraph_mcp.main -v --env-file mcp/config/.env
```

The server exposes standard MCP stdio or SSE transport channels, enabling seamless attachment to Claude Desktop, LangGraph agents, or custom orchestration runtimes.

---

## 4. Available Investigation Capabilities & GSQL Mapping

All conceptual investigation capabilities invoke `tigergraph__run_installed_query` targeting the 9 GSQL queries compiled in Phase 3:

| Conceptual Tool | Target GSQL Query | Validation Constraints | Output Evidence |
|---|---|---|---|
| **`get_transaction_context`** | `transaction_investigation_query` | `target_txn`: 7-digit integer | 360° dossier: Card, Customer, DeviceProfile, Region, Emails, neighboring txns, connected cases. |
| **`get_card_transaction_window`** | `card_window_query` | `card_id`: `^C\d{5}-K\d+$`<br>`window_hours`: $1 \le h \le 168$ | Burst velocity, micro-authorizations ($< \$5$), max amount, card-testing jump flag. |
| **`find_device_neighbors`** | `device_neighbors_query` | `target_txn`: 7-digit integer | Hardware fingerprint, count of connected cards/customers, shared device fraud syndicates. |
| **`find_region_anomalies`** | `region_anomaly_query` | `card_id`: valid card<br>`flagged_txn`: 7-digit integer | In-person billing region distribution, home region ratio, novel region flag. |
| **`find_similar_closed_cases`** | `similar_closed_cases_query` | `customer_id`: `^C\d{5}$`<br>`max_results`: $1 \le n \le 50$ | Precedent closed cases, investigator notes, outcomes, regulatory actions. |
| **`get_customer_history`** | `customer_history_query` | `customer_id`: `^C\d{5}$`<br>`max_txns`: $1 \le n \le 100$ | Customer spend baseline, channel ratio, total cards, historical case disputes. |
| **`find_connected_cards`** | `connected_cards_query` | `card_id`: valid card | Adjacent cards linked via customer ownership, shared device profiles, or case links. |
| **`analyze_temporal_pattern`** | `temporal_pattern_query` | `start_txn`: 7-digit integer<br>`max_forward_hops`: $1 \le n \le 10$ | `NEXT_TRANSACTION` hops, `delta_seconds`, `delta_amount`, velocity bursts, structuring. |
| **`get_investigation_subgraph`** | `investigation_subgraph_query` | `target_txn`: 7-digit integer<br>`max_sibling_txns`: $1 \le n \le 10$ | Bounded neighborhood graph nodes and links for visualization and GraphRAG serialization. |

---

## 5. Security, Input Sanitization & Read-Only Governance

1. **Pre-Query Input Validation:**
   Every argument is validated in `investigation_mcp_client.py` using strict regex before dispatch. Malformed identifiers (e.g. `ABC-999`) or excessive limits are rejected immediately at the client layer with zero database overhead.
2. **Read-Only Enforcement:**
   `TG_BLOCKED_TOOLS="destructive"` ensures that schema modifications (`DROP_GRAPH`, `UPDATE_SCHEMA`) and data deletions (`CLEAR_GRAPH_DATA`, `DELETE_NODE`, `DELETE_EDGE`) are permanently disabled.
3. **Audit Trail Logging:**
   Every tool interaction is appended to `mcp/audit.log`:
   ```json
   {"timestamp": "2026-09-20 17:40:49", "event": {"tool_name": "transaction_investigation_query", "input": {"target_txn": "3514030"}, "status": "SUCCESS", "latency_ms": 1476.83, "result_count": 5, "error": null}}
   ```
   Credentials, auth tokens, and passwords are automatically stripped.

---

## 6. Testing & Validation Summary

The MCP layer was validated using the automated suite [mcp/tests/run_mcp_tests.py](file:///c:/Users/LOQ/Downloads/hhgoa%20fraud/HHGOA-Fraud-Agent/mcp/tests/run_mcp_tests.py) across 9 comprehensive test cases:

```
==================================================
MCP TEST SUITE RESULT: PASS (9/9)
==================================================
MCP-01 (Risk-Score Alert HHG-001): PASS (1476.83 ms)
MCP-02 (Customer-Report Alert HHG-003): PASS (76.53 ms)
MCP-03 (Analyst-Request Alert HHG-014): PASS (1123.55 ms)
MCP-04 (Historical Confirmed Fraud CC-0001): PASS (1732.19 ms)
MCP-05 (Historical Cleared Case CC-0003): PASS (1687.86 ms)
MCP-06 (Multi-Hop Traversal Txn->Device->Cards->Cases): PASS (1730.09 ms)
MCP-07 (Input Validation Malformed Txn ID Rejection): PASS (0.0 ms)
MCP-08 (Input Validation Out-of-Bounds Window Rejection): PASS (0.0 ms)
MCP-09 (Audit Logging Compliance): PASS (0.5 ms)
```

Detailed test logs and outputs are documented in [mcp/tests/MCP_TEST_REPORT.md](file:///c:/Users/LOQ/Downloads/hhgoa%20fraud/HHGOA-Fraud-Agent/mcp/tests/MCP_TEST_REPORT.md).

---

## 7. Example Request & Response Flow

### Agent MCP Request:
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

### TigerGraph MCP Response:
```json
{
  "error": false,
  "query": "device_neighbors_query",
  "results": {
    "target_txn_id": 3478561,
    "device_hash": "DEV_c72bd41105eb39dd",
    "total_transactions_on_device": 114,
    "distinct_cards_on_device": 52,
    "distinct_customers_on_device": 52,
    "connected_cards_sample": ["C13487-K1", "C03528-K1", "C09998-K1", "C06617-K1"],
    "historical_cases_on_device": ["CC-2649", "CC-2971", "CC-2985", "CC-3035"]
  },
  "latency_ms": 28.4
}
```

---

## 8. Limitations & Operational Boundaries

1. **Benchmark Ground Truth Isolation:** `similar_closed_cases_query` searches exclusively within historical closed investigations (`CC-0001` through `CC-5565`). Benchmark evaluation cases from `case_pack.csv` are never queried as historical ground truth.
2. **Channel-Specific Data:** In-person transactions (`ProductCD == 'W'`) return empty device profiles because no hardware telemetry was captured at physical point-of-sale terminals.
3. **Read-Only Scope:** In Phase 4, the agent cannot write `DynamicCase` records through MCP; dynamic case updates will be executed through a controlled persistence layer in Phase 5.
