# PHASE 7A.5 — STARTUP & CONNECTION REPORT
## HHGOA_IEEE TigerGraph Agentic Fraud Investigation

**Generated:** 2026-09-20  
**Auditor:** Antigravity Agent

---

## FINDINGS SUMMARY

| Check | Status | Detail |
|-------|--------|--------|
| PROJECT ROOT | ✅ FOUND | `C:\Users\LOQ\Downloads\hhgoa fraud\HHGOA-Fraud-Agent` |
| API MAIN | ✅ FOUND | `api\main.py` exists |
| FASTAPI IMPORT | ✅ PASS | `from api.main import app` → `FastAPI` |
| UVICORN | ✅ PASS | uvicorn 0.53.0 / Python 3.12.10 |
| FASTAPI SERVER | ✅ PASS | Running on `http://127.0.0.1:8000` |
| /docs | ✅ PASS | Swagger UI accessible |
| /health/dependencies | ✅ PASS | `OFFLINE_STAGED_SIMULATION` |
| FRONTEND | ✅ PASS | Vite dev server on `http://localhost:5174/` |
| API BASE URL | ✅ PASS | `http://127.0.0.1:8000` (via `.env`) |
| CORS | ✅ PASS | `allow_origins=["*"]` for dev |
| VITE PROXY | ✅ PASS | `/api` + `/health` proxied to `http://127.0.0.1:8000` |
| /api/dashboard/summary | ✅ FIXED | Was 500 — NoneType bug fixed |
| /api/dashboard/distribution | ✅ FIXED | Was 500 — NoneType bug fixed |
| /api/cases | ✅ PASS | 36 cases returned |
| /api/investigations/:id | ✅ PASS | 200 OK |
| /api/benchmark | ✅ PASS | 20-case report returned |
| /api/audit | ✅ PASS | Paginated log entries returned |
| /api/search | ✅ PASS | 200 OK |
| PYTEST | ✅ PASS | 18 passed, 0 failed |
| LINT | ✅ PASS | 15 warnings, 0 errors |
| BUILD | ✅ PASS | 0 TypeScript errors |
| TIGERGRAPH | 📊 OFFLINE_STAGED_SIMULATION | graph_verified=false |
| LIVE TIGERGRAPH | ❌ NOT VERIFIED | Not provisioned — by design |

---

## ROOT CAUSE OF "Service Unavailable" / "Network Error"

### Bug 1 — Wrong startup directory
The user ran `python -m uvicorn api.main:app` from the parent directory  
`C:\Users\LOQ\Downloads\hhgoa fraud` instead of the project root:  
`C:\Users\LOQ\Downloads\hhgoa fraud\HHGOA-Fraud-Agent`

This caused `ModuleNotFoundError: No module named 'api'`.

**Fix:** Always `cd` into `HHGOA-Fraud-Agent` first:
```powershell
cd "C:\Users\LOQ\Downloads\hhgoa fraud\HHGOA-Fraud-Agent"
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Bug 2 — Dashboard 500 error (NoneType comparison)
`api/routes/dashboard.py` compared `c.fraud_probability >= 0.7` and  
`c.risk_score >= 0.7` without None guard. Test cases (HHG-TEST-*) have  
`fraud_probability = null`, causing `TypeError: '>=' not supported between  
instances of 'NoneType' and 'float'`.

**Fix:** Added `or 0.0` guard to both comparisons (lines 22, 60).

---

## HOW TO START (CORRECT COMMANDS)

```powershell
# Terminal 1 — FastAPI Backend
cd "C:\Users\LOQ\Downloads\hhgoa fraud\HHGOA-Fraud-Agent"
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — React Frontend
cd "C:\Users\LOQ\Downloads\hhgoa fraud\HHGOA-Fraud-Agent\frontend"
npm run dev
# → http://localhost:5174/
```

---

## RUNTIME VERIFICATION

```
GET /health/dependencies → 200 OK
{
  "data_mode": "OFFLINE_STAGED_SIMULATION",
  "graph_verified": false,
  "mcp_verified": false,
  "writeback_verified": false
}
```

The frontend ProvenanceBanner will show **amber** with `OFFLINE STAGED SIMULATION`.  
This is correct. TigerGraph is **not** provisioned.

---

## SECURITY CHECK

- No TigerGraph credentials in frontend source ✅
- No API keys in frontend ✅  
- No backend secrets embedded in `.env` ✅
- `graph_verified`, `mcp_verified`, `writeback_verified` all remain `false` ✅

---

## PHASE 7A FRONTEND CONNECTION: ✅ PASS

**Root causes fixed:**
1. Startup directory clarified (must run from `HHGOA-Fraud-Agent/`)
2. Dashboard 500 bug fixed (NoneType guard on `fraud_probability`)

All API endpoints now return 200 with real HHGOA_IEEE dataset data.
