# Phase 6 Benchmark Persistence & Graph Writeback Report

**Execution Date:** 2026-09-20T12:53:37.472022+00:00  
**Total Benchmark Cases:** 20  
**Graph Readback Verification:** 100.0% PASS  

---

## 1. Quantitative Verification Summary

| Metric | Value | Compliance Requirement | Status |
|---|---|---|---|
| **Total Cases Persisted** | 20 / 20 | 20 / 20 | **PASS** |
| **Graph Readback Verification Rate** | 100.0% | 100.0% | **PASS** |
| **SARs Generated Under Policy** | 6 | Policy-Governed | **PASS** |
| **Average Case Writeback Latency** | 4.88s | < 5.0s | **PASS** |

---

## 2. Case Persistence Audit Table

| Case ID | Trigger | Verdict | Pattern | Exposure | Writeback | Approval | SAR |
|---|---|---|---|---|---|---|---|
| `HHG-001` | risk_score | **legitimate** | none | $0.00 | VERIFIED | `auto` | False |
| `HHG-002` | risk_score | **legitimate** | card_not_present_fraud | $0.00 | VERIFIED | `auto` | False |
| `HHG-003` | customer_report | **fraud** | none | $49.00 | VERIFIED | `L1` | False |
| `HHG-004` | customer_report | **fraud** | card_not_present_fraud | $128.33 | VERIFIED | `L2` | True |
| `HHG-005` | risk_score | **legitimate** | card_not_present_fraud | $0.00 | VERIFIED | `auto` | False |
| `HHG-006` | customer_report | **fraud** | card_not_present_fraud | $482.12 | VERIFIED | `L2` | True |
| `HHG-007` | risk_score | **legitimate** | none | $0.00 | VERIFIED | `auto` | False |
| `HHG-008` | customer_report | **fraud** | card_not_present_fraud | $55.68 | VERIFIED | `L2` | True |
| `HHG-009` | customer_report | **fraud** | card_not_present_fraud | $30.02 | VERIFIED | `L2` | True |
| `HHG-010` | risk_score | **uncertain** | card_not_present_fraud | $1000.03 | VERIFIED | `auto` | False |
| `HHG-011` | customer_report | **fraud** | card_not_present_fraud | $131.30 | VERIFIED | `L2` | True |
| `HHG-012` | risk_score | **legitimate** | none | $0.00 | VERIFIED | `auto` | False |
| `HHG-013` | risk_score | **legitimate** | card_not_present_fraud | $0.00 | VERIFIED | `auto` | False |
| `HHG-014` | analyst_request | **legitimate** | none | $0.00 | VERIFIED | `auto` | False |
| `HHG-015` | risk_score | **uncertain** | card_not_present_fraud | $599.94 | VERIFIED | `auto` | False |
| `HHG-016` | customer_report | **fraud** | card_not_present_fraud | $59.67 | VERIFIED | `L2` | True |
| `HHG-017` | risk_score | **legitimate** | card_not_present_fraud | $0.00 | VERIFIED | `auto` | False |
| `HHG-018` | customer_report | **fraud** | none | $39.08 | VERIFIED | `L1` | False |
| `HHG-019` | risk_score | **legitimate** | card_not_present_fraud | $0.00 | VERIFIED | `auto` | False |
| `HHG-020` | risk_score | **legitimate** | card_not_present_fraud | $0.00 | VERIFIED | `auto` | False |