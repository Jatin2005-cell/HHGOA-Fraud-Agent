# Case Management & Controlled Graph Writeback Layer

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Component:** `case_management/`  
**Phase:** Phase 6  

---

## 1. Overview

The `case_management/` subsystem provides persistent storage, deterministic lifecycle transitions, and controlled, safe graph writeback for fraud investigation cases.

### Core Principles:
1. **Isolated Write Path:** While the Phase 4 Investigation MCP operates strictly in read-only mode, `case_management/graph_writeback.py` handles validated mutations for `DynamicCase` vertices and incident edges.
2. **Deterministic Lifecycle:** 10 discrete states (`NEW` -> `INVESTIGATING` -> `EVIDENCE_PENDING` -> `REVIEW` -> `ACTION_REQUIRED` -> `APPROVAL_PENDING` -> `RESOLVED` -> `CLOSED`, plus `ESCALATED`, `FAILED`, `CANCELLED`). Illegal state jumps are strictly blocked.
3. **Idempotency & Readback:** Every writeback operation is verified via `graph_readback.py`, ensuring zero duplicate case creation and verified vertex attributes.
4. **Audit Logging:** Every operation is logged in `case_management/audit.log` with caller identity and sanitized payload parameters.
