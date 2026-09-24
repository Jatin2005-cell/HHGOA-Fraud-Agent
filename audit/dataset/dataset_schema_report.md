# Dataset Schema & Cryptographic Integrity Forensic Report

**Dataset Name:** HHGOA_IEEE Fraud Investigation Dataset  
**Location:** `dataset/raw/`  
**Integrity Status:** **VERIFIED (100% Match)**  

---

## 1. Raw Dataset Cryptographic Inventory

| Filename | File Size (Bytes) | SHA-256 Checksum | Actual Rows | Actual Cols | Integrity Audit |
|---|---|---|---|---|---|
| `transactions.csv` | 707,936,515 | `dd084e58d7c33e7fd5a59c7b992ba9d6f62b0bd443fb19d4a5d5212e0246bb2b` | 590,742 | 397 | **VERIFIED** |
| `identity.csv` | 26,716,154 | `9ebd6740ecb7e2afd392b5082a6f349907e871144659f622f5302ecd4ca39fad` | 144,432 | 41 | **VERIFIED** |
| `closed_cases_history.csv` | 2,706,417 | `840613948d023fc3ddbfcb3291d5be250ee328e6eba1d2810b010fca5a757854` | 5,565 | 15 | **VERIFIED** |
| `case_pack.csv` | 3,548 | `353494638b6ec2f07af67257b90ab85a1f1d537a0f015089abd9b54cfc7596e4` | 20 | 8 | **VERIFIED** |
| `README.md` | 38,663 | `57e6dd7c7766b4efe3e903f111be2f4237d058d53e3b1738d6e56dcd6cecda59` | 472 lines | 1 | **VERIFIED** |

---

## 2. Forensic Statistical Verification

### 2.1 `transactions.csv`
- **Total Row Count:** `590,742` transactions.
- **TransactionID Range:** Minimum `3,000,001` to Maximum `3,590,742`.
- **Continuous Temporal Span:** Spanning 6 continuous months (`TransactionDT` delta matches 183 days).
- **Risk Score Feature:** Continuous range from `0.01` to `0.99` (No artificial binary "is_fraud" ground truth present).
- **Unique Account Holders / Customers:** `13,553` distinct entities.
- **Product Category Distribution:**
  - `W` (Web / E-commerce): 439,670 (74.4%)
  - `C` (Commercial / POS): 68,721 (11.6%)
  - `R` (Retail): 37,699 (6.4%)
  - `H` (Hotel / Travel): 33,024 (5.6%)
  - `S` (Service): 11,628 (2.0%)

### 2.2 `identity.csv`
- **Total Row Count:** `144,432` device/network identity records.
- **Join Completeness:** 100% of identity records map directly to legitimate `TransactionID` values in `transactions.csv`.
- **Device Categories:** `Desktop` (85,204), `Mobile` (55,801), Unspecified (3,427).

### 2.3 `closed_cases_history.csv`
- **Total Historical Precedents:** `5,565` closed investigation files from the initial 4 months.
- **Outcomes:** `confirmed_fraud`: 4,665 (83.8%), `cleared`: 900 (16.2%).
- **Fraud Typologies Documented:**
  - Card Not Present (CNP): 1,404
  - Account Takeover (ATO): 1,205
  - CNP New Device: 1,076
  - Out of Region Use: 955
  - None (Cleared): 900
  - Card Testing: 16
  - Undocumented Typologies: 9
- **SAR Reports Filed Historically:** 397 cases mandated regulatory SAR submission.

### 2.4 `case_pack.csv` (20 Benchmark Exam Cases)
- **Exact Case IDs:** `HHG-001` through `HHG-020`.
- **Zero Duplicate Case IDs:** 20 unique cases.
- **Trigger Type Breakdown:**
  - `risk_score`: 11 cases
  - `customer_report`: 8 cases
  - `analyst_request`: 1 case
- **Temporal Non-Overlap:** All 20 cases originate strictly from the final 2 evaluation months; zero overlap exists with `closed_cases_history.csv`.
