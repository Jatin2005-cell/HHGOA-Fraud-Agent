# HHGOA_IEEE TigerGraph Agentic Fraud Investigation — Complete Dataset Analysis

**Document Status:** Complete Dataset Inspection & Structural Specification  
**Version:** 1.0.0  
**Target Repository:** `HHGOA-Fraud-Agent`  
**Dataset Origin:** IEEE-CIS Fraud Detection (Vesta Corporation) augmented by TigerGraph for Hacker House Goa 2026.

---

## 1. Executive Summary & File Inventory

The dataset comprises **5 core files** located in `dataset/raw/`, providing 6 months of real-world card transaction and identity data, historical labeled fraud cases, and 20 evaluation benchmark cases. Every original IEEE-CIS/Vesta column has been preserved, with no synthetic alteration of core features, but with yes/no labels replaced by real-time model risk scores and enriched with temporal, customer, and case tracking fields.

| File Name | File Size | Row Count | Column Count | Description & Purpose |
|---|---|---|---|---|
| `README.md` | 38.7 KB | 473 lines | N/A | Ground-truth hackathon manual, domain glossary, fraud policies (R1–R10), approval routing rules, benchmark evaluation rubric, 20 benchmark case prompts, and output schema specifications. |
| `transactions.csv` | 707.9 MB | 590,742 | 397 | 6 months of card transactions (July 2, 2016 – December 31, 2016). Includes all 393 original Vesta columns + 4 added bank production columns (`customer_id`, `ts`, `channel`, `risk_score`). |
| `identity.csv` | 26.7 MB | 144,432 | 41 | Device, browser, network, OS, proxy, and hardware telemetry for online transactions. Joins 1:1 on `TransactionID` with transactions where `channel == 'online'`. |
| `closed_cases_history.csv` | 2.7 MB | 5,565 | 15 | Finished investigations from months 1–4 (July to October 2016). 4,665 confirmed fraud cases, 900 cleared false alarms. Serves as ground-truth memory and few-shot vector context. |
| `case_pack.csv` | 3.5 KB | 20 | 8 | The 20 benchmark evaluation alerts from months 5–6 (November and December 2016). The agent is evaluated on investigating these cases. |

---

## 2. File-by-File Detailed Explanation

### 2.1 `transactions.csv`
- **Volume:** 590,742 transactions spanning 182 days (2016-07-02 00:02:21 to 2016-12-31 23:59:33).
- **Customers & Cards:** Approximately 13,500 distinct customers (`customer_id`) making purchases across debit/credit card accounts.
- **Amounts:** Amounts in USD (`TransactionAmt`), ranging from micropayments ($0.25) to major purchases ($5,000+).
- **Anonymized Model Scores:** Replaces binary `isFraud` with `risk_score` (continuous 0.0 to 1.0). High risk score (e.g. >0.70) is an alert signal, not a fraud verdict.
- **Product Codes:**
  - `W`: In-person transactions (Card-Present). No `identity.csv` record. Marked with `channel = 'in_person'`.
  - `C`, `H`, `R`, `S`: Online / Card-Not-Present transactions. Accompanied by device identity records in `identity.csv`. Marked with `channel = 'online'`.

### 2.2 `identity.csv`
- **Volume:** 144,432 identity records, exclusively for online transactions (`channel == 'online'`).
- **Device & Environment Signals:**
  - Operating system (`id_30`), browser and version (`id_31`), screen resolution (`id_33`), screen color depth (`id_32`).
  - Device type (`DeviceType`: `'mobile'` vs `'desktop'`).
  - Device manufacturer and build string (`DeviceInfo`, e.g. `'SAMSUNG SM-G892A Build/NRD90M'`, `'iOS Device'`, `'Trident/7.0'`).
  - Device age status (`id_15`: `'New'` vs `'Found'`).
  - Network and proxy status (`id_23`: `'transparent'`, `'anonymous'`, `'hidden'`).
  - Model match indicators (`id_34`: `'match_status:1'`, `'match_status:2'`).
  - Encoded risk indicators (`id_01` to `id_11`: IP domain ratings, page dwell time, login counts).

