# Forensic Red Flag Audit & Gap Analysis

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Audit Standard:** Strict Forensic Scrutiny (No Assumptions, Direct Source Evidence)  
**Last Updated:** Phase 6.6 Verification (September 20, 2026)  

---

## 1. Summary of Red Flag Detections

| # | Potential Risk / Red Flag | Evidence Inspected | Forensic Finding | Severity |
|---|---|---|---|---|
| **RF-01** | **Live TigerGraph Database Connectivity** | Sockets `127.0.0.1:9000` & `14240`, `.env` configs | **RED FLAG CONFIRMED:** No live TigerGraph container or active Cloud instance is connected. Runtime relies on `use_local_fallback=True` in `investigation_mcp_client.py`. | **HIGH** |
| **RF-02** | **Graph Writeback Authenticity** | `case_management/graph_writeback.py` | **RED FLAG CONFIRMED:** Writeback mutates staged local graph tables (`dataset/processed/dynamic_cases.csv`) rather than issuing live TigerGraph RESTPP write mutations. | **MEDIUM** |
| **RF-03** | **Hard-Coded Benchmark Outputs** | Grep analysis of `agent/core/` for `HHG-001`..`020` | **NO RED FLAG (PASS):** Zero hardcoded case outputs or answers found in agent logic; all 20 cases run dynamically. | **NONE** |
| **RF-04** | **Exposed Secrets or Tracked Credentials** | Regex scan of all `.env`, `.py`, `.md` files | **NO RED FLAG (PASS):** Zero real passwords/keys exposed; only placeholders in `example.env`. | **NONE** |
| **RF-05** | **Incorrect Dataset or Altered Dimensions** | Cryptographic hash & row count audit | **NO RED FLAG (PASS):** Exact match: 590,742 transactions, 144,432 identity rows, 5,565 closed cases, 20 exam cases. | **NONE** |
| **RF-06** | **Benchmark Data Contamination / Leakage** | Overlap check between benchmark and history | **NO RED FLAG (PASS):** Exact zero overlap (`set()`); benchmark cases are exclusively from the final 2 evaluation months. | **NONE** |
| **RF-07** | **Simulated Additional Evidence vs Fake Graph** | `agent/core/investigation_orchestrator.py` | **GOVERNED SIMULATION:** Additional evidence (step-up auth, customer call response) is simulated per challenge design guidelines (Page 2). | **LOW** |
| **RF-08** | **Phase 4 MCP Package Legitimacy** | Python environment package audit | **NO RED FLAG (PASS):** Official `pyTigerGraph-mcp 1.0.1` and `mcp 2.2.0` packages are installed. | **NONE** |
| **RF-09** | **Refuted Claim of Official Package Fallback** | Source inspection of site-packages `tigergraph_mcp` | **RED FLAG CONFIRMED & DISCLOSED:** Official `pyTigerGraph-mcp` does NOT contain any fallback engine. The local fallback engine is 100% project-authored code in `mcp/tools/investigation_mcp_client.py`. | **HIGH** |
| **RF-10** | **Misleading API Dependency Reporting** | `/health/dependencies` in `api/main.py` | **RESOLVED IN PHASE 6.6:** Previously hardcoded `"tigergraph_engine": "ONLINE"`. Now dynamically and transparently reports `"data_mode": "OFFLINE_STAGED_SIMULATION"`, `"graph_verified": false`, and `"tigergraph_engine": "OFFLINE (Staged Simulation Active)"`. | **RESOLVED** |
| **RF-11** | **Phase 7 UI Readiness Gate** | Phase 6.6 Gate Audit (`audit/PHASE_7_GATE.md`) | **GATE BLOCKED:** Phase 7 cannot claim Live TigerGraph execution without a live instance. Must be explicitly flagged as `OFFLINE_STAGED_SIMULATION` mode in UI or provision live cluster. | **HIGH** |

---

## 2. Detailed Findings on Critical Red Flags

### RF-01 & RF-09: TigerGraph Live Cluster vs. Project Staged Simulation
- **Report Claim:** Previous phase reports claimed that the official `pyTigerGraph-mcp 1.0.1` client automatically uses its local fallback engine over `dataset/processed/`.
- **Forensic Reality:** Inspection of `site-packages/tigergraph_mcp` revealed zero occurrences of fallback, simulation, or Pandas data loading. The official package connects exclusively to live TigerGraph instances via `pyTigerGraph.AsyncTigerGraphConnection`.
- **Project Implementation:** The fallback engine is entirely project-authored code located in `mcp/tools/investigation_mcp_client.py` (`_execute_local_query_engine()`). It replicates GSQL queries in pure Pandas over `dataset/processed/*.csv`.
- **Architectural Resolution:** This capability is now formalized as a legitimate developer feature:
  - **LIVE MODE:** `pyTigerGraph` -> RESTPP -> Compiled GSQL on live TigerGraph cluster.
  - **OFFLINE SIMULATION MODE:** Local staged dataset -> simulation adapter -> Agent.
  Both modes are machine-readable via `client.get_runtime_status()`.

### RF-02: Graph Writeback & Readback
- **Report Claim:** "Graph writeback and readback verified."
- **Forensic Reality:** The system writes DynamicCase vertices and incident edges to `dataset/processed/dynamic_cases.csv`, `edges_case_involves.csv`, and `edges_case_on_card.csv`.
- **Authenticity Standard:** Writing to local CSV or Parquet files is **NOT** equivalent to live TigerGraph writeback.
- **Classification:**
  - `GRAPH WRITEBACK TO TIGERGRAPH = NOT VERIFIED` (Level B Staged Store Writeback = VERIFIED).
  - `GRAPH READBACK FROM TIGERGRAPH = NOT VERIFIED` (Level B Staged Store Readback = VERIFIED).

### RF-10: Transparent Dependency & Provenance Reporting
- **Issue:** Previously, `/health/dependencies` returned `"tigergraph_engine": "ONLINE"`, creating a false impression of a connected live database cluster.
- **Remediation:** In Phase 6.6, `/health/dependencies` was updated to dynamically invoke `get_runtime_status()` from the MCP layer. It now reports:
  ```json
  {
    "status": "healthy",
    "data_mode": "OFFLINE_STAGED_SIMULATION",
    "graph_name": null,
    "graph_verified": false,
    "schema_verified": false,
    "mcp_verified": false,
    "writeback_verified": false,
    "dependencies": {
      "tigergraph_engine": "OFFLINE (Staged Simulation Active)",
      "mcp_server": "READY (Local Simulation Fallback)",
      "case_management_store": "READY",
      "investigation_agent": "ONLINE"
    }
  }
  ```
