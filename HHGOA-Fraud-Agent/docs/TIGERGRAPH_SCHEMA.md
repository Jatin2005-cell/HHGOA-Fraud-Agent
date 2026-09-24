# TigerGraph Fraud Knowledge Graph — Schema & Query Architecture

**Document Status:** Approved Architectural Specification  
**Version:** 2.0.0  
**Target Engine:** TigerGraph 3.x / 4.x (Savanna Cloud & Community Edition)  
**Challenge:** TigerGraph Agentic Fraud Investigation (Hacker House Goa 2026)

---

## 1. Architectural Overview & Graph Rationale

The fraud investigation agent relies on a multi-relational Knowledge Graph (KG) built on TigerGraph. Relational databases fall short when detecting synthetic identities, distributed device rings, or multi-hop card-testing cascades. TigerGraph's native parallel graph architecture enables real-time deep-link traversal ($k$-hop pattern matching), temporal transaction sequence analysis, and GraphRAG grounding directly within the LLM agent's decision loop.

### Core Domain Entities Mapped to Graph
The schema models entities and relationships supported directly by the IEEE-CIS raw files (`transactions.csv`, `identity.csv`, `closed_cases_history.csv`, `case_pack.csv`, and `README.md`):

1. **Transactional Domain:** `Customer`, `Card` (Account), `Transaction`, `DeviceProfile`, `BillingRegion`, `EmailDomain`.
2. **Case Memory & Institutional Domain:** `Case` (unifying historical closed investigations and dynamic agent-opened cases).
3. **Governance & GraphRAG Domain:** `FraudPattern` (typology definitions) and `PolicyRule` (bank policies R1–R10).

---

## 2. Vertex Definitions & Attributes

```
+-------------------------------------------------------------------------------------------------------+
|                                              VERTICES                                                 |
+-------------------+--------------------+----------------------+---------------------------------------+
| Vertex Name       | Primary ID (Type)  | Secondary Indexes    | Attributes                            |
+-------------------+--------------------+----------------------+---------------------------------------+
| Customer          | customer_id STRING | None                 | id STRING, total_cards INT            |
| Card              | card_id STRING     | card1, card4         | id STRING, card1 INT, card2 FLOAT,    |
|                   |                    |                      | card3 FLOAT, card4 STRING,            |
|                   |                    |                      | card5 FLOAT, card6 STRING,            |
|                   |                    |                      | status STRING                         |
| Transaction       | txn_id STRING      | ts, risk_score, addr1| id STRING, ts DATETIME, amount FLOAT, |
|                   |                    |                      | product_cd STRING, channel STRING,    |
|                   |                    |                      | risk_score FLOAT, addr1 FLOAT,        |
|                   |                    |                      | addr2 FLOAT, dist1 FLOAT, dist2 FLOAT,|
|                   |                    |                      | p_emaildomain STRING,                 |
|                   |                    |                      | r_emaildomain STRING, m_flags STRING  |
| DeviceProfile     | device_hash STRING | device_type, os      | device_hash STRING,                   |
|                   |                    |                      | device_info STRING,                   |
|                   |                    |                      | device_type STRING, os STRING,        |
|                   |                    |                      | browser STRING, screen_res STRING,    |
|                   |                    |                      | proxy_status STRING,                  |
|                   |                    |                      | device_status STRING                  |
| BillingRegion     | region_id STRING   | None                 | region_code FLOAT, country_code FLOAT |
| EmailDomain       | domain_name STRING | None                 | name STRING, is_disposable BOOL       |
| Case              | case_id STRING     | status, verdict,     | case_id STRING, case_type STRING,     |
|                   |                    | pattern              | status STRING, verdict STRING,        |
|                   |                    | opened_at DATETIME, closed_at DATETIME|
|                   |                    |                      | fraud_probability FLOAT,              |
|                   |                    |                      | exposure_usd FLOAT, n_txns INT,       |
|                   |                    |                      | actions_taken STRING,                 |
|                   |                    |                      | report_filed BOOL,                    |
|                   |                    |                      | analyst_notes STRING, summary STRING  |
| FraudPattern      | pattern_id STRING  | None                 | name STRING, description STRING,      |
|                   |                    |                      | typical_indicators STRING             |
| PolicyRule        | rule_id STRING     | None                 | name STRING, description STRING,      |
|                   |                    |                      | mandatory_actions STRING,             |
|                   |                    |                      | default_approval_route STRING         |
+-------------------+--------------------+----------------------+---------------------------------------+
```

