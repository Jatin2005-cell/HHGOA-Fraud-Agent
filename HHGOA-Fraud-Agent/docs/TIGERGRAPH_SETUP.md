# TigerGraph Setup & Data Ingestion Manual

**Document Version:** 1.0.0  
**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Graph Name:** `FraudInvestigationGraph`  
**Status:** Validated Production Setup (100% Tests Passing)

---

## 1. Graph Overview

The `FraudInvestigationGraph` is designed to power real-time fraud pattern detection, multi-hop entity resolution, temporal transaction chain analysis, and case memory retrieval for the AI fraud investigation agent.

### 1.1 Architecture & Metrics

| Entity Type | Vertex / Edge Name | Validated Count | Description |
|---|---|---|---|
| **Vertex** | `Customer` | **13,553** | Bank customer account entities. |
| **Vertex** | `Card` | **24,234** | Unique card instruments (`Cxxxxx-K1`, `Cxxxxx-K2`, `Cxxxxx-K3`). |
| **Vertex** | `Transaction` | **590,742** | 6 months of card transactions (July–Dec 2016). |
| **Vertex** | `DeviceProfile` | **9,706** | Hardware/browser fingerprints (`DEV_<md5>`). |
| **Vertex** | `BillingRegion` | **332** | Geographic card billing regions (`REG_<addr1>`). |
| **Vertex** | `EmailDomain` | **60** | Unique email service domains (`gmail.com`, etc.). |
| **Vertex** | `ClosedCase` | **5,565** | Finished historical investigations (months 1–4). |
| **Vertex** | `DynamicCase` | *Dynamic (0)* | Reserved schema for agent-created/updated cases. |
| **Edge** | `OWNS` | **24,234** | `Customer` $\rightarrow$ `Card`. |
| **Edge** | `MADE` | **590,742** | `Card` $\rightarrow$ `Transaction`. |
| **Edge** | `FROM_DEVICE` | **144,432** | `Transaction` $\rightarrow$ `DeviceProfile` (online transactions). |
| **Edge** | `NEXT_TRANSACTION` | **576,264** | Chronological link between adjacent txns on same card. |
| **Edge** | `BILLED_IN` | **525,003** | `Transaction` $\rightarrow$ `BillingRegion`. |
| **Edge** | `PURCHASER_EMAIL` | **496,262** | `Transaction` $\rightarrow$ `EmailDomain` (`P_emaildomain`). |
| **Edge** | `RECIPIENT_EMAIL` | **137,453** | `Transaction` $\rightarrow$ `EmailDomain` (`R_emaildomain`). |
| **Edge** | `CASE_INVOLVES` | **14,955** | `ClosedCase` $\rightarrow$ `Transaction`. |
| **Edge** | `CASE_ON_CARD` | **5,565** | `ClosedCase` $\rightarrow$ `Card`. |
| **Edge** | `CONNECTED_CARD` | **92** | `ClosedCase` $\rightarrow$ `Card` (multi-card compromise). |

---

## 2. Vertex & Edge Specifications

### 2.1 Vertices
- **`Customer(PRIMARY_ID customer_id STRING, id STRING, total_cards INT)`**
- **`Card(PRIMARY_ID card_id STRING, id STRING, card1 INT, card2 FLOAT, card3 FLOAT, card4 STRING, card5 FLOAT, card6 STRING, status STRING)`**
- **`Transaction(PRIMARY_ID txn_id STRING, id STRING, ts DATETIME, amount FLOAT, product_cd STRING, channel STRING, risk_score FLOAT, addr1 FLOAT, addr2 FLOAT, dist1 FLOAT, dist2 FLOAT, p_emaildomain STRING, r_emaildomain STRING, m_flags STRING)`**
- **`DeviceProfile(PRIMARY_ID device_hash STRING, device_info STRING, device_type STRING, os STRING, browser STRING, screen_res STRING, proxy_status STRING, device_status STRING)`**
- **`BillingRegion(PRIMARY_ID region_id STRING, region_code FLOAT, country_code FLOAT)`**
- **`EmailDomain(PRIMARY_ID domain_name STRING, name STRING, is_disposable BOOL)`**
- **`ClosedCase(PRIMARY_ID case_id STRING, customer_id STRING, card_id STRING, opened_at DATETIME, closed_at DATETIME, outcome STRING, pattern STRING, first_fraud_txn_id STRING, n_txns INT, exposure_usd FLOAT, actions_taken STRING, report_filed STRING, analyst_notes STRING)`**
- **`DynamicCase(PRIMARY_ID case_id STRING, opened_at DATETIME, closed_at DATETIME, status STRING, verdict STRING, fraud_probability FLOAT, pattern STRING, pattern_description STRING, exposure_usd FLOAT, stop_reason STRING, sar_filed BOOL, summary STRING)`**

