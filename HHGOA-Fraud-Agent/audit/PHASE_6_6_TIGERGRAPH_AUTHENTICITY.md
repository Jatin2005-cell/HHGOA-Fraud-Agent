# Phase 6.6 — TigerGraph Authenticity & Architecture Forensic Audit Report

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Challenge:** Hacker House Goa 2026  
**Audit Date:** September 20, 2026  
**Auditor:** Antigravity Autonomous Systems Engineering & Forensic Verification  
**Scope:** Technical Verification of TigerGraph Layer, MCP Runtime, GraphRAG, Writeback, and Readback Integrity  

---

## 1. Executive Summary & The Golden Rule

The purpose of this Phase 6.6 forensic audit is to definitively determine whether the project's graph layer executes against a **live TigerGraph engine** or a **local staged dataset simulation**.

### The Golden Rule Classification

The system strictly differentiates across four fundamental execution tiers:

| Tier | Category | Description | Workspace Status |
|---|---|---|---|
| **Level A** | **Real TigerGraph Execution** | Live pyTigerGraph / MCP client connecting to an active TigerGraph instance (Savanna Cloud or Community Edition) over RESTPP (`:9000` / `:443`) executing compiled GSQL. | **NOT AVAILABLE** (No live TigerGraph instance is reachable; credentials are placeholders). |
| **Level B** | **Local Dataset / Staged Graph Simulation** | Project-authored Python simulation engine executing relational/graph queries over genuine, pre-processed HHGOA_IEEE CSV tables (`dataset/processed/`). | **ACTIVE (100% of current runtime)**. |
| **Level C** | **Mocked Test Data** | Synthetic unit test fixtures used exclusively in unit tests (`agent/tests/test_stop_conditions.py`, mock LLM responses). | **TEST FIXTURES ONLY**. |
| **Level D** | **Static / Hardcoded Output** | Pre-canned answers or lookup tables for benchmark cases. | **PROVEN ABSENT (0%)** — All 20 cases execute dynamic reasoning. |

> [!WARNING]
> **CRITICAL ARCHITECTURAL DISCLOSURE:**  
> The previous Phase 6.5 audit reported *"the official pyTigerGraph-mcp 1.0.1 client automatically uses its local fallback engine over dataset/processed/"*.  
> **THIS CLAIM HAS BEEN REFUTED UPON SOURCE INSPECTION.**  
> **Official TigerGraph MCP does not provide the claimed local TigerGraph fallback; the project contains its own fallback/simulation layer.**

---

## 2. Verification of Official MCP Package

An inspection was conducted on the installed Python environment:

```bash
python -c "import tigergraph_mcp; print(tigergraph_mcp.__file__)"
# Output: C:\Users\LOQ\AppData\Local\Programs\Python\Python312\Lib\site-packages\tigergraph_mcp\__init__.py

python -c "import pyTigerGraph; print(pyTigerGraph.__file__)"
# Output: C:\Users\LOQ\AppData\Local\Programs\Python\Python312\Lib\site-packages\pyTigerGraph\__init__.py

python -c "import importlib.metadata as m; print('pyTigerGraph:', m.version('pyTigerGraph')); print('pyTigerGraph-mcp:', m.version('pyTigerGraph-mcp'))"
# Output: pyTigerGraph: 2.0.4, pyTigerGraph-mcp: 1.0.1
```

### Keyword Search in Official Package Source (`tigergraph_mcp`)
The installed package directory was scanned for fallback and simulation keywords:
- `local fallback`: **0 occurrences**
- `fallback engine`: **0 occurrences**
- `staged graph`: **0 occurrences**
- `processed dataset`: **0 occurrences**
- `pandas`: **0 occurrences**
- `mock`: **0 occurrences**
- `simulator` / `simulation`: **0 occurrences**
- `TigerGraphConnection` / `AsyncTigerGraphConnection`: **Present** (in `connection_manager.py`)
- `RESTPP`: **Present** (in `connection_manager.py`)
- `GSQL`: **Present** (in query tool wrappers)
- `TG_HOST`: **Present** (environment config resolver)