### 2.3 `closed_cases_history.csv`
- **Volume:** 5,565 closed cases spanning 2016-07-02 to 2016-11-02.
- **Historical Ground Truth:**
  - `outcome`: 4,665 `confirmed_fraud`, 900 `cleared`.
  - `pattern`:
    - `card_not_present_fraud`: 1,404 cases
    - `account_takeover`: 1,205 cases
    - `card_not_present_new_device`: 1,076 cases
    - `out_of_region_use`: 955 cases
    - `none`: 900 cases (cleared / false alarms)
    - `card_testing`: 16 cases
    - `undocumented`: 9 cases
- **Multi-Card Connections:** 397 cases resulted in regulatory filings (`report_filed == 'Yes'`), often linking multiple cards (`connected_card_ids`) compromised by the same device or actor.
- **Case Memory Utility:** Acts as the knowledge repository for GraphRAG and vector retrieval to identify similar historical typologies, investigator notes, and precedent actions.

### 2.4 `case_pack.csv`
- **Volume:** Exactly 20 cases (`HHG-001` through `HHG-020`) dated between 2016-11-12 and 2016-12-29.
- **Trigger Types:**
  - `risk_score` (11 cases): Initiated by high real-time machine learning score on a transaction.
  - `customer_report` (8 cases): Initiated by customer contacting the bank disputing an unauthorized charge.
  - `analyst_request` (1 case: `HHG-014`): Initiated by a fraud analyst noticing a device fingerprint cluster across multiple cards.
- **Customer Overlap:** 16 of the 20 benchmark cases involve customers who already have prior case histories in `closed_cases_history.csv`, making case memory retrieval directly applicable.

### 2.5 `README.md`
- Contains complete regulatory and institutional guidelines:
  - Regulatory links: FinCEN (SAR Narrative Guidance, Account Takeover Advisories), FATF, FFIEC, and OFAC.
  - Bank Fraud Policy Rules (R1 through R10).
  - Explicit three-part JSON schema required for each case evaluation.

---

## 3. Complete Column Inventory

### 3.1 `transactions.csv` (397 Columns)

| Group Name | Column Names | Count | Data Type | Semantics & Usage |
|---|---|---|---|---|
| **Core Identifiers & Temporal** | `TransactionID`<br>`customer_id`<br>`TransactionDT`<br>`ts` | 4 | Integer<br>String<br>Integer<br>DateTime String | `TransactionID`: Unique primary identifier for transaction.<br>`customer_id`: Bank customer entity ID (e.g. `C06075`).<br>`TransactionDT`: Timedelta in seconds from start.<br>`ts`: Real timestamp `YYYY-MM-DD HH:MM:SS`. |
| **Transaction Metrics & Channel** | `TransactionAmt`<br>`ProductCD`<br>`channel`<br>`risk_score` | 4 | Float<br>String<br>String<br>Float | `TransactionAmt`: Purchase amount in USD.<br>`ProductCD`: `W` (in-person) or `C, H, R, S` (online).<br>`channel`: Derived channel (`in_person` or `online`).<br>`risk_score`: Model score (0.0 to 1.0). High score is trigger, not verdict. |
| **Card Attributes** | `card1` to `card6` | 6 | Integer/Float/String | `card1`: Issuer code/hash.<br>`card2`, `card3`, `card5`: Issuer metadata.<br>`card4`: Card brand network (`visa`, `mastercard`, `american express`, `discover`).<br>`card6`: Card type (`credit`, `debit`). |
| **Location & Distance** | `addr1`, `addr2`<br>`dist1`, `dist2` | 4 | Float | `addr1`: Anonymized billing region.<br>`addr2`: Billing country code (`87` = domestic).<br>`dist1`, `dist2`: Physical/network distance between transaction points. |
| **Email Domains** | `P_emaildomain`<br>`R_emaildomain` | 2 | String | `P_emaildomain`: Purchaser email domain (e.g. `gmail.com`, `anonymous.com`).<br>`R_emaildomain`: Recipient/merchant email domain. |
| **Transaction Counts** | `C1` to `C14` | 14 | Float | Engineered counts (e.g. number of addresses, phones, or attempts linked to card). |
| **Time Deltas** | `D1` to `D15` | 15 | Float | Time deltas in days (e.g. days since prior transaction, days since card issuance). |
| **Match Indicators** | `M1` to `M9` | 9 | String (`T`, `F`, or null) | Verification matches (e.g. cardholder name matching billing address, shipping match). |
| **Vesta Feature Space** | `V1` to `V339` | 339 | Float | Engineered behavioral, entity-linking, and risk ranking signals provided by Vesta. |