### 2.2 Edges
- **`OWNS(FROM Customer, TO Card, issued_ts DATETIME, is_primary BOOL)`**
- **`MADE(FROM Card, TO Transaction, ts DATETIME)`**
- **`FROM_DEVICE(FROM Transaction, TO DeviceProfile, id_15_status STRING, id_23_proxy STRING, match_status STRING)`**
- **`BILLED_IN(FROM Transaction, TO BillingRegion, dist1 FLOAT)`**
- **`PURCHASER_EMAIL(FROM Transaction, TO EmailDomain)`**
- **`RECIPIENT_EMAIL(FROM Transaction, TO EmailDomain)`**
- **`NEXT_TRANSACTION(FROM Transaction, TO Transaction, delta_seconds INT, delta_amount FLOAT, same_region BOOL)`**
- **`CASE_INVOLVES(FROM ClosedCase|DynamicCase, TO Transaction, is_first_fraud BOOL, is_flagged_trigger BOOL)`**
- **`CASE_ON_CARD(FROM ClosedCase|DynamicCase, TO Card)`**
- **`CONNECTED_CARD(FROM ClosedCase|DynamicCase, TO Card, connection_reason STRING)`**

---

## 3. Data Processing & Staging Architecture

### 3.1 Card ID Derivation Logic
In the raw data, transactions specify `customer_id` and card attributes (`card1` through `card6`), while `closed_cases_history.csv` and `case_pack.csv` identify cards using suffixes: `Cxxxxx-K1`, `Cxxxxx-K2`, `Cxxxxx-K3`.

The mapping pipeline implements a 100% deterministic, zero-conflict derivation:
1. **Ground-Truth Calibration:** 14,975 transactions involved in historical closed cases and benchmark cases explicitly bind `(customer_id, card_tuple)` $\rightarrow$ `card_id`. Tested across all 5,565 closed cases: **0 conflicts detected**.
2. **Deterministic Sequence Resolution:** For unassigned card tuples of any customer, tuples are sorted chronologically by earliest transaction timestamp (`min(ts)`). Unassigned tuples receive the lowest unused suffix (`K1`, `K2`, `K3`).
3. **Outcome:** 24,234 valid `Card` vertices with zero orphan transactions.

### 3.2 Deterministic Device Hashing
Device fingerprints in `identity.csv` are normalized and hashed:
$$\text{device\_hash} = \text{"DEV\_"} + \text{MD5}(\text{DeviceInfo} \parallel \text{id\_30} \parallel \text{id\_31} \parallel \text{id\_33})[:16]$$
- Resolves 144,432 online identity rows into **9,706 unique DeviceProfile vertices**.
- Identical client fingerprints resolve to the exact same vertex across all customers.

### 3.3 Temporal Sequence Generation (`NEXT_TRANSACTION`)
Transactions are partitioned by `card_id` and ordered by timestamp `ts`:
- Connects $T_i \rightarrow T_{i+1}$.
- Computes `delta_seconds = int((ts_{i+1} - ts_i).total_seconds())`.
- Computes `delta_amount = round(amount_{i+1} - amount_i, 2)`.
- Flags `same_region = (addr1_{i+1} == addr1_i)`.
- Produces **576,264 sequential edges** enabling single-hop card-testing and velocity analysis.

---

## 4. Execution & Setup Commands

### 4.1 Step 1: Run Preprocessing & Staging
To regenerate the staging dataset in `dataset/processed/`:
```powershell
python HHGOA-Fraud-Agent/tigergraph/preprocess_and_load.py
```