### Detailed Attribute Breakdown

#### 2.1 `Customer`
- **`PRIMARY_ID customer_id`** (STRING): Matches `customer_id` from `transactions.csv` (e.g. `C12382`).
- **`id`** (STRING): Redundant string identifier for projection.
- **`total_cards`** (INT): Count of distinct cards issued to customer (1, 2, or 3).

#### 2.2 `Card` (Account)
- **`PRIMARY_ID card_id`** (STRING): Matches card references in cases (e.g. `C12382-K1`, `C06403-K2`).
- **`card1`** (INT): Disguised payment card issuer bank code.
- **`card2`** (FLOAT): Issuer subsidiary code.
- **`card3`** (FLOAT): Card country code (e.g. 150.0, 185.0).
- **`card4`** (STRING): Card network brand (`visa`, `mastercard`, `american express`, `discover`).
- **`card5`** (FLOAT): Card tier/category code.
- **`card6`** (STRING): Account type (`credit`, `debit`).
- **`status`** (STRING): Lifecycle status (`active`, `monitored`, `blocked`).

#### 2.3 `Transaction`
- **`PRIMARY_ID txn_id`** (STRING): `TransactionID` from `transactions.csv` (e.g. `"3514030"`).
- **`ts`** (DATETIME): Real timestamp of authorization (July 2 – Dec 31, 2016).
- **`amount`** (FLOAT): Transaction amount in USD (`TransactionAmt`).
- **`product_cd`** (STRING): Product classification code (`W`, `C`, `H`, `R`, `S`).
- **`channel`** (STRING): Channel modality (`in_person` for `W`, `online` for all others).
- **`risk_score`** (FLOAT): Real-time machine learning fraud risk score (0.00 to 1.00).
- **`addr1`** (FLOAT): Anonymized cardholder billing region code.
- **`addr2`** (FLOAT): Billing country code (`87.0` indicates domestic home territory).
- **`dist1`, `dist2`** (FLOAT): Geometric/network distance metrics between transaction points.
- **`p_emaildomain`** (STRING): Purchaser's registered email domain.
- **`r_emaildomain`** (STRING): Merchant/recipient email domain.
- **`m_flags`** (STRING): Verification flags composite string (from `M1` through `M9`).

#### 2.4 `DeviceProfile`
- **`PRIMARY_ID device_hash`** (STRING): Unique composite key calculated as `DeviceInfo | id_30 | id_31 | id_33`.
- **`device_info`** (STRING): Hardware description string (e.g. `SAMSUNG SM-G892A Build/NRD90M`, `iOS Device`).
- **`device_type`** (STRING): Form factor (`mobile` or `desktop`).
- **`os`** (STRING): Operating system and build (`id_30`, e.g. `Android 7.0`, `iOS 11.1.2`, `Windows 10`).
- **`browser`** (STRING): Web browser client (`id_31`, e.g. `chrome 62.0`, `samsung browser 6.2`).
- **`screen_res`** (STRING): Screen display resolution (`id_33`, e.g. `2220x1080`, `1920x1080`).
- **`proxy_status`** (STRING): IP masking status (`id_23`, e.g. `anonymous`, `hidden`, `transparent`).
- **`device_status`** (STRING): Identity state (`id_15`: `New` vs `Found`).

#### 2.5 `BillingRegion`
- **`PRIMARY_ID region_id`** (STRING): Normalized identifier (e.g. `REG_444.0`, `REG_264.0`).
- **`region_code`** (FLOAT): Numeric code matching `addr1`.
- **`country_code`** (FLOAT): Numeric code matching `addr2`.

#### 2.6 `EmailDomain`
- **`PRIMARY_ID domain_name`** (STRING): Normalized domain name (e.g. `gmail.com`, `yahoo.com`, `anonymous.com`).
- **`name`** (STRING): Display string.
- **`is_disposable`** (BOOL): True for high-risk temporary email providers.