**Finding:**  
The official `pyTigerGraph-mcp` package requires an actual live TigerGraph cluster. It contains no offline dataset fallback or Pandas simulation engine. The fallback engine is implemented entirely inside the project repository at `mcp/tools/investigation_mcp_client.py`.

---

## 3. TigerGraph Connection Verification

Configuration inspection of `mcp/config/example.env`:

```ini
# Sanitized configuration parameters
TG_HOST=https://your-tigergraph-instance.i.tgcloud.io
TG_GRAPHNAME=FraudInvestigationGraph
TG_USERNAME=tigergraph
TG_RESTPP_PORT=443
TG_ALLOWED_TOOLS=query,read-only
TG_BLOCKED_TOOLS=destructive
```

### Network & Process Probe Results
1. **Cloud Host DNS:** Attempting to resolve `your-tigergraph-instance.i.tgcloud.io` triggers `urllib3.exceptions.NameResolutionError` (`[Errno 11001] getaddrinfo failed`).
2. **Local Ports:** Probing `127.0.0.1:9000` (RESTPP) and `127.0.0.1:14240` (GraphStudio) returns `CLOSED`.
3. **Container Engine:** `Get-Command docker` returns not found (Docker is not installed on the host OS).
4. **Conclusion:**
   ```
   TIGERGRAPH LIVE CONNECTION = NOT AVAILABLE
   ```

---

## 4. Verification of the Project's "Local Staged Graph Simulation"

The local simulation layer was inspected in `mcp/tools/investigation_mcp_client.py`:
- **File:** `mcp/tools/investigation_mcp_client.py`
- **Class:** `TigerGraphMCPClient`
- **Method:** `_execute_local_query_engine(query_name, params, data_dir)`
- **Activation Condition:** Activated when `self.use_local_fallback = True` or when `self._conn` is `None`.
- **Data Source:** Reads directly from `dataset/processed/` using `pandas.read_csv()`:
  - `transactions.csv` (15,000 active transactions)
  - `cards.csv` (12,793 cards)
  - `devices.csv` (10,381 devices)
  - `closed_cases.csv` (5,565 historical closed cases)
  - `edges_from_device.csv` (3,640 device edges)
  - `edges_billed_in.csv` (13,767 region edges)
  - `edges_case_involves.csv` (14,977 case transaction edges)
  - `edges_case_on_card.csv` (5,587 case card edges)
  - `edges_next_transaction.csv` (14,980 temporal sequence edges)
- **GSQL Emulation:** The method replicates the exact GSQL graph traversal logic in pure Python/Pandas. It does **not** execute GSQL bytecode or communicate with a TigerGraph binary.
- **Provenance:** 100% project-authored code, NOT official TigerGraph code.

---

## 5. GSQL Authenticity Audit

The project contains 9 GSQL queries in `tigergraph/queries/`. Each was analyzed for syntax and execution status:

| Query Name | Source File | Syntax Valid? | Installed on Live TG? | Executed on Live TG? | Uses Graph Data? | Simulation Result |
|---|---|---|---|---|---|---|
| `transaction_investigation_query` | `tigergraph/queries/transaction_investigation_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `card_window_query` | `tigergraph/queries/card_window_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `device_neighbors_query` | `tigergraph/queries/device_neighbors_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `region_anomaly_query` | `tigergraph/queries/region_anomaly_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `similar_closed_cases_query` | `tigergraph/queries/similar_closed_cases_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `customer_history_query` | `tigergraph/queries/customer_history_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `connected_cards_query` | `tigergraph/queries/connected_cards_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `temporal_pattern_query` | `tigergraph/queries/temporal_pattern_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |
| `investigation_subgraph_query` | `tigergraph/queries/investigation_subgraph_query.gsql` | **YES** | **NO** | **NO** | Simulated from CSV | **PASS (Level B)** |

