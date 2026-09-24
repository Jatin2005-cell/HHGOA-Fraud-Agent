# Investigation & Case Management REST API

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Component:** `api/`  
**Phase:** Phase 6  
**Framework:** FastAPI / Uvicorn  

---

## 1. Overview

The `api/` package delivers the REST API layer for frontend clients, orchestrating fraud investigations, lifecycle transitions, provenanced evidence access, human approval workflows, and FinCEN SAR reporting.

---

## 2. API Endpoints Reference

| HTTP Verb | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness health check |
| `GET` | `/health/dependencies` | Database and agent dependency status |
| `POST` | `/api/investigations` | Register a new alert investigation case |
| `POST` | `/api/investigations/{case_id}/run` | Run autonomous agent & persist DynamicCase |
| `GET` | `/api/investigations/{case_id}` | Complete case record |
| `GET` | `/api/investigations/{case_id}/timeline` | Chronological audit timeline |
| `GET` | `/api/investigations/{case_id}/evidence` | Provenanced graph evidence claims |
| `GET` | `/api/investigations/{case_id}/actions` | Initial and final next-best actions |
| `GET` | `/api/investigations/{case_id}/approval` | Governance approval status |
| `POST` | `/api/approvals/{case_id}/approve` | Human supervisor action approval |
| `POST` | `/api/approvals/{case_id}/reject` | Human supervisor action rejection |
| `GET` | `/api/investigations/{case_id}/sar` | FinCEN Suspicious Activity Report |
| `POST` | `/api/investigations/{case_id}/evidence-request`| Issue simulated evidence query |
| `GET` | `/api/cases` | Search and filter cases with pagination |
| `GET` | `/api/cases/{case_id}` | Single case details |