#### 2.7 `Case` (Case Memory & Dynamic Agent Record)
- **`PRIMARY_ID case_id`** (STRING): Case identifier (`CC-0001`–`CC-5565`, `HHG-001`–`HHG-020`, `CASE-2016-xxxx`).
- **`case_type`** (STRING): `historical` (first 4 months ground truth), `benchmark` (eval set), `agent_investigation`.
- **`status`** (STRING): `open`, `closed_fraud`, `closed_legitimate`, `escalated`.
- **`verdict`** (STRING): `fraud`, `legitimate`, `uncertain`.
- **`opened_at`** (DATETIME): Time alert created.
- **`closed_at`** (DATETIME): Time investigation concluded.
- **`fraud_probability`** (FLOAT): Calibrated probability assessment (0.00 to 1.00).
- **`exposure_usd`** (FLOAT): Cumulative dollar exposure of confirmed fraud episode.
- **`n_txns`** (INT): Count of transactions encompassed in episode.
- **`actions_taken`** (STRING): Pipe-delimited list of actions executed.
- **`report_filed`** (BOOL): Regulatory SAR filing flag.
- **`analyst_notes`** (STRING): Detailed case text narrative.
- **`summary`** (STRING): Condensed executive briefing.

#### 2.8 `FraudPattern` (Domain Knowledge Node)
- **`PRIMARY_ID pattern_id`** (STRING): Canonical typology code (`card_testing`, `card_not_present_fraud`, `card_not_present_new_device`, `out_of_region_use`, `account_takeover`, `threshold_structuring`, `shared_device_syndicate`, `undocumented`, `none`).
- **`name`** (STRING): Display name.
- **`description`** (STRING): Definitive structural pattern criteria.
- **`typical_indicators`** (STRING): Key graph signals (velocity, device reuse, region jump).

#### 2.9 `PolicyRule` (Governance Node)
- **`PRIMARY_ID rule_id`** (STRING): Canonical rule code (`R1` through `R10`).
- **`name`** (STRING): Rule title (e.g. `Verify Before Block`, `Card Testing Protocol`).
- **`description`** (STRING): Institutional policy statement.
- **`mandatory_actions`** (STRING): Required action string.
- **`default_approval_route`** (STRING): `auto`, `L1`, or `L2`.

---

## 3. Edge Definitions & Relational Semantics

```
                                    +----------------+
                                    |    Customer    |
                                    +----------------+
                                            |
                                            | OWNS (1:N)
                                            v
                                    +----------------+
                 +----------------- |      Card      | <-----------------+
                 |  CONNECTED_CARD  +----------------+                   |
                 |                          |                            | ON_CARD
                 |                          | MADE (1:N)                 |
                 v                          v                            |
+----------------+                   +----------------+                  |
|      Case      | -- INVOLVES_TXN ->|  Transaction   |                  |
+----------------+                   +----------------+                  |
   |     |                                  |   |   |                    |
   |     | EXHIBITS_PATTERN                 |   |   | FROM_DEVICE        |
   |     v                                  |   |   v                    |
   |  +--------------+                      |   |  +---------------+     |
   |  | FraudPattern |                      |   |  | DeviceProfile |     |
   |  +--------------+                      |   |  +---------------+     |
   |     |                                  |   |                        |
   |     | GOVERNED_BY_RULE                 |   | BILLED_IN              |
   |     v                                  |   v                        |
   |  +--------------+                      |  +---------------+         |
   +->|  PolicyRule  |<---------------------+  | BillingRegion |         |
      +--------------+      (CITES_RULE)       +---------------+         |
                                                |                        |
                                                | PURCHASER_EMAIL        |
                                                v                        |
                                               +---------------+         |
                                               |  EmailDomain  |         |
                                               +---------------+         |
                                                                         |
   (Transaction) --- NEXT_TRANSACTION (temporal link within card) -------> (Transaction)
```

### Edge Specifications