### 3.2 `identity.csv` (41 Columns)

| Group Name | Column Names | Count | Data Type | Semantics & Usage |
|---|---|---|---|---|
| **Join Key** | `TransactionID` | 1 | Integer | Primary foreign key matching `transactions.csv:TransactionID`. |
| **Encoded Ratings & Metrics** | `id_01` to `id_11` | 11 | Float | Encoded numerical scores: IP rating, dwell time on page, login velocity, device rating. |
| **Identity & Risk Flags** | `id_12` to `id_29` | 18 | String/Float | Categorical verification indicators.<br>`id_12`: `Found`/`NotFound`.<br>`id_15`: Device status (`New` vs `Found`).<br>`id_16`: Verification flag.<br>`id_23`: Proxy status (`transparent`, `anonymous`, `hidden`).<br>`id_28`, `id_29`: Account identity status. |
| **Client Environment** | `id_30`<br>`id_31`<br>`id_32`<br>`id_33`<br>`id_34` | 5 | String/Float | `id_30`: OS family and version (e.g. `Android 7.0`, `iOS 11.1.2`, `Windows 10`).<br>`id_31`: Browser client (e.g. `chrome 62.0`, `samsung browser 6.2`).<br>`id_32`: Screen bit depth (e.g. `32.0`).<br>`id_33`: Screen resolution (e.g. `2220x1080`, `1920x1080`).<br>`id_34`: Match status string (e.g. `match_status:1`, `match_status:2`). |
| **Additional Flags** | `id_35` to `id_38` | 4 | String (`T` / `F`) | Environmental consistency and verification flags. |
| **Hardware Profile** | `DeviceType`<br>`DeviceInfo` | 2 | String | `DeviceType`: `mobile` or `desktop`.<br>`DeviceInfo`: Device model name/fingerprint string (e.g. `SAMSUNG SM-G892A Build/NRD90M`, `iOS Device`, `Trident/7.0`, `Windows`). |

### 3.3 `closed_cases_history.csv` (15 Columns)

| Column Name | Data Type | Description & Value Domain |
|---|---|---|
| `case_id` | String | Unique identifier for historical case (`CC-0001` through `CC-5565`). |
| `customer_id` | String | Customer involved (`C00001` to `C13500`). |
| `card_id` | String | Specific card account involved (e.g. `C00259-K1`, `C06403-K2`). |
| `opened_at` | DateTime | Timestamp when investigation opened (`2016-07-02` to `2016-11-02`). |
| `closed_at` | DateTime | Timestamp when investigation was closed. |
| `outcome` | String | Ground-truth outcome: `confirmed_fraud` (4,665) or `cleared` (900). |
| `pattern` | String | Typology: `card_not_present_fraud`, `account_takeover`, `card_not_present_new_device`, `out_of_region_use`, `card_testing`, `undocumented`, `none`. |
| `first_fraud_txn_id` | String / Null | The transaction where the fraud began. Null for cleared cases. |
| `txn_ids` | String | Pipe-separated list of transaction IDs included in the case episode. |
| `n_txns` | Integer | Total count of transactions involved in the case episode. |
| `exposure_usd` | Float | Sum of amounts involved in confirmed fraud ($0.00 for cleared cases). |
| `connected_card_ids` | String / Null | Pipe-separated list of other customer cards compromised in the same incident. |
| `actions_taken` | String | Pipe-separated institutional actions taken (e.g. `CREATE_CASE\|BLOCK_CARD`). |
| `report_filed` | String | `Yes` (397 cases) or `No` (5,168 cases). Regulatory SAR filing indicator. |
| `analyst_notes` | Text | Human investigator's detailed case narrative explaining evidence, reasoning, and resolution. |

### 3.4 `case_pack.csv` (8 Columns)

