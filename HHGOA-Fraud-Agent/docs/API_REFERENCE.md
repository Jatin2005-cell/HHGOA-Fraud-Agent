# HHGOA Fraud Investigation REST API Reference

**Service Name:** `HHGOA-Fraud-Agent-API`  
**Version:** `1.0.0`  
**Base URL:** `http://localhost:8000` (or configured `API_HOST:API_PORT`)  
**API Prefix:** `/api/v1`  
**Architecture:** FastAPI, Asynchronous, OpenAPI 3.1 compliant  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc` (ReDoc)

---

## 1. Authentication & Security

- **Mechanism:** Bearer Token via `Authorization` header (`Authorization: Bearer <API_AUTH_TOKEN>`).
- **Configurable:** When `API_AUTH_ENABLED=false` (development mode), requests without headers are accepted.
- **Request Correlation:** Every incoming request receives or tracks an `X-Request-ID` header, propagated through audit trails and responses.
- **Injection Sanitization:** All string path and query parameters undergo strict regex validation blocking SQL/GSQL destructive keywords (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `INTERPRET QUERY`).

---

## 2. Standard Response Envelopes

### Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "request_id": "req-9b8417c2"
}
```

### Error Envelope
```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Invalid lifecycle transition from CLOSED to INVESTIGATING",
    "details": {}
  },
  "request_id": "req-9b8417c2"
}
```

---

## 3. Endpoints Directory

### 3.1 System & Health Checks

#### `GET /health`
Returns high-level API operational status and timestamp.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "hhgoa-fraud-investigation-api",
  "timestamp": "2026-09-20T18:22:00Z"
}
```

#### `GET /health/dependencies`
Deep diagnostics for upstream services: TigerGraph instance, MCP query readiness, and dynamic case repository persistence.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "dependencies": {
    "case_repository": { "status": "UP", "path": "data/cases" },
    "tigergraph_writeback": { "status": "UP", "staged_sync": true },
    "mcp_investigation_tools": { "status": "UP", "mode": "read-only" }
  }
}
```

---

### 3.2 Investigations

#### `POST /api/v1/investigations`
Trigger an autonomous fraud investigation using the Phase 5 multi-agent orchestrator.

**Request Body:**
```json
{
  "case_id": "HHG-001",
  "trigger_type": "risk_score",
  "trigger_text": "High risk transaction flagged by real-time ML score",
  "flagged_txn_id": "3000001",
  "customer_id": "CUST_001",
  "card_id": "CARD_001",
  "risk_score": 0.94
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "case_id": "HHG-001",
    "status": "APPROVAL_PENDING",
    "verdict": "CONFIRMED_FRAUD",
    "fraud_probability": 0.96,
    "pattern": "CARD_CLONING",
    "exposure_usd": 1285.50,
    "approval_route": "L2",
    "sar_required": true,
    "writeback_status": "VERIFIED"
  }
}
```

#### `GET /api/v1/investigations/{case_id}`
Fetch real-time investigation progress and results for a specific case identifier.

---

### 3.3 Dynamic Cases & Lifecycle

#### `GET /api/v1/cases`
Filter and paginate persisted fraud cases.

**Query Parameters:**
- `status` (string, optional): Lifecycle status (`NEW`, `INVESTIGATING`, `APPROVAL_PENDING`, `RESOLVED`, `CLOSED`, etc.)
- `verdict` (string, optional): `CONFIRMED_FRAUD`, `SUSPICIOUS`, `LEGITIMATE`
- `pattern` (string, optional): `CARD_CLONING`, `ACCOUNT_TAKEOVER`, `CARDING_TESTING`, etc.
- `approval_route` (string, optional): `auto`, `L1`, `L2`
- `limit` (int, default: 20): Number of records per page
- `offset` (int, default: 0): Pagination offset

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 20,
    "limit": 20,
    "offset": 0,
    "cases": [ ... ]
  }
}
```

#### `GET /api/v1/cases/{case_id}`
Retrieve full details, graph writeback verification, metadata, and verdict for a specific case.

#### `PATCH /api/v1/cases/{case_id}/status`
Transition case lifecycle state under deterministic finite state machine rules.

**Request Body:**
```json
{
  "status": "RESOLVED",
  "reason": "Customer confirmed legitimate authorization after out-of-band contact",
  "actor": "investigator_alice"
}
```

#### `GET /api/v1/cases/{case_id}/timeline`
Retrieve complete chronological audit log of all events, transitions, agent iterations, and human decisions.

---

### 3.4 Evidence & Graph Context

#### `GET /api/v1/cases/{case_id}/evidence`
Retrieve structured multi-hop graph evidence, card transaction windows, device neighbor overlaps, and similar historical precedents.

#### `POST /api/v1/cases/{case_id}/evidence`
Attach external or manual evidence (chargeback notices, IP telemetry, customer call logs) to an active investigation.

---

### 3.5 Action Execution & Mitigation

#### `GET /api/v1/cases/{case_id}/actions`
View recommended Next Best Actions (Initial, Final after GraphRAG, and delta changes).

#### `POST /api/v1/cases/{case_id}/actions/execute`
Execute or simulate recommended mitigation actions (`BLOCK_CARD`, `RESTRICT_ACCOUNT`, `DISMISS_ALERT`, etc.).

---

### 3.6 Human-in-the-Loop Approvals

#### `GET /api/v1/approvals/pending`
Retrieve all cases awaiting human supervisor review, filtered by routing level (`L1` vs `L2`).

#### `POST /api/v1/approvals/{case_id}/decision`
Submit supervisor decision (`APPROVE`, `REJECT`, `ESCALATE`).

**Request Body:**
```json
{
  "decision": "APPROVE",
  "approver_role": "FRAUD_MANAGER",
  "approver_id": "mgr_carol",
  "notes": "Confirmed high-velocity card cloning across 3 foreign IPs."
}
```

**Enforcement Rules:**
- Agent cannot self-approve (`ACTOR_TYPE != AGENT`).
- `L1` actions require Team Lead or higher.
- `L2` actions (exposure > $1,000 or customer freeze) require Fraud Manager.

---

### 3.7 FinCEN Suspicious Activity Reports (SAR)

#### `GET /api/v1/cases/{case_id}/sar`
Retrieve the generated FinCEN-compliant SAR package, complete with 6–12 sentence legal narrative, suspect subjects, and exposure amount.

#### `POST /api/v1/cases/{case_id}/sar/generate`
Manually trigger or regenerate SAR documentation if policy rules (R1, R8, R10) are satisfied.

#### `POST /api/v1/cases/{case_id}/sar/validate`
Validate existing SAR payload against regulatory completeness rules (narrative word count $\ge 40$, required subjects, valid timestamps).