| Edge Name | Source Vertex | Target Vertex | Attributes | Directed | Semantics & Business Rule |
|---|---|---|---|---|---|
| **`OWNS`** | `Customer` | `Card` | `issued_ts DATETIME, is_primary BOOL` | Directed | Customer ownership of payment instrument. |
| **`MADE`** | `Card` | `Transaction` | `ts DATETIME` | Directed | Payment instrument utilized for authorization. |
| **`FROM_DEVICE`**| `Transaction` | `DeviceProfile` | `id_15_status STRING, id_23_proxy STRING, match_status STRING` | Directed | Identifies hardware/browser fingerprint used for online purchases. Absent for `in_person`. |
| **`BILLED_IN`** | `Transaction` | `BillingRegion` | `dist1 FLOAT` | Directed | Geographic association of authorization with billing postal/state area. |
| **`PURCHASER_EMAIL`** | `Transaction` | `EmailDomain` | None | Directed | Identifies purchaser email provider domain. |
| **`RECIPIENT_EMAIL`** | `Transaction` | `EmailDomain` | None | Directed | Identifies payee/recipient email provider domain. |
| **`NEXT_TRANSACTION`**| `Transaction`| `Transaction` | `delta_seconds INT, delta_amount FLOAT, same_region BOOL` | Directed | Chronological sequence link connecting adjacent transactions on same `Card`. Essential for card testing and velocity analysis. |
| **`INVOLVES_TXN`** | `Case` | `Transaction` | `is_first_fraud BOOL, is_flagged_trigger BOOL` | Directed | Encompasses all transactions verified as part of the fraud episode. |
| **`ON_CARD`** | `Case` | `Card` | None | Directed | Directly links case to the primary compromised card under investigation. |
| **`CONNECTED_CARD`** | `Case` | `Card` | `connection_reason STRING` | Directed | Links case to adjacent compromised cards sharing device fingerprints or customer credentials. |
| **`EXHIBITS_PATTERN`**| `Case` | `FraudPattern` | `confidence FLOAT` | Directed | Links case to confirmed fraud typology. |
| **`GOVERNED_BY_RULE`**| `FraudPattern`| `PolicyRule` | None | Directed | Maps fraud typologies directly to institutional governance rules. |
| **`CITES_RULE`** | `Case` | `PolicyRule` | `action STRING, approval_route STRING` | Directed | Records institutional policy justification for actions recommended in case. |

---

## 4. Primary IDs and Indexing Strategy

### 4.1 Primary Keys
- **Deterministic String Keys**: All entities use deterministic string keys (`customer_id`, `card_id`, `txn_id`, `case_id`, `rule_id`, `pattern_id`).
- **Composite Hashing for Device Profiles**: Device fingerprints lack an explicit unique ID in Vesta raw data. A normalized composite string is hashed:  
  `device_hash = MD5(CONCAT_WS("|", DeviceInfo, id_30, id_31, id_33))`  
  This ensures idempotent resolution across both `identity.csv` and case attachments.

### 4.2 Secondary Indexes
TigerGraph secondary indexes dramatically accelerate initial subgraph location prior to graph expansion:

| Vertex | Indexed Attribute | Rationale |
|---|---|---|
| `Transaction` | `ts` | Enables efficient temporal window queries ($\pm 48$ hours of alert). |
| `Transaction` | `risk_score` | Supports rapid filtering of high-risk transactions ($> 0.70$). |
| `Transaction` | `addr1` | Enables fast cluster extraction by geographic billing region. |
| `Card` | `card1` | Enables issuer-level compromise analysis across card series. |
| `DeviceProfile` | `device_type`, `os` | Filters hardware categories for forensic clustering. |
| `Case` | `status`, `pattern` | Rapid retrieval of historical case memory by typology. |

---

## 5. Loading Strategy & Preprocessing Pipeline

Because raw `transactions.csv` is ~708 MB with 590,742 rows and 397 columns, an optimized staging and loading strategy is applied:

```
[ dataset/raw/ ]
  ├── transactions.csv (708MB)
  ├── identity.csv (26.7MB)
  ├── closed_cases_history.csv (2.7MB)
  └── case_pack.csv (3.5KB)
           │
           ▼  Python Preprocessing & Validation (HHGOA-Fraud-Agent/dataset/processed/)
  ├── processed_customers.csv
  ├── processed_cards.csv
  ├── processed_transactions.csv
  ├── processed_devices.csv
  ├── processed_cases.csv
  └── processed_edges_next_txn.csv
           │
           ▼  TigerGraph GSQL Loading Jobs (HHGOA-Fraud-Agent/tigergraph/load_data.gsql)
  [ TigerGraph Distributed Graph Store ]
```

### Preprocessing Steps:
1. **Card Entity Extraction (`processed_cards.csv`):**
   - In `transactions.csv`, group by `customer_id` and unique tuple `(card1, card2, card3, card4, card5, card6)`.
   - Assign chronological suffixes `K1`, `K2`, `K3` based on earliest transaction timestamp `ts`.
   - Verified 100% consistent with `case_pack.csv` and `closed_cases_history.csv` naming conventions.
2. **Device Normalization (`processed_devices.csv`):**
   - Clean and trim `DeviceInfo`, `id_30`, `id_31`, `id_33`.
   - Generate canonical `device_hash`.
3. **Temporal Sequence Edge Generation (`processed_edges_next_txn.csv`):**
   - Sort transactions per `card_id` by `ts`.
   - Calculate `delta_seconds` and `delta_amount` between consecutive records $T_i \rightarrow T_{i+1}$.