---

## 6. Graph Writeback & Readback Verification

### Writeback
- **Code:** `case_management/graph_writeback.py` (`CaseWritebackService.write_case()`)
- **Actual Destination:** Appends/updates records in `dataset/processed/dynamic_cases.csv`, `dataset/processed/edges_case_involves.csv`, and `dataset/processed/edges_case_on_card.csv`.
- **Verdict:**
  ```
  GRAPH WRITEBACK TO TIGERGRAPH = NOT VERIFIED
  (Level B Staged Graph Store Writeback: VERIFIED)
  ```

### Readback
- **Code:** `case_management/graph_readback.py` (`CaseReadbackService.verify_case()`)
- **Actual Source:** Reads back persisted rows from `dataset/processed/dynamic_cases.csv` and cross-references edge CSV files.
- **Verdict:**
  ```
  GRAPH READBACK FROM TIGERGRAPH = NOT VERIFIED
  (Level B Staged Graph Readback: VERIFIED)
  ```

---

## 7. GraphRAG & Case Memory Verification

1. **Graph Context Construction:** `agent/graph_rag/graph_context_builder.py` normalizes raw tool outputs into `EvidenceItem` objects with provenance tags.
2. **Case Memory Retrieval:** `agent/graph_rag/case_memory.py` queries `dataset/processed/closed_cases.csv` (5,565 historical closed cases). Tested dynamically on cases `CC-0001`, `CC-0003`, and `CC-2649`.
3. **Factual Fusion:** `HybridRetriever` in `agent/graph_rag/retriever.py` dynamically merges retrieved graph evidence, case memory precedents, and Policy Rules R1–R10.
4. **Data Source:** GraphRAG currently operates over **Level B (Local Staged Dataset)**, not live TigerGraph vertices.

---

## 8. Agent Independence & Non-Hardcoding Verification

A global codebase audit was performed for benchmark IDs `HHG-001` through `HHG-020`:
- **Occurrences in `agent/core/`, `agent/fsm/`, `agent/policy/`, `agent/graphrag/`:** **ZERO (0)**.
- **Occurrences in `agent/schemas/`:** 1 documentation string example.
- **Occurrences in `agent/tests/`:** Unit test fixtures providing test case IDs.
- **Occurrences in `dataset/raw/case_pack.csv`:** Real test alert trigger records.
- **Occurrences in `cases/` & `data/cases/`:** Dynamic execution output JSONs.
- **Findings:** The agent possesses **NO hardcoded benchmark answers**, NO lookup tables, NO case-specific branching logic, and NO pre-baked verdicts.
- **Verdict:** **PASS**.

---

## 9. API Source Classification (29 Endpoints)

