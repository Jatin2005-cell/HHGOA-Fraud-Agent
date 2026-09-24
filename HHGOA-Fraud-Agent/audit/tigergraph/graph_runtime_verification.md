# TigerGraph Forensic Runtime Verification Report

**Audit Target:** TigerGraph Graph Database & GSQL Query Pipeline  
**Classification:** **PARTIALLY VERIFIED (Schema & GSQL Defined; Local Staged Graph Engine Active)**  

---

## 1. Environment & Network Reachability Audit

We conducted independent socket and protocol probes against the environment without exposing credentials:

- **Configured Host Domain:** `https://your-tigergraph-instance.i.tgcloud.io` (Placeholder in `example.env`)
- **Active Environment File:** `.env` does not contain remote TigerGraph cluster credentials.
- **Local Port 9000 (TigerGraph RESTPP):** `Connection Failed (TcpTestSucceeded = False)`
- **Local Port 14240 (TigerGraph GraphStudio):** `Connection Failed (TcpTestSucceeded = False)`
- **Host Docker Daemon:** `Not installed on host OS (Windows 11)`

### Finding:
There is currently **no live running TigerGraph database instance** reachable on localhost or configured with active cloud credentials in `.env`.

---

## 2. Graph Schema & GSQL Implementation Analysis

The TigerGraph GSQL artifacts are fully authored and compliant with the Phase 2 & Phase 3 specifications:

- **Schema Definition (`tigergraph/schema.gsql`):**
  - Vertices: `Customer`, `Card`, `Transaction`, `DeviceProfile`, `BillingRegion`, `EmailDomain`, `ClosedCase`, `DynamicCase`.
  - Directed Incident Edges: `OWNS_CARD`, `MADE_TRANSACTION`, `USED_DEVICE`, `IN_BILLING_REGION`, `USES_EMAIL_DOMAIN`, `CONNECTED_CARD`, `CASE_INVOLVES`, `CASE_ON_CARD`, `SIMILAR_TO`.
- **Batch Loading Job (`tigergraph/load_data.gsql`):**
  - Defines batch token mappings and vertex/edge generation from the raw CSV tables.
- **Investigation GSQL Queries (`tigergraph/queries/*.gsql`):**
  - `transaction_investigation_query.gsql`
  - `card_window_query.gsql`
  - `device_neighbors_query.gsql`
  - `region_anomaly_query.gsql`
  - `similar_closed_cases_query.gsql`
  - `customer_history_query.gsql`
  - `connected_cards_query.gsql`
  - `temporal_pattern_query.gsql`
  - `investigation_subgraph_query.gsql`

---

## 3. The Local Fallback Architecture (`dataset/processed/`)

Because a live TigerGraph cluster was not reachable during runtime, the project author implemented an autonomous fallback mechanism in `mcp/tools/investigation_mcp_client.py`:
- `TigerGraphMCPClient(use_local_fallback=True)`
- Instead of crashing or returning simulated fake strings, it executes the **exact GSQL traversal and filtering logic** directly against the staged graph tables in `dataset/processed/`:
  - `transactions.csv` (590,742 records)
  - `devices.csv` & `edges_from_device.csv` (144,432 records)
  - `edges_case_involves.csv` & `edges_case_on_card.csv`
  - `dynamic_cases.csv` (20 benchmark writeback records)

### Forensic Conclusion:
Data integrity is preserved because all graph context originates from the real HHGOA_IEEE tables. However, the database runtime is **staged local graph storage**, not an active TigerGraph Cloud or Docker service.
