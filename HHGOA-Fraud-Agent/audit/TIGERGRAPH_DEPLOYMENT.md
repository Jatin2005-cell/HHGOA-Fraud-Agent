# TigerGraph Deployment & Migration Manual

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Challenge:** Hacker House Goa 2026  
**Target Graph:** `FraudInvestigationGraph`  
**Purpose:** Standard Operating Procedure to provision TigerGraph (Savanna Cloud or Docker CE) and migrate from Level B (Offline Simulation) to Level A (Live TigerGraph).

---

## 1. Provisioning Options

### Option 1: TigerGraph Savanna Cloud (Recommended)
1. Go to [TigerGraph Savanna Portal](https://savanna.tgcloud.io/) or [TigerGraph Cloud](https://tgcloud.io/).
2. Click **Create Solution** -> Select **Blank Graph** or **Enterprise Trial**.
3. Choose Cloud Provider (AWS / GCP / Azure) and Region (e.g., `us-east-1`).
4. Set Solution Name: `hhgoa-fraud-agent`.
5. Set Initial Password for user `tigergraph`.
6. Once the cluster status shows **READY**, note the domain (e.g. `https://hhgoa-fraud.i.tgcloud.io`).

### Option 2: Docker Community Edition (Local Linux/macOS or Windows WSL2)
```bash
docker pull docker.tigergraph.com/tigergraph-ce:latest
docker run -d -p 9000:9000 -p 14240:14240 --name tg-fraud -t docker.tigergraph.com/tigergraph-ce:latest
docker exec -it tg-fraud gadmin status
```

---

## 2. Environment Configuration

Populate `mcp/config/.env` (and never commit this file):

```ini
TG_HOST=https://<your-subdomain>.i.tgcloud.io
TG_GRAPHNAME=FraudInvestigationGraph
TG_USERNAME=tigergraph
TG_PASSWORD=<your_secure_password>
TG_SECRET=<your_tg_secret>
TG_TOKEN=<your_generated_api_token>
TG_RESTPP_PORT=443
TG_ALLOWED_TOOLS=query,read-only
TG_BLOCKED_TOOLS=destructive
```

---

## 3. Schema Creation

Execute the schema script via GSQL CLI or pyTigerGraph:

```bash
gsql -u tigergraph -p <your_password> tigergraph/schema.gsql
```

The schema creates:
- **Vertices:**
  - `Transaction` (PRIMARY_ID `txn_id` UINT)
  - `Customer` (PRIMARY_ID `customer_id` STRING)
  - `Card` (PRIMARY_ID `card_id` STRING)
  - `DeviceProfile` (PRIMARY_ID `device_hash` STRING)
  - `BillingRegion` (PRIMARY_ID `region_id` STRING)
  - `EmailDomain` (PRIMARY_ID `domain` STRING)
  - `ClosedCase` (PRIMARY_ID `case_id` STRING)
  - `DynamicCase` (PRIMARY_ID `case_id` STRING)
- **Edges:**
  - `MADE` (`Card` -> `Transaction`)
  - `OWNS` (`Customer` -> `Card`)
  - `FROM_DEVICE` (`Transaction` -> `DeviceProfile`)
  - `BILLED_IN` (`Transaction` -> `BillingRegion`)
  - `PURCHASER_EMAIL`, `RECIPIENT_EMAIL` (`Transaction` -> `EmailDomain`)
  - `NEXT_TRANSACTION` (`Transaction` -> `Transaction`)
  - `CASE_INVOLVES` (`ClosedCase` / `DynamicCase` -> `Transaction`)
  - `CASE_ON_CARD` (`ClosedCase` / `DynamicCase` -> `Card`)

---

## 4. Dataset Loading

Run the automated data loader:

```bash
python tigergraph/preprocess_and_load.py --mode=cloud
```

Alternatively, run GSQL loading jobs:
```bash
gsql -g FraudInvestigationGraph tigergraph/load_data.gsql
```

Data to load from `dataset/processed/`:
- 15,000 active transactions (`transactions.csv`)
- 12,793 cards (`cards.csv`)
- 10,381 devices (`devices.csv`)
- 5,565 closed historical cases (`closed_cases.csv`)
- All associated edge files (`edges_*.csv`)

---

## 5. GSQL Query Installation

Install the 9 investigation queries into TigerGraph:

```bash
gsql -g FraudInvestigationGraph tigergraph/queries/transaction_investigation_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/card_window_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/device_neighbors_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/region_anomaly_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/similar_closed_cases_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/customer_history_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/connected_cards_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/temporal_pattern_query.gsql
gsql -g FraudInvestigationGraph tigergraph/queries/investigation_subgraph_query.gsql

# Compile and publish queries to RESTPP endpoints:
gsql -g FraudInvestigationGraph "INSTALL QUERY ALL"
```

---

## 6. Activation & Verification

1. In `mcp/tools/investigation_mcp_client.py`, switch mode:
   ```python
   # Set default to live mode:
   client = TigerGraphMCPClient(use_local_fallback=False)
   ```
2. Verify live connectivity:
   ```bash
   python -c "from mcp.tools.investigation_mcp_client import TigerGraphMCPClient; c = TigerGraphMCPClient(use_local_fallback=False); print(c.get_runtime_status())"
   ```
3. Run test suite against live cluster:
   ```bash
   python -m pytest tests/
   ```
4. Verify `/health/dependencies` returns `"data_mode": "LIVE_TIGERGRAPH"`.
