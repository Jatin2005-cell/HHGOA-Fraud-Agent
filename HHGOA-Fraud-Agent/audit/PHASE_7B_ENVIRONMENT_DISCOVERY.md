# PHASE 7B — ENVIRONMENT DISCOVERY REPORT
## HHGOA_IEEE TigerGraph Migration Project

**Generated:** 2026-09-20  
**Phase:** 0 — Environment Discovery  
**Auditor:** Autonomous Phase 7B Migration Engineer  

---

## 1. PROJECT LOCATION & STRUCTURE

| Attribute | Value |
|---|---|
| **Root Directory** | `C:\Users\LOQ\Downloads\hhgoa fraud\HHGOA-Fraud-Agent` |
| **Parent Workspace** | `C:\Users\LOQ\Downloads\hhgoa fraud` |
| **OS Platform** | Windows 11 (AMD64) |
| **Active Backends** | FastAPI (uvicorn PID active on port 8000) |
| **Active Frontends** | Vite / React dev server (active on port 5174) |

### Core Project Directories
- `tigergraph/`: GSQL schema, loading scripts, and 9 GSQL investigation query files.
- `dataset/raw/`: Raw source IEEE-CIS and case pack datasets (`transactions.csv`, `identity.csv`, `case_pack.csv`, `closed_cases_history.csv`).
- `dataset/processed/`: Processed vertices (`customers.csv`, `cards.csv`, `devices.csv`, `billing_regions.csv`, `email_domains.csv`, `closed_cases.csv`, `dynamic_cases.csv`) and edges (`edges_made.csv`, `edges_from_device.csv`, `edges_case_on_card.csv`, etc.).
- `mcp/`: Official `pyTigerGraph` MCP client adapter (`mcp/tools/investigation_mcp_client.py`).
- `agent/`: 17-state GraphRAG agent orchestrator, policy engine, evaluation runner for HHG-001..HHG-020.
- `api/`: FastAPI routes (`/investigations`, `/cases`, `/evidence`, `/actions`, `/approvals`, `/sar`, `/dashboard`, `/benchmark`, `/audit`).
- `frontend/`: React/TypeScript Fraud Investigation Command Center (Phase 7A frozen).

---

## 2. HOST SYSTEM TOOLS & RUNTIMES

| Tool | Status | Path / Version |
|---|---|---|
| **Python** | ✅ Available | `C:\Users\LOQ\AppData\Local\Programs\Python\Python312\python.exe` (v3.12.10) |
| **Node.js** | ✅ Available | `D:\node.EXE` (v24.18.0) |
| **npm** | ✅ Available | `D:\npm.CMD` |
| **Git** | ✅ Available | `D:\Program Files\cmd\git.EXE` (v2.55.0.windows.3) |
| **Java** | ✅ Available | `C:\Program Files\Common Files\Oracle\Java\javapath\java.EXE` (Java 21.0.12 LTS) |
| **Docker** | ❌ Not Installed | Command not found |
| **WSL** | ❌ Not Installed | Windows Subsystem for Linux is not installed |

---

## 3. NETWORK PORTS & LOCAL SERVICES

| Port | Service | Status | Detail |
|---|---|---|---|
| **8000** | FastAPI API Server | 🟢 OPEN | Active uvicorn listener |
| **5174** | Vite Dev Frontend | 🟢 OPEN | Active React dashboard |
| **3306** | Local Database (MySQL) | 🟢 OPEN | Active local listener |
| **9000** | TigerGraph RESTPP | 🔴 CLOSED | No local TigerGraph daemon |
| **14240**| TigerGraph GraphStudio | 🔴 CLOSED | No local TigerGraph daemon |
| **10000**| TigerGraph GSQL | 🔴 CLOSED | No local TigerGraph daemon |
| **5432** | PostgreSQL | 🔴 CLOSED | No active listener |

---

## 4. SECRETS & GIT HYGIENE INSPECTION

- **Parent `.gitignore`**: Verified at `C:\Users\LOQ\Downloads\hhgoa fraud\.gitignore`.
- **Ignored Patterns**:
  ```gitignore
  .env
  *.env
  !.env.example
  !example.env
  config/.env
  mcp/config/.env
  ```
- **Live `.env` Presence**: No `.env` containing unmasked production secrets exists.
- **Git Repository**: Workspace is not directly initialized as a nested sub-repo (tracked under parent/unversioned workspace).

---

## 5. TIGERGRAPH ASSETS IN REPOSITORY

1. **Schema DDL**: `tigergraph/schema.gsql` (Target: `FraudInvestigationGraph`, 8 vertex types, 9 edge types).
2. **Data Loader**: `tigergraph/load_data.gsql` and `tigergraph/preprocess_and_load.py`.
3. **9 Investigation Queries**:
   - `transaction_investigation_query.gsql`
   - `card_window_query.gsql`
   - `device_neighbors_query.gsql`
   - `region_anomaly_query.gsql`
   - `similar_closed_cases_query.gsql`
   - `customer_history_query.gsql`
   - `connected_cards_query.gsql`
   - `temporal_pattern_query.gsql`
   - `investigation_subgraph_query.gsql`
4. **MCP Adapter**: `mcp/tools/investigation_mcp_client.py` natively supports `pyTigerGraph` connection with transparent fallback.

---

## 6. DISCOVERY CONCLUSION

The codebase contains all necessary GSQL queries, loading scripts, schemas, and `pyTigerGraph` integration artifacts to execute Phase 7B immediately upon connecting to a real TigerGraph instance.
Local Docker and WSL are not available on this host machine, indicating that live TigerGraph connectivity must point to a remote/cloud instance (e.g. TigerGraph Cloud / Savanna at `*.i.tgcloud.io`).