| Column Name | Data Type | Description |
|---|---|---|
| `case_id` | String | Benchmark case identifier (`HHG-001` through `HHG-020`). |
| `opened_at` | DateTime | Timestamp when alert was generated (`2016-11-12` to `2016-12-29`). |
| `trigger_type` | String | Trigger cause: `risk_score` (11), `customer_report` (8), `analyst_request` (1). |
| `trigger_text` | String | Textual description of alert trigger reason. |
| `flagged_txn_id` | Integer | The transaction ID where the alert fired. |
| `card_id` | String | Card account identifier (e.g. `C12382-K1`). |
| `customer_id` | String | Customer account identifier (e.g. `C12382`). |
| `risk_score` | Float / Null | Model risk score (populated if `trigger_type == 'risk_score'`). |

---

## 4. Key Relationships & Entity Modeling

```
+----------------+        OWNS         +------------+        MADE         +-----------------+
|    Customer    | ----------------->  |    Card    | ----------------->  |   Transaction   |
| (customer_id)  | 1                 * |  (card_id) | 1                 * | (TransactionID) |
+----------------+                     +------------+                     +-----------------+
                                             |                                   |        |
                                             |                                   |        |
                                     CONNECTED_TO /                              |        | BILLED_IN
                                        ON_CARD                                  |        v
                                             |                      FROM_DEVICE  |  +----------------+
                                             v                                   |  | BillingRegion  |
                                    +-----------------+                          |  |    (addr1)     |
                                    |   Case / CC     | <------------------------+  +----------------+
                                    |    (case_id)    |         INVOLVES                 |
                                    +-----------------+                                  |
                                             |                                           v
                                             |                                  +-----------------+
                                             | PURCHASER_EMAIL                  |  DeviceProfile  |
                                             v                                  | (DeviceProfile) |
                                    +-----------------+                         +-----------------+
                                    |   EmailDomain   |
                                    | (P_emaildomain) |
                                    +-----------------+
```

### 4.1 Primary Identifiers
- **Customer:** `customer_id` (e.g. `C12382`)
- **Card:** `card_id` (e.g. `C12382-K1`). Each customer may possess 1, 2, or 3 cards (`K1`, `K2`, `K3`), corresponding to distinct `(card1, card2, card3, card4, card5, card6)` attribute profiles.
- **Transaction:** `TransactionID` (integer, e.g. `3514030`)
- **Identity Record:** `TransactionID` (1:1 join key to online transactions)
- **Device Profile:** Synthetic composite key formed by:  
  `DeviceInfo | id_30 (OS) | id_31 (Browser) | id_33 (Screen Resolution)`  
  *(Example: `SAMSUNG SM-G892A Build/NRD90M | Android 7.0 | samsung browser 6.2 | 2220x1080`)*
- **Billing Region:** `addr1` (numeric region code, e.g. `444.0`, `264.0`)
- **Email Domain:** `P_emaildomain` / `R_emaildomain` (e.g. `gmail.com`, `anonymous.com`)
- **Case:** `case_id` (e.g. `CC-0001` for historical, `HHG-001` for benchmark, `CASE-2016-xxxx` for dynamic agent-created cases)

### 4.2 Relational Cardinality
1. **Customer to Card:** `1-to-Many` (`Customer` owns 1 to 3 `Card` instances).
2. **Card to Transaction:** `1-to-Many` (`Card` makes many transactions over time).
3. **Transaction to Identity:** `0-to-1` (Exactly 1 identity record for `online` transactions; 0 for `in_person` transactions).
4. **Transaction to DeviceProfile:** `Many-to-1` (Multiple online transactions share the same hardware/client profile).
5. **Transaction to BillingRegion:** `Many-to-1` (`addr1` links transactions geolocatively).
6. **Transaction to EmailDomain:** `Many-to-1` (`P_emaildomain` links purchaser email domains).
7. **Transaction to Transaction (Temporal Sequence):** `Next-in-time` sequence ordered by `ts` within each `card_id` and within each `customer_id`.
8. **Case to Transaction:** `1-to-Many` (`ClosedCase` or `Case` involves `txn_ids`).
9. **Case to Card:** `1-to-Many` (`ClosedCase` is associated with `card_id` and may connect to `connected_card_ids`).

---

## 5. Fraud Typology Analysis

The dataset features **5 documented patterns** and **2 undocumented patterns** discovered via closed case analysis:

### Documented Patterns:
1. **`card_testing` (16 historical cases):**
   - **Pattern:** 3 or more rapid, low-value online authorizations (<$5.00) within an hour, followed by a significantly larger purchase ($100–$500+).
   - **Policy Action:** R5: Recommend `DECLINE_TRANSACTION` and `STEP_UP_AUTH`. If a purchase >$100 has cleared, recommend `BLOCK_CARD`.
