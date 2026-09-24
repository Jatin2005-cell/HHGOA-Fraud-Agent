# TigerGraph MCP Integration Test Plan

**Version:** 1.0.0  
**Target Graph:** `FraudInvestigationGraph`  
**Execution Scope:** Phase 4 MCP Tool Interface Verification  

---

## 1. Test Objectives

1. Verify that the MCP tool layer connects to TigerGraph without bypassing GSQL investigation queries.
2. Validate strict read-only enforcement (`TG_ALLOWED_TOOLS="query,read-only"`, `TG_BLOCKED_TOOLS="destructive"`).
3. Confirm input sanitization and rejection of malformed IDs or out-of-bound arguments.
4. Execute 5 required real-world dataset test scenarios:
   - Risk-Score Benchmark Alert (`HHG-001`: `3514030`)
   - Customer-Report Benchmark Alert (`HHG-003`: `3530164`)
   - Analyst-Request Benchmark Alert (`HHG-014`: `3478561`)
   - Historical Confirmed Fraud Case (`CC-0001`: `3000120`)
   - Historical Cleared False Alarm (`CC-0003`: `3000607`)
5. Validate deep multi-hop graph traversal through MCP:
   - `Transaction ──► Card ──► Customer`
   - `Transaction ──► DeviceProfile ──► Other Transactions ──► Other Cards/Customers`
   - `Transaction ──► ClosedCase`
6. Verify bounded payload control to prevent context window saturation in Phase 5.
7. Confirm audit logging for security compliance.

---

## 2. Test Execution Matrix

| Test ID | Test Category | Target Tool | Test Input | Expected Behavior |
|---|---|---|---|---|
| **MCP-01** | Risk-Score Benchmark Alert | `get_transaction_context` | `transaction_id = 3514030` | Return complete 360° dossier; Card `C12382-K1`, Customer `C12382`, Region `REG_444.0`. |
| **MCP-02** | Customer-Report Benchmark Alert | `find_similar_closed_cases` | `customer_id = "C08623"` | Return 6 prior closed cases from historical memory. |
| **MCP-03** | Analyst-Request Benchmark Alert | `find_device_neighbors` | `transaction_id = 3478561` | Discover shared device `DEV_c72bd41105eb39dd`, 114 txns across 52 cards. |
| **MCP-04** | Historical Confirmed Fraud | `get_transaction_context` | `transaction_id = 3000120` | Return case `CC-0001`, Card `C00259-K1`, confirmed fraud, exposure $155.43. |
| **MCP-05** | Historical Cleared False Alarm | `find_region_anomalies` | `card_id = "C05876-K2"`, `txn_id = 3000607` | Return regional distribution; verify customer travel history. |
| **MCP-06** | Multi-Hop Traversal Validation | `get_transaction_context` + `find_device_neighbors` | `transaction_id = 3478561` | Verify 3-hop traversal: `Txn -> Device -> Txns -> Cards -> Customers`. |
| **MCP-07** | Input Validation: Malformed Txn ID | `get_transaction_context` | `transaction_id = "ABC-999"` | Raise `ValueError`; reject execution without querying TigerGraph. |
| **MCP-08** | Input Validation: Out-of-Bounds Window | `get_card_transaction_window` | `window_hours = 999` | Raise `ValueError`; reject request exceeding 168-hour limit. |
| **MCP-09** | Audit Logging Verification | Logger Verification | Post-Execution Inspection | Confirm `audit.log` records timestamp, query, status, latency, with zero credential leaks. |
