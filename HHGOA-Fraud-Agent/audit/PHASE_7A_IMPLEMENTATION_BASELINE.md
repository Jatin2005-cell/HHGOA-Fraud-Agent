# Phase 7A Implementation Baseline Report

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Date:** September 20, 2026  
**Auditor:** Antigravity Autonomous Systems Engineer  
**Objective:** Baseline audit of existing APIs, schemas, and frontend components before Phase 7A execution.

---

## 1. Backend REST API Baseline (FastAPI on Port 8000)

| Endpoint | Method | Service / Handler | Data Source | Provenance Mode |
|---|---|---|---|---|
| `/health` | GET | `api.main.health_check` | In-memory | `healthy` |
| `/health/dependencies` | GET | `api.main.health_dependencies` | `TigerGraphMCPClient.get_runtime_status()` | `OFFLINE_STAGED_SIMULATION` |
| `/api/investigations` | POST | `InvestigationService.create_investigation` | `CaseRepository` | `LOCAL_STAGED_DATASET` |
| `/api/investigations/{id}/run` | POST | `InvestigationService.run_investigation` | `InvestigationOrchestrator` -> Staged CSV | `LOCAL_STAGED_DATASET` |
| `/api/investigations/{id}` | GET | `InvestigationService.get_investigation` | `CaseRepository` | `LOCAL_STAGED_DATASET` |
| `/api/investigations/{id}/timeline` | GET | `InvestigationService.get_timeline` | `TimelineBuilder` | In-memory / recorded trace |
| `/api/investigations/{id}/evidence` | GET | `EvidenceService.get_case_evidence` | `CaseRepository` | Staged CSV evidence |
| `/api/investigations/{id}/actions` | GET | `ActionService.get_actions` | `CaseRepository` | Policy engine output |
| `/api/investigations/{id}/approval` | GET | `ApprovalService.get_approval_status` | `CaseRepository` | Governance queue |
| `/api/investigations/{id}/sar` | GET | `SARService.get_sar` | `CaseRepository` | Generated FinCEN SAR |
| `/api/investigations/{id}/graph` | GET | `InvestigationService.get_investigation_graph` | `edges_*.csv` in `dataset/processed/` | Staged topology |
| `/api/cases` | GET | `CaseService.list_cases` | `CaseRepository` | In-memory / dynamic_cases.csv |
| `/api/cases/{id}` | GET | `CaseService.get_case` | `CaseRepository` | DynamicCase record |
| `/api/approvals/{id}/approve` | POST | `ApprovalService.approve_action` | `CaseRepository` | Human governance |
| `/api/approvals/{id}/reject` | POST | `ApprovalService.reject_action` | `CaseRepository` | Human governance |
| `/api/sar/{id}` | GET | `SARService.get_sar` | `CaseRepository` | Regulatory filing |
| `/api/dashboard/summary` | GET | `DashboardService.get_summary` | `CaseRepository` | Real KPIs |
| `/api/dashboard/distribution`| GET | `DashboardService.get_distributions` | `CaseRepository` | Real distributions |
| `/api/benchmark` | GET | `BenchmarkService.get_summary` | `BenchmarkRunner` / `case_pack.csv` | 20 exam cases |
| `/api/audit` | GET | `AuditService.get_events` | `case_management/audit.log` | Immutable audit trail |
| `/api/search` | GET | `SearchService.global_search` | `CaseRepository` index | Entity search |

---

## 2. Frontend Pre-Implementation Baseline

- **Framework:** React 19.2.8 + Vite 8.3.0 + TypeScript 5.8
- **Styling:** TailwindCSS 4 + `@tailwindcss/vite` + Lucide Icons + Recharts
- **Pre-existing UI Components:**
  - Layout: `AppLayout.tsx`, `Header.tsx`, `Sidebar.tsx`
  - Dashboard: `Dashboard.tsx`, `KpiCard.tsx`, `CaseCharts.tsx`
  - Case Table: `CaseTable.tsx`, `CaseFilterBar.tsx`
  - Investigation: `InvestigationForm.tsx`, `InvestigationPipeline.tsx`
  - Case Details Tabs: `OverviewTab.tsx`, `GraphTab.tsx`, `EvidenceTab.tsx`, `TimelineTab.tsx`, `ActionsTab.tsx`, `ApprovalTab.tsx`, `SarTab.tsx`, `AiExplanationTab.tsx`
- **Pre-existing Deficiencies to Remediate in Phase 7A:**
  1. `App.tsx` had the default Vite starter counter instead of full React Router routes.
  2. Missing page views: `Investigate.tsx`, `Cases.tsx`, `CaseDetails.tsx`, `Approvals.tsx`, `SarReports.tsx`, `Benchmark.tsx`, `AuditLogs.tsx`.
  3. No centralized strongly typed `useRuntimeStatus` hook and global `ProvenanceBanner`.
  4. "Why Connected?" interactive edge reasoning in `GraphTab.tsx` needed full integration with factual backend topology.