2. **`card_not_present_fraud` (1,404 historical cases):**
   - **Pattern:** Online transactions without physical card presentation, featuring abnormal amounts or merchants divergent from customer baseline, typically in bursts of 2–4 within 48 hours.
   - **Policy Action:** R1–R4: If single signal / prob < 0.70, verify with customer first. If customer denies, block card and open case.
3. **`card_not_present_new_device` (1,076 historical cases):**
   - **Pattern:** Online CNP transaction originating from a device where `id_15 == 'New'`, frequently coupled with proxy usage (`id_23 in ['anonymous', 'hidden']`).
   - **Policy Action:** Stronger suspicion than pattern 2, but requires verification since legitimate customers acquire new devices.
4. **`out_of_region_use` (955 historical cases):**
   - **Pattern:** In-person (`channel == 'in_person'`) purchases in an unfamiliar billing region (`addr1`), occurring concurrently with normal transactions in the customer's home region.
   - **Policy Action:** Distinguish between card cloning (simultaneous activity in two distant regions) and customer travel (consecutive purchases in one new region over days).
5. **`account_takeover` (1,205 historical cases):**
   - **Pattern:** Mixed-channel activity with severe device, credential, and match flag anomalies (`M1`–`M9`, `id_34`), indicating compromised login credentials rather than a stolen card number alone.
   - **Policy Action:** R10: If credentials or multiple cards are compromised, recommend `BLOCK_ALL_CARDS`.

### Undocumented Patterns in Dataset:
6. **Shared Device Multi-Card Syndicate (`undocumented`):**
   - *Cases CC-2649, CC-2971, CC-2985, CC-3035*: Same hardware profile (`Samsung SM-G935F on Chrome for Android behind anonymous proxy`) used across distinct customer accounts within a narrow time window.
   - **Policy Action:** R6 & R9: File SAR (`FILE_REPORT`), `CREATE_CASE`, and place all connected cards under `MONITOR_CONNECTED_CARDS`.
7. **Threshold Avoidance / Structuring (`undocumented`):**
   - *Cases CC-3748, CC-3841, CC-3907, CC-4086, CC-4124*: Exactly 4 online purchases within 40 minutes, each calibrated just under the $500 threshold (e.g. $470–$490) totaling ~$1,900.
   - **Policy Action:** R8 & R9: High exposure >$1,000, systematic evasion. File SAR (`FILE_REPORT`), `CREATE_CASE`, `ESCALATE_TO_ANALYST`.

---

## 6. Institutional Fraud Policy & Approval Routing (R1–R10)

### 6.1 Policy Rules Matrix

