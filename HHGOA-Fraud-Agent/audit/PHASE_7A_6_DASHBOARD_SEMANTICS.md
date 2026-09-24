# PHASE 7A.6 — DASHBOARD DATA SEMANTICS AUDIT REPORT
## HHGOA_IEEE TigerGraph Agentic Fraud Investigation

**Generated:** 2026-09-20  
**Status:** COMPLETE  
**Auditor:** Antigravity System

---

## 1. EXECUTIVE SUMMARY

| Audit Item | Result | Evidence |
|------------|--------|----------|
| **NULL SEMANTICS** | **UNKNOWN** | `fraud_probability: Optional[float] = None` in schema; populated only upon investigation completion |
| **DASHBOARD LOGIC** | **CORRECT** | Explicit `_best_risk_score()` selector, `Pending Assessment` tier, null exclusion from averages |
| **TESTS** | **PASS** | 31/31 Pytest passed, all 5 core endpoints verified HTTP 200 |

---

## 2. NULL SEMANTICS INVESTIGATION

### 2.1 Codebase Schema Inspection
In `agent/schemas/investigation_schema.py`:
```python
class InvestigationState(BaseModel):
    ...
    fraud_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
```
In `case_management/case_repository.py`:
```python
class DynamicCaseRecord(BaseModel):
    case_id: str
    status: CaseStatus = CaseStatus.NEW
    risk_score: Optional[float] = None
    fraud_probability: Optional[float] = None
```

### 2.2 Case Lifecycle & Generation Logic
1. When an alert arrives or a case is initialized in status `NEW`, `fraud_probability` is `None`.
2. The pre-screening alert score is placed in `risk_score` (if available from rule triggers).
3. `fraud_probability` is computed autonomously by the 17-state GraphRAG agent during investigation execution (`DECIDE_VERDICT` / `WRITEBACK_RESULTS`).
4. Therefore, `fraud_probability = None` definitively means **UNKNOWN / NOT YET CALCULATED**, and NEVER 0.0 (benign/zero fraud probability).

---

## 3. DASHBOARD AGGREGATION RULES (`api/routes/dashboard.py`)

1. **No Coercion to 0.0**: `None` is never coerced to `0.0` for analytics or risk banding.
2. **Authoritative Priority**: `_best_risk_score(c)` prioritizes agent-verified `c.fraud_probability`. If uncomputed, it falls back to alert pre-screening `c.risk_score`.
3. **Pending Assessment Category**: Cases where both `fraud_probability` and `risk_score` are `None` are placed into a dedicated `"Pending Assessment"` bucket in `/api/dashboard/distribution` rather than being falsely classified as "Low Risk (<0.4)".
4. **KPI Integrity**:
   - `high_risk_cases`: Only cases with a known score &ge; 0.70 are counted.
   - `pending_assessment`: Cases lacking both scores are exposed via dedicated KPI card.
   - `total_cases`: Full case population is accurately preserved.

---

## 4. ENDPOINT VERIFICATION (LIVE HTTP 200)

| Endpoint | HTTP Status | Response Verification |
|----------|-------------|-----------------------|
| `GET /api/dashboard/summary` | **200 OK** | Returned total_cases=37, high_risk_cases=22, pending_assessment=3, pending_approvals=9, exposure=$2575.17 |
| `GET /api/dashboard/distribution` | **200 OK** | Returned cases_by_status, cases_by_pattern, risk_distribution (including 'Pending Assessment'=3), approval_distribution |
| `GET /api/cases` | **200 OK** | Full paginated case list successfully retrieved |
| `GET /api/benchmark` | **200 OK** | 20-case benchmark suite results retrieved |
| `GET /health/dependencies` | **200 OK** | Verified `data_mode: "OFFLINE_STAGED_SIMULATION"`, `graph_verified: false` |

---

## 5. AUTOMATED TEST VALIDATION

- **Pytest Suite**: 31 passed in 14.62s (100% PASS rate, 0 failures, 0 errors).
- **TypeError / Null Guarding**: Zero NoneType comparison regressions.