### 4.2 Step 2: Validate Data Integrity
Run the automated validation suite:
```powershell
python HHGOA-Fraud-Agent/tigergraph/validation/validate_graph.py
```
*Expected Result: `OVERALL VALIDATION STATUS: PASS` with 0 errors.*

### 4.3 Step 3: Deploy to TigerGraph (Savanna or Community Edition)

#### Option A: GSQL Shell (Interactive or Scripted)
```bash
# 1. Create Schema
gsql tigergraph/schema.gsql

# 2. Run Loading Job
gsql -g FraudInvestigationGraph tigergraph/load_data.gsql

# 3. Trigger Data Ingestion
gsql -g FraudInvestigationGraph "RUN LOADING JOB load_fraud_data USING \
  customers_file=\"$(pwd)/dataset/processed/customers.csv\", \
  cards_file=\"$(pwd)/dataset/processed/cards.csv\", \
  txns_file=\"$(pwd)/dataset/processed/transactions.csv\", \
  devices_file=\"$(pwd)/dataset/processed/devices.csv\", \
  regions_file=\"$(pwd)/dataset/processed/billing_regions.csv\", \
  email_file=\"$(pwd)/dataset/processed/email_domains.csv\", \
  cases_file=\"$(pwd)/dataset/processed/closed_cases.csv\", \
  edges_owns_file=\"$(pwd)/dataset/processed/edges_owns.csv\", \
  edges_made_file=\"$(pwd)/dataset/processed/edges_made.csv\", \
  edges_from_dev_file=\"$(pwd)/dataset/processed/edges_from_device.csv\", \
  edges_billed_file=\"$(pwd)/dataset/processed/edges_billed_in.csv\", \
  edges_p_email_file=\"$(pwd)/dataset/processed/edges_purchaser_email.csv\", \
  edges_r_email_file=\"$(pwd)/dataset/processed/edges_recipient_email.csv\", \
  edges_next_txn_file=\"$(pwd)/dataset/processed/edges_next_transaction.csv\", \
  edges_case_txn_file=\"$(pwd)/dataset/processed/edges_case_involves.csv\", \
  edges_case_card_file=\"$(pwd)/dataset/processed/edges_case_on_card.csv\", \
  edges_conn_card_file=\"$(pwd)/dataset/processed/edges_connected_card.csv\""
```

#### Option B: Deploy Graph Queries
```bash
gsql -g FraudInvestigationGraph tigergraph/queries/investigation_queries.gsql
gsql -g FraudInvestigationGraph "INSTALL QUERY ALL"
```

---

## 5. Verification & Health Check Queries

Verify graph population via GSQL:
```gsql
USE GRAPH FraudInvestigationGraph

// Verify vertex counts
PRINT Customer.size();
PRINT Card.size();
PRINT Transaction.size();
PRINT DeviceProfile.size();
PRINT ClosedCase.size();

// Verify sample multi-hop path
INTERPRET QUERY () FOR GRAPH FraudInvestigationGraph {
    Start = {Customer.*};
    Cards = SELECT c FROM Start:cust -(OWNS:e)-> Card:c LIMIT 5;
    Txns = SELECT t FROM Cards:c -(MADE:e)-> Transaction:t LIMIT 10;
    PRINT Cards, Txns;
}
```

---

## 6. Known Characteristics & Boundary Handling

1. **In-Person vs Online Channel Isolation:**
   - Transactions with `ProductCD == 'W'` are flagged as `in_person`.
   - Verified that exactly 0 in-person transactions possess `FROM_DEVICE` edges or identity records.
   - All 144,432 identity records connect exclusively to `online` transactions (`channel == 'online'`).
2. **Benchmark Set Isolation:**
   - Benchmark cases from `case_pack.csv` are deliberately **not** loaded into `ClosedCase`.
   - They remain isolated as external evaluation input for the agent to investigate during Phase 5.
3. **Dynamic Cases:**
   - `DynamicCase` vertices have 0 initial records. The AI agent instantiates them at runtime as alerts are investigated, populated with calibrated `fraud_probability`, `verdict`, and `actions_taken`.