| Rule | Trigger Condition | Mandatory Institutional Actions | Approval Route |
|---|---|---|---|
| **R1** | Single signal or weak signal with fraud probability < 0.70 | `VERIFY_WITH_CUSTOMER` or `STEP_UP_AUTH` before any blocking | `auto` |
| **R2** | Customer denies transaction | `BLOCK_CARD` and `CREATE_CASE`. If exposure > $1,000 or linked to shared device, add `FILE_REPORT` | `L1` (if ≤ $2.5k) / `L2` (if > $2.5k) for Block; `L2` for Report; `auto` for Case |
| **R3** | Customer confirms transaction | `CLOSE_NO_FRAUD` | `auto` |
| **R4** | No customer reply within 24 hours | `MONITOR_CARD`, `DECLINE_TRANSACTION` for pending authorizations. Escalate if exposure > $500 | `auto` / `L1` |
| **R5** | Card testing sequence (≥3 tiny online txns + large purchase) | `DECLINE_TRANSACTION` and `STEP_UP_AUTH`. If purchase > $100 has already cleared, `BLOCK_CARD` | `L1` |
| **R6** | Shared origin (multiple cards share device profile, region, or recipient email) | `CREATE_CASE`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS` | `auto` (Case, Monitor) / `L2` (Report) |
| **R7** | Customer disputes recurring charge matching historical pattern | `CREATE_CASE`, `VERIFY_WITH_CUSTOMER`, `WARN_CUSTOMER` (Do not block) | `auto` |
| **R8** | Uncertain verdict and exposure > $500, or conflicting evidence | `ESCALATE_TO_ANALYST` | `auto` |
| **R9** | Coordinated abuse fitting no documented pattern | `CREATE_CASE`, `FILE_REPORT`, `ESCALATE_TO_ANALYST` (describe in own words) | `auto` / `L2` |
| **R10** | Multiple cards compromised or credentials compromised | `BLOCK_ALL_CARDS` (Never use unless ≥2 cards confirmed fraud or credentials breached) | `L2` |

### 6.2 Approval Authority Levels
- **`auto` (Agent Execution):** Actions the AI agent may execute autonomously without human sign-off (`ALLOW_TRANSACTION`, `MONITOR_CARD`, `MONITOR_CONNECTED_CARDS`, `WARN_CUSTOMER`, `VERIFY_WITH_CUSTOMER`, `STEP_UP_AUTH`, `GENERATE_REPORT`, `CREATE_CASE`, `ESCALATE_TO_ANALYST`, `CLOSE_NO_FRAUD`).
- **`L1` (Team Lead Approval):** Required for `DECLINE_TRANSACTION`, and `BLOCK_CARD` when total exposure ≤ $2,500.
- **`L2` (Fraud Manager Approval):** Required for `BLOCK_CARD` when exposure > $2,500, `BLOCK_ALL_CARDS` under all circumstances, and any regulatory `FILE_REPORT` (SAR).

---

## 7. Required Benchmark Output Specification

For each of the 20 cases (`HHG-001` through `HHG-020`), the agent must generate a strictly conforming JSON file named `cases/<case_id>.json`. The output has three distinct core parts:

```json
{
  "case_id": "HHG-xxx",
  "case": {
    "status": "open | closed_fraud | closed_legitimate | escalated",
    "verdict": "fraud | legitimate | uncertain",
    "fraud_probability": 0.00,
    "pattern": "card_testing | card_not_present_fraud | card_not_present_new_device | out_of_region_use | account_takeover | undocumented | none",
    "pattern_description": "",
    "affected_txn_ids": ["..."],
    "first_suspicious_txn_id": "...",
    "connected_card_ids": ["..."],
    "connected_device_profiles": ["..."],
    "exposure_usd": 0.00,
    "evidence": [
      {
        "claim": "...",
        "source": "graph | document | customer | external",
        "ref": "...",
        "entity_ids": ["..."]
      }
    ],
    "similar_prior_cases": ["CC-xxxx"],
    "summary": "...",
    "written_to_graph": true,
    "graph_case_id": "CASE-2016-xxxx"
  },
  "evidence_requests": [
    {
      "type": "customer_validation | step_up_auth | analyst_info",
      "asked_after_step": 1,
      "assumed_response": "..."
    }
  ],
  "next_best_actions": {
    "initial": [
      {
        "action": "...",
        "route": "auto | L1 | L2",
        "reason": "..."
      }
    ],
    "final": [
      {
        "action": "...",
        "route": "auto | L1 | L2",
        "reason": "..."
      }
    ],
    "what_changed": "..."
  },
  "sar": {
    "file": false,
    "reason": "...",
    "narrative": "",
    "subjects": [],
    "total_amount_usd": 0.0,
    "activity_dates": []
  },
  "stop_reason": "...",
  "tool_calls": 0,
  "tokens": 0,
  "latency_s": 0.0
}
```

---

## 8. TigerGraph Graph Schema Specification

To empower the agent with deep multi-hop graph queries and graph algorithms (PageRank, Louvain Community Detection, Weakly Connected Components for fraud rings), the dataset maps into the following TigerGraph schema:

### 8.1 Vertex Types

| Vertex Type | Primary ID (Key) | Attributes | Description & Source |
|---|---|---|---|
| **`Customer`** | `customer_id` (STRING) | `id STRING` | Bank customer account entity (`transactions.csv:customer_id`). |
| **`Card`** | `card_id` (STRING) | `id STRING, card1 INT, card2 FLOAT, card3 FLOAT, card4 STRING, card5 FLOAT, card6 STRING` | Physical/virtual card account (`closed_cases_history.csv:card_id`, derived in transactions). |
| **`Transaction`** | `TransactionID` (STRING) | `id STRING, ts DATETIME, amount FLOAT, channel STRING, product_cd STRING, risk_score FLOAT, addr1 FLOAT, addr2 FLOAT, dist1 FLOAT, dist2 FLOAT, P_emaildomain STRING, R_emaildomain STRING` | Individual transaction event (`transactions.csv`). |
| **`DeviceProfile`** | `device_hash` (STRING) | `device_info STRING, device_type STRING, os STRING, browser STRING, screen STRING, proxy_status STRING, device_status STRING` | Hardware and client fingerprint (`identity.csv`). |
| **`BillingRegion`** | `region_id` (STRING) | `region_code FLOAT, country_code FLOAT` | Geolocative billing region (`transactions.csv:addr1, addr2`). |
| **`EmailDomain`** | `domain_name` (STRING) | `name STRING` | Email domain entity (`transactions.csv:P_emaildomain, R_emaildomain`). |
| **`ClosedCase`** | `case_id` (STRING) | `customer_id STRING, card_id STRING, opened_at DATETIME, closed_at DATETIME, outcome STRING, pattern STRING, exposure_usd FLOAT, report_filed STRING, analyst_notes STRING` | Ground-truth historical case record (`closed_cases_history.csv`). |
| **`DynamicCase`** | `case_id` (STRING) | `opened_at DATETIME, verdict STRING, fraud_prob FLOAT, pattern STRING, exposure_usd FLOAT, sar_filed BOOL, summary STRING` | Newly opened/progressed cases written dynamically by the agent. |

### 8.2 Edge Types

| Edge Type | Source Vertex | Target Vertex | Attributes | Semantics |
|---|---|---|---|---|
| **`OWNS`** | `Customer` | `Card` | `is_primary BOOL` | Customer ownership of card account. |
| **`MADE`** | `Card` | `Transaction` | `ts DATETIME` | Card used to execute transaction. |
| **`FROM_DEVICE`** | `Transaction` | `DeviceProfile` | `match_status STRING` | Online transaction originating from specific device profile. |
| **`BILLED_IN`** | `Transaction` | `BillingRegion` | None | Transaction billed in geographic region. |
| **`PURCHASER_EMAIL`** | `Transaction` | `EmailDomain` | None | Transaction associated with purchaser email domain. |
| **`RECIPIENT_EMAIL`** | `Transaction` | `EmailDomain` | None | Transaction associated with merchant/recipient email domain. |
| **`NEXT_TRANSACTION`**| `Transaction` | `Transaction` | `delta_seconds INT, delta_amount FLOAT` | Temporal sequential link between consecutive transactions on same card. |
| **`CASE_INVOLVES`** | `ClosedCase` / `DynamicCase` | `Transaction` | `is_first_fraud BOOL` | Case encompasses transaction. |
| **`CASE_ON_CARD`** | `ClosedCase` / `DynamicCase` | `Card` | None | Primary compromised card under investigation. |
| **`CONNECTED_CARD`** | `ClosedCase` / `DynamicCase` | `Card` | `connection_reason STRING` | Connected cards caught in same fraud cluster or shared device ring. |

---

## 9. Conclusion & Next Steps

This analysis provides the foundational ground truth for the HHGOA_IEEE fraud investigation challenge. Every file, column, relationship, pattern, policy rule, approval hierarchy, and graph element has been verified against the physical raw dataset.

**Immediate Next Phases:**
1. **Data Preprocessing & Graph Pipeline (`tigergraph/`):**
   - Create schema creation GSQL script (`tigergraph/schema.gsql`).
   - Create data loading job (`tigergraph/load_data.gsql`) mapping `transactions.csv`, `identity.csv`, and `closed_cases_history.csv`.
2. **Graph Queries & MCP Tools (`agent/tools/`):**
   - Implement GSQL queries: `card_window_query`, `device_neighbors_query`, `region_anomaly_query`, `similar_closed_cases_query`.
   - TigerGraph MCP server integration.
3. **Agent Core & GraphRAG Engine (`agent/` & `graphrag/`):**
   - LangGraph / Agent state machine implementing investigation loop (Trigger -> Gather Graph Evidence -> Vector Context -> Policy Evaluation -> Decision & Action Routing).
4. **Benchmark Execution (`cases/`):**
   - Run autonomous investigations on all 20 benchmark cases (`HHG-001` through `HHG-020`) and generate conforming JSON answer files.
