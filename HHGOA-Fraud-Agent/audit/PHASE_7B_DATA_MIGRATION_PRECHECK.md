# PHASE 7B — SOURCE DATASET VERIFICATION REPORT
## HHGOA_IEEE Programmatic Pre-Ingestion Baseline

**Date:** 2026-09-20  
**Status:** VALIDATED SOURCE BASELINE  
**Auditor:** Autonomous Phase 7B Migration Engineer  

---

## 1. PROGRAMMATICALLY COMPUTED SOURCE COUNTS

Every source entity and relationship file in `dataset/processed/` was counted directly from disk:

| Vertex / Edge Name | Source File | Exact Record Count | Primary ID / Key Structure |
|---|---|---|---|
| **Customer** | `customers.csv` | **13,553** | `customer_id` (`Cxxxxx`) |
| **Card** | `cards.csv` | **24,234** | `card_id` (`Cxxxxx-K1/2/3`) |
| **Transaction** | `transactions.csv` | **590,742** | `txn_id` (numeric string) |
| **DeviceProfile** | `devices.csv` | **9,706** | `device_hash` (`DEV_<md5[:16]>`) |
| **BillingRegion** | `billing_regions.csv` | **332** | `region_id` (`REG_<addr1>`) |
| **EmailDomain** | `email_domains.csv` | **60** | `domain_name` (e.g. `gmail.com`) |
| **ClosedCase** | `closed_cases.csv` | **5,565** | `case_id` (`CASE-xxxxx`) |
| **DynamicCase** | `dynamic_cases.csv` | **20** | `case_id` (`HHG-001..020`) |
| **OWNS** | `edges_owns.csv` | **24,234** | `(customer_id, card_id)` |
| **MADE** | `edges_made.csv` | **590,742** | `(card_id, txn_id)` |
| **FROM_DEVICE** | `edges_from_device.csv` | **144,432** | `(txn_id, device_hash)` |
| **BILLED_IN** | `edges_billed_in.csv` | **525,003** | `(txn_id, region_id)` |
| **PURCHASER_EMAIL** | `edges_purchaser_email.csv` | **496,262** | `(txn_id, domain_name)` |
| **RECIPIENT_EMAIL** | `edges_recipient_email.csv` | **137,453** | `(txn_id, domain_name)` |
| **NEXT_TRANSACTION** | `edges_next_transaction.csv` | **576,264** | `(txn_id, txn_id)` sequential |
| **CASE_INVOLVES** | `edges_case_involves.csv` | **14,975** | `(case_id, txn_id)` |
| **CASE_ON_CARD** | `edges_case_on_card.csv` | **5,585** | `(case_id, card_id)` |
| **CONNECTED_CARD** | `edges_connected_card.csv` | **92** | `(case_id, card_id)` |

---

## 2. KNOWN TRANSACTION BASELINE (TXN: 3478561)

Direct record inspection from `dataset/processed/transactions.csv`:

```text
txn_id:         3478561
card_id:        C13487-K1
ts:             2016-11-22 16:11:00
amount:         74.96 USD
product_cd:     C
channel:        online
risk_score:     0.05
addr1 (region): 191.0
addr2 (dist):   87.0
p_emaildomain:  yahoo.com
r_emaildomain:  gmail.com
m_flags:        NA_NA_NA_NA_NA_NA_NA_NA_NA
```

---

## 3. MIGRATION INGESTION READINESS

All 18 source CSV files are intact, validly formatted, and ready for streaming into `FraudInvestigationGraph` upon connection to the active Savanna instance.
