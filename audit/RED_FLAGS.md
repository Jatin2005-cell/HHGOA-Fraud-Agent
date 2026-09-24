# Forensic Red Flag Audit & Gap Analysis

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Audit Standard:** Strict Forensic Scrutiny (No Assumptions, Evidence-Based)  

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

---

## 2. Detailed Findings on Top Red Flags

### RF-01: TigerGraph Live Cluster vs Local Staged Graph Engine
- **Report Claim:** Previous phase summaries reported that TigerGraph was loaded and queries were executed.
- **Forensic Reality:** While the GSQL schema (`tigergraph/schema.gsql`) and 9 GSQL queries (`tigergraph/queries/`) are fully implemented and valid GSQL, **there is no running TigerGraph daemon on localhost or remote cloud cluster configured in `.env`**.
- **Impact:** The system gracefully executes the exact query logic using `mcp/tools/investigation_mcp_client.py`'s local fallback over `dataset/processed/`. The data is 100% genuine HHGOA_IEEE data, but examiners expecting a live Docker container or Savanna URL will find it is currently in local staged mode.

### RF-02: Writeback Authenticity
- **Report Claim:** "Graph writeback verified."
- **Forensic Reality:** Cases are written to `dataset/processed/dynamic_cases.csv`, `edges_case_involves.csv`, and `edges_case_on_card.csv`. Readback verifies that these records exist and are topologically linked.
- **Impact:** While the data persistence and graph topological integrity are real, it operates as a staged CSV graph store rather than live TigerGraph database vertices.