4. **Case Normalization (`processed_cases.csv`):**
   - Parse pipe-separated `txn_ids` and `connected_card_ids` into relational vertex and edge load files.
   - Load static knowledge nodes: `FraudPattern` and `PolicyRule` (R1–R10).

---

## 6. Required Graph Queries for Agent Investigation

The agent requires specialized GSQL queries mapped to the 5 known fraud typologies and 2 undocumented patterns:

### 6.1 `card_window_query` (Typology 1: Card Testing & Typology 2: CNP Burst)
- **Input:** `card_id STRING`, `center_ts DATETIME`, `window_hours INT`
- **Logic:** Traverses `Card ──MADE──► Transaction` where `ts` is within $[center\_ts - window\_hours, center\_ts + window\_hours]$.
- **Pattern Detection:**
  - Identifies $\ge 3$ consecutive micro-authorizations ($< \$5.00$) followed by a major purchase ($> \$100.00$) within 1 hour (Card Testing).
  - Identifies 2–4 high-value online purchases within 48 hours with no prior card history (CNP Burst).

### 6.2 `device_neighbors_query` (Typology 3: CNP New Device & Shared Syndicate)
- **Input:** `txn_id STRING`
- **Logic:**
  1. Starts at `Transaction(txn_id)`.
  2. Traverses `──FROM_DEVICE──► DeviceProfile`.
  3. Traverses reverse `◄──FROM_DEVICE── Transaction ◄──MADE── Card ◄──OWNS── Customer`.
  4. Also traverses `DeviceProfile ◄──FROM_DEVICE── Transaction ◄──INVOLVES_TXN── Case`.
- **Pattern Detection:**
  - Returns count of distinct cards and customers sharing this identical hardware/proxy fingerprint.
  - Detects if device was flagged in prior closed cases (e.g. `CC-2649` syndicate).

### 6.3 `region_anomaly_query` (Typology 4: Out-of-Region Use)
- **Input:** `txn_id STRING`, `card_id STRING`
- **Logic:**
  1. Retrieves `addr1` and `addr2` for target transaction.
  2. Compares against the cardholder's 90-day historical distribution of `addr1` across all card-present (`channel == 'in_person'`) transactions.
- **Pattern Detection:**
  - Identifies isolated transactions in a foreign region occurring within hours of domestic transactions (Card Cloning).
  - Distinguishes from multi-day consecutive activity in a single foreign region (Legitimate Travel).

### 6.4 `account_takeover_subgraph` (Typology 5: Account Takeover)
- **Input:** `customer_id STRING`
- **Logic:**
  1. Traverses `Customer ──OWNS──► Card ──MADE──► Transaction`.
  2. Gathers device status (`id_15 == 'New'`), proxy anomalies (`id_23`), match flag failures (`M1`–`M9`), and concurrent multi-channel usage (`in_person` and `online`).
- **Pattern Detection:**
  - Identifies simultaneous credential and multi-card compromise triggering Rule R10 (`BLOCK_ALL_CARDS`).

### 6.5 `similar_closed_cases_query` (GraphRAG Case Memory)
- **Input:** `pattern_name STRING`, `device_hash STRING`, `card_id STRING`, `exposure_target FLOAT`
- **Logic:**
  1. Retrieves closed cases matching the pattern, connected device, or similar exposure bucket.
  2. Returns case IDs (`CC-xxxx`), analyst narratives, actions taken, and SAR filing status (`report_filed`).
- **Agent Utility:** Grounds LLM generation with verbatim past case precedents to populate `similar_prior_cases` and justify `next_best_actions`.

---

## 7. GSQL Schema Definition Script

The production GSQL schema is defined below and implemented in `tigergraph/schema.gsql`:

```gsql
CREATE GRAPH FraudInvestigationGraph()

USE GRAPH FraudInvestigationGraph

# -------------------------------------------------------------
# VERTICES
# -------------------------------------------------------------
CREATE VERTEX Customer (
    PRIMARY_ID customer_id STRING,
    id STRING,
    total_cards INT
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX Card (
    PRIMARY_ID card_id STRING,
    id STRING,
    card1 INT,
    card2 FLOAT,
    card3 FLOAT,
    card4 STRING,
    card5 FLOAT,
    card6 STRING,
    status STRING
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX Transaction (
    PRIMARY_ID txn_id STRING,
    id STRING,
    ts DATETIME,
    amount FLOAT,
    product_cd STRING,
    channel STRING,
    risk_score FLOAT,
    addr1 FLOAT,
    addr2 FLOAT,
    dist1 FLOAT,
    dist2 FLOAT,
    p_emaildomain STRING,
    r_emaildomain STRING,
    m_flags STRING
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX DeviceProfile (
    PRIMARY_ID device_hash STRING,
    device_info STRING,
    device_type STRING,
    os STRING,
    browser STRING,
    screen_res STRING,
    proxy_status STRING,
    device_status STRING
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX BillingRegion (
    PRIMARY_ID region_id STRING,
    region_code FLOAT,
    country_code FLOAT
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX EmailDomain (
    PRIMARY_ID domain_name STRING,
    name STRING,
    is_disposable BOOL
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX Case (
    PRIMARY_ID case_id STRING,
    case_type STRING,
    status STRING,
    verdict STRING,
    opened_at DATETIME,
    closed_at DATETIME,
    fraud_probability FLOAT,
    exposure_usd FLOAT,
    n_txns INT,
    actions_taken STRING,
    report_filed BOOL,
    analyst_notes STRING,
    summary STRING
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX FraudPattern (
    PRIMARY_ID pattern_id STRING,
    name STRING,
    description STRING,
    typical_indicators STRING
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

CREATE VERTEX PolicyRule (
    PRIMARY_ID rule_id STRING,
    name STRING,
    description STRING,
    mandatory_actions STRING,
    default_approval_route STRING
) WITH STATS="OUTDEGREE_BY_EDGETYPE";

# -------------------------------------------------------------
# EDGES
# -------------------------------------------------------------
CREATE DIRECTED EDGE OWNS (FROM Customer, TO Card, issued_ts DATETIME, is_primary BOOL) WITH REVERSE_EDGE="OWNED_BY";
CREATE DIRECTED EDGE MADE (FROM Card, TO Transaction, ts DATETIME) WITH REVERSE_EDGE="MADE_BY";
CREATE DIRECTED EDGE FROM_DEVICE (FROM Transaction, TO DeviceProfile, id_15_status STRING, id_23_proxy STRING, match_status STRING) WITH REVERSE_EDGE="DEVICE_USED_IN";
CREATE DIRECTED EDGE BILLED_IN (FROM Transaction, TO BillingRegion, dist1 FLOAT) WITH REVERSE_EDGE="HAS_TRANSACTION";
CREATE DIRECTED EDGE PURCHASER_EMAIL (FROM Transaction, TO EmailDomain) WITH REVERSE_EDGE="PURCHASER_FOR";
CREATE DIRECTED EDGE RECIPIENT_EMAIL (FROM Transaction, TO EmailDomain) WITH REVERSE_EDGE="RECIPIENT_FOR";
CREATE DIRECTED EDGE NEXT_TRANSACTION (FROM Transaction, TO Transaction, delta_seconds INT, delta_amount FLOAT, same_region BOOL);
CREATE DIRECTED EDGE INVOLVES_TXN (FROM Case, TO Transaction, is_first_fraud BOOL, is_flagged_trigger BOOL) WITH REVERSE_EDGE="INVOLVED_IN_CASE";
CREATE DIRECTED EDGE ON_CARD (FROM Case, TO Card) WITH REVERSE_EDGE="TARGETED_IN_CASE";
CREATE DIRECTED EDGE CONNECTED_CARD (FROM Case, TO Card, connection_reason STRING) WITH REVERSE_EDGE="CONNECTED_TO_CASE";
CREATE DIRECTED EDGE EXHIBITS_PATTERN (FROM Case, TO FraudPattern, confidence FLOAT) WITH REVERSE_EDGE="SEEN_IN_CASE";
CREATE DIRECTED EDGE GOVERNED_BY_RULE (FROM FraudPattern, TO PolicyRule);
CREATE DIRECTED EDGE CITES_RULE (FROM Case, TO PolicyRule, action STRING, approval_route STRING) WITH REVERSE_EDGE="CITED_BY_CASE";
```

---

## 8. Summary of Alignment with Hackathon Requirements

1. **Strictly Grounded**: Only incorporates entities and relations supported by the raw dataset and domain task.
2. **Dual Case Support**: Integrates ground-truth labeled history (`closed_cases_history.csv`) and dynamic case progression.
3. **GraphRAG-Ready**: Embeds institutional fraud policies (R1–R10) and typologies directly into graph vertices for combined graph-and-vector retrieval.
4. **Autonomous & Governed**: Direct mapping between graph evidence, policy rules, and required approval routing (`auto`, `L1`, `L2`).