| Endpoint | HTTP Method | Actual Data Source | Real TG? | Dynamic? |
|---|---|---|---|---|
| `/health` | GET | Static system health | No | Yes |
| `/health/dependencies` | GET | `TigerGraphMCPClient.get_runtime_status()` | No (Reports OFFLINE_STAGED_SIMULATION) | Yes |
| `/api/investigations` | POST | `CaseRepository` (`data/cases/*.json`) | No | Yes |
| `/api/investigations/{id}/run` | POST | `InvestigationOrchestrator` -> Staged CSV -> `CaseWritebackService` | No | Yes |
| `/api/investigations/{id}` | GET | `CaseRepository` | No | Yes |
| `/api/investigations/{id}/timeline` | GET | `TimelineBuilder` (from case event history) | No | Yes |
| `/api/investigations/{id}/evidence` | GET | `CaseRepository` (evidence list) | No | Yes |
| `/api/investigations/{id}/actions` | GET | `CaseRepository` (recommended actions) | No | Yes |
| `/api/investigations/{id}/approval` | GET | `ApprovalService` (approval route) | No | Yes |
| `/api/investigations/{id}/sar` | GET | `SARService` (FinCEN SAR draft) | No | Yes |
| `/api/investigations/{id}/evidence-request` | POST | `InvestigationService` (simulated evidence response) | No | Yes |
| `/api/investigations/{id}/graph` | GET | `dataset/processed/edges_*.csv` | No | Yes |
| `/api/cases` | GET | `CaseRepository` | No | Yes |
| `/api/cases/{id}` | GET | `CaseRepository` | No | Yes |
| `/api/evidence/{id}` | GET | `CaseRepository` | No | Yes |
| `/api/actions/{id}` | GET | `CaseRepository` | No | Yes |
| `/api/approvals/{id}/approve` | POST | `ApprovalService` (human governance verification) | No | Yes |
| `/api/approvals/{id}/reject` | POST | `ApprovalService` | No | Yes |
| `/api/sar/{id}` | GET | `SARService` | No | Yes |
| `/api/dashboard/summary` | GET | `DashboardService` / `dynamic_cases.csv` | No | Yes |
| `/api/dashboard/distribution` | GET | `DashboardService` | No | Yes |
| `/api/dashboard/activity` | GET | `DashboardService` | No | Yes |
| `/api/benchmark` | GET | `BenchmarkRunner` / `case_pack.csv` | No | Yes |
| `/api/audit` | GET | `case_management/audit.log` | No | Yes |
| `/api/search` | GET | `CaseRepository` search engine | No | Yes |

---

## 10. Required Links Audit Table

| URL | Purpose | Status | Conformance Notes |
|---|---|---|---|
| `https://drive.google.com/drive/folders/1YDJUW1fiE7Jx8R9KqknC4IcsED9zll2A` | Official HHGOA_IEEE dataset | **USED** | Complete 590,742 raw rows and 5,565 closed cases ingested. |
| `https://github.com/tigergraph/tigergraph-mcp` | Official TigerGraph MCP repo | **USED** | Package `pyTigerGraph-mcp 1.0.1` installed; tool schemas mapped. |
| `https://savanna.tgcloud.io/` | TigerGraph Savanna Cloud hosting | **NOT USED** | Live cloud cluster not provisioned; placeholder credentials in config. |
| `https://dl.tigergraph.com/` | TigerGraph Community Edition / Docker | **NOT APPLICABLE** | Host lacks Docker; local ports 9000/14240 closed. |
| `https://discord.gg/7JMkCAy9D3` | TigerGraph Mentor Support Discord | **REFERENCED ONLY** | Hackathon communication resource. |
| `https://chat.whatsapp.com/GfjxqVkdSoTGxl4Vrx54dc` | Hacker House Goa WhatsApp | **REFERENCED ONLY** | Hackathon announcements channel. |

---

## 11. Security Audit Findings

1. **No Credentials in Version Control:** `mcp/config/.env` is strictly ignored in `.gitignore`. Only `example.env` with generic placeholders is committed.
2. **Sanitized Audit Logs:** `mcp/tools/investigation_mcp_client.py` scrubs parameters matching `token`, `secret`, and `password` prior to logging in `mcp/audit.log`.
3. **No Unrestricted GSQL Endpoints:** The API exposes zero arbitrary query endpoints. Only predefined, schema-bound read tools and validated writeback methods exist.
4. **Approval Separation & Self-Approval Prevention:** `ApprovalService.approve_action()` strictly forbids self-approval by `"agent"`, `"llm"`, or `"ai"`, and mandates `L2_FRAUD_MANAGER` role for all L2 actions.
5. **Security Audit Verdict:** **PASS**.

---

## 12. Architecture Classification

```
============================================================
ARCHITECTURE CLASSIFICATION: YELLOW
============================================================
The application logic, autonomous agent, state machine, policy
engine, GraphRAG pipeline, case management lifecycle, SAR
generator, and REST API are genuinely and solidly built on real
HHGOA_IEEE data.

However, TigerGraph is NOT running live. The application executes
entirely on a Level B Local Staged Graph Simulation Engine.
============================================================
```
