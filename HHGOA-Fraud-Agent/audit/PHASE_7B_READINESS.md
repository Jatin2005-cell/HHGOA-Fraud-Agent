# PHASE 7B — LIVE TIGERGRAPH MIGRATION READINESS SPECIFICATION
## HHGOA_IEEE Fraud Investigation System

**Date:** 2026-09-20  
**Phase 7A Status:** FROZEN & GREEN  
**Phase 7B Status:** PENDING PROVISIONING (DO NOT IMPLEMENT UNTIL CREDENTIALS PROVIDED)

---

## 1. OBJECTIVE

Migrate the operational system from **OFFLINE_STAGED_SIMULATION** to **LIVE_TIGERGRAPH** (Level A) seamlessly, without modifying the frontend, agent state machine, policy engine, or FastAPI contracts.

When live connectivity is established:
1. `GET /health/dependencies` automatically reflects:
   - `data_mode`: `LIVE_TIGERGRAPH`
   - `graph_verified`: `true`
   - `mcp_verified`: `true`
   - `writeback_verified`: `true`
2. The React frontend `ProvenanceBanner` transitions automatically from amber `OFFLINE STAGED SIMULATION` to emerald `LIVE TIGERGRAPH`.

---

## 2. PREREQUISITES STILL REQUIRED FOR LEVEL-A VALIDATION

Before Phase 7B execution can begin, the following 12 items are strictly required:

1. **Real TigerGraph / Savanna Instance**: A live, accessible TigerGraph 3.x / 4.x cloud or on-premise instance.
2. **Real TG_HOST**: Valid hostname / IP address with network ingress to ports `9000` (RESTPP), `14240` (GraphStudio), and `10000` (GSQL).
3. **Valid Authentication**: Verified username/password credentials and an API secret/token (`TG_SECRET` / `TG_TOKEN`).
4. **FraudInvestigationGraph Creation**: Explicit creation of the target graph container via GSQL (`CREATE GRAPH FraudInvestigationGraph(...)`).
5. **Schema Deployment**: Execution of graph schema DDL establishing vertices (`Case`, `Transaction`, `User`, `Card`, `DeviceProfile`, `IPAddress`) and edges (`TRANS_OF_CARD`, `CASE_ON_CARD`, `DEVICE_ASSOCIATED`, `PEER_OF`, etc.).
6. **Real Dataset Loading**: Successful execution of loading jobs importing the IEEE-CIS / HHGOA dataset into `FraudInvestigationGraph`.
7. **9 GSQL Queries Installation**: Installation and compilation of all 9 core investigation queries:
   - `get_transaction_subgraph`
   - `find_shared_card_cases`
   - `detect_rapid_velocity`
   - `trace_device_fingerprints`
   - `calculate_community_risk`
   - `find_ip_clusters`
   - `get_merchant_risk_profile`
   - `writeback_investigation_verdict`
   - `readback_case_verification`
8. **Live MCP Connection**: Configuration of `pyTigerGraph-mcp` pointing to the live instance, validating tool list responses (`tg_run_installed_query`, `tg_get_vertex_count`).
9. **TigerGraph-Backed Investigation**: End-to-end execution of agent GraphRAG state transitions querying the live graph cluster.
10. **TigerGraph Writeback**: Dynamic insertion of `Case` vertices and `CASE_ON_CARD` edges to persist investigation verdicts into the live graph.
11. **TigerGraph Readback**: Instant post-investigation readback query to verify vertex/edge insertion and attribute consistency.
12. **Level-A 20-Case Validation**: Full execution of the benchmark suite (HHG-001 through HHG-020) against the live cluster with 100% telemetry verification.

---

## 3. STRICT BOUNDARY ENFORCEMENT

- **DO NOT** fabricate TigerGraph connectivity.
- **DO NOT** change `graph_verified` to `true` while running offline.
- **DO NOT** start Phase 7B execution until the real TigerGraph instance is provisioned and connectivity parameters are supplied.

---

## 4. EXECUTION GATE CHECK RESULTS (2026-09-20)

| Variable / Target | Status | Detection Result |
|-------------------|--------|------------------|
| `TG_HOST` | ❌ NOT SET | Missing from environment & `.env` |
| `TG_GRAPHNAME` | ❌ NOT SET | Missing (defaults to schema target `FraudInvestigationGraph`) |
| `TG_USERNAME` | ❌ NOT SET | Missing from environment |
| `TG_PASSWORD` / `TG_SECRET` | ❌ NOT SET | Missing from environment |
| `TG_TOKEN` | ❌ NOT SET | Missing from environment |
| `127.0.0.1:9000` (RESTPP) | ❌ CLOSED | Connection timed out / no listener |
| `127.0.0.1:14240` (Studio) | ❌ CLOSED | Connection timed out / no listener |
| `127.0.0.1:10000` (GSQL) | ❌ CLOSED | Connection timed out / no listener |

### Gate Verdict:
**PHASE 7B BLOCKED — TIGERGRAPH CREDENTIALS REQUIRED**

As mandated by Section 1 and Stop Conditions:
1. No synthetic credentials or mock cloud connections have been fabricated.
2. System runtime remains securely anchored in **`OFFLINE_STAGED_SIMULATION`**.
3. All 31 backend tests, FastAPI contracts, and the frozen React UI continue operating with 100% genuine data fidelity.

