# TigerGraph Data Lineage & End-to-End Execution Trace

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Challenge:** Hacker House Goa 2026  
**Audit Reference:** Phase 6.6 Specification (Section 14)  
**Execution Runtime:** OFFLINE_STAGED_SIMULATION (Level B)  

---

## 1. Overview of End-to-End Lineage

This audit documents the complete end-to-end lifecycle for two representative benchmark alerts:
1. **Case HHG-004:** Customer-Report Alert (`customer_report`) → Confirmed Card-Not-Present Fraud Path.
2. **Case HHG-014:** Fraud Analyst Request Alert (`analyst_request`) → Multi-Card Shared-Device Syndicate Investigation Path.

For each stage of execution, the exact operational data source is identified to maintain strict architectural provenance.

---

## 2. End-to-End Lineage Trace: Case HHG-004

```
[Trigger Ingestion]  dataset/raw/case_pack.csv (Row 5: HHG-004)
        │
        ▼
[Agent Activation]  agent/core/orchestrator.py -> InvestigationFSM (17-state machine)
        │
        ▼
[Tool Adapter]      agent/tools/mcp_tools.py (MCPInvestigationAdapter)
        │
        ▼
[MCP Layer]         mcp/tools/investigation_mcp_client.py (TigerGraphMCPClient)
        │
        ▼
[Query Engine]      _execute_local_query_engine() (Level B Simulation Mode)
        │           Reads: dataset/processed/transactions.csv (Txn 3583227)
        │                  dataset/processed/edges_from_device.csv
        │                  dataset/processed/closed_cases.csv
        │
        ▼
[Graph Evidence]    agent/graph_rag/graph_context_builder.py
        │           Normalized Evidence:
        │           - Online purchase $128.33 on card C08106-K1 for customer C08106
        │           - Device fingerprint DEV_9a7d32c58e12b409 (mobile Android browser)
        │           - Customer dispute: "I never made this $128.33 purchase"
        │
        ▼
[GraphRAG Fusion]   agent/graph_rag/retriever.py (HybridRetriever)
        │           - Historical Precedent: Customer C08106 has no prior fraud history
        │           - Pattern Document Store: Card Not Present (CNP) Fraud characteristics
        │           - Policy Store: Injects Policy Rules R1–R10
        │
        ▼
[Risk & Policy]     agent/policy/policy_rules.py & agent/core/risk_engine.py
        │           - Evaluated Rule R2 (Customer Dispute on Online Transaction)
        │           - Evaluated Rule R4 (High Risk Score / CNP Velocity)
        │           - Computed Fraud Probability: 0.86
        │           - Selected Typology: Card Not Present Fraud
        │
        ▼
[Action Selection]  agent/policy/next_best_action.py
        │           - Selected Actions:
        │             1. BLOCK_CARD (Immediate risk mitigation)
        │             2. REISSUE_CARD (Customer convenience)
        │             3. REIMBURSE_CUSTOMER ($128.33 credit)
        │             4. FILE_SAR (Required: confirmed unauthorized CNP compromise)
        │           - Approval Route: L2 (Requires L2_FRAUD_MANAGER governance sign-off)
        │
        ▼
[Case Creation]     case_management/case_repository.py
        │           Saved: cases/HHG-004.json & data/cases/HHG-004.json
        │
        ▼
[Graph Writeback]   case_management/graph_writeback.py (CaseWritebackService)
        │           Destination:
        │           - Vertex appended to: dataset/processed/dynamic_cases.csv
        │           - Edges appended to: dataset/processed/edges_case_involves.csv (Txn 3583227)
        │           - Edges appended to: dataset/processed/edges_case_on_card.csv (Card C08106-K1)
        │           (Live TigerGraph Writeback: NOT ACTIVE / OFFLINE MODE)
        │
        ▼
[Graph Readback]    case_management/graph_readback.py (CaseReadbackService)
        │           Verification:
        │           - Reads back persisted row from dynamic_cases.csv
        │           - Cross-references edge files -> Status: VERIFIED (Level B)
        │
        ▼
[API Exposure]      api/routes/investigations.py
                    GET /api/investigations/HHG-004 -> Returns dynamic investigation dossier
```

---

## 3. End-to-End Lineage Trace: Case HHG-014

```
[Trigger Ingestion]  dataset/raw/case_pack.csv (Row 15: HHG-014)
        │
        ▼
[Agent Activation]  agent/core/orchestrator.py -> InvestigationFSM
        │
        ▼
[Tool Adapter]      agent/tools/mcp_tools.py (MCPInvestigationAdapter)
        │
        ▼
[MCP Layer]         mcp/tools/investigation_mcp_client.py (TigerGraphMCPClient)
        │
        ▼
[Tool Queries]      Invokes:
        │           1. get_transaction_context(3478561)
        │           2. find_device_neighbors(3478561)
        │           3. find_connected_cards(C13487-K1)
        │           4. find_similar_closed_cases(pattern="shared_device_syndicate")
        │
        ▼
[Query Engine]      _execute_local_query_engine() (Level B Simulation Mode)
        │           Reads: dataset/processed/edges_from_device.csv
        │           Extracts: Device DEV_c72bd41105eb39dd
        │           Identifies: 114 transactions across 52 cards and 48 customers
        │           Discovers: Historical cases CC-2649, CC-2971, CC-2985, CC-3035
        │
        ▼
[Graph Evidence]    agent/graph_rag/graph_context_builder.py
        │           Normalized Evidence:
        │           - Device DEV_c72bd41105eb39dd shared across 52 distinct payment cards
        │           - Direct link to 4 historical closed syndicate fraud cases
        │           - Transaction 3478561 ($292.36) operates from high-velocity bot fingerprint
        │
        ▼
[GraphRAG Fusion]   agent/graph_rag/retriever.py (HybridRetriever)
        │           - Precedents: CC-2649, CC-2971 confirmed organized device ring
        │           - Policy Store: Injects Policy Rules R1–R10 (Rule R5 Shared Device Ring)
        │
        ▼
[Risk & Policy]     agent/policy/policy_rules.py
        │           - Evaluated Rule R5 (Shared Device / Multi-Card Syndicate Ring)
        │           - Computed Fraud Probability: 0.94
        │           - Selected Typology: Device Fingerprint Sharing
        │
        ▼
[Action Selection]  agent/policy/next_best_action.py
        │           - Selected Actions:
        │             1. BLOCK_DEVICE (Blacklist DEV_c72bd41105eb39dd across gateway)
        │             2. SUSPEND_ALL_ASSOCIATED_CARDS (Alert 52 compromised cards)
        │             3. FILE_SAR (FinCEN reporting for organized crime syndicate)
        │           - Approval Route: L2 (Mandatory L2_FRAUD_MANAGER sign-off)
        │
        ▼
[Case Creation]     case_management/case_repository.py
        │           Saved: cases/HHG-014.json & data/cases/HHG-014.json
        │
        ▼
[Graph Writeback]   case_management/graph_writeback.py (CaseWritebackService)
        │           Destination:
        │           - Vertex appended to: dataset/processed/dynamic_cases.csv
        │           - Edges appended to: dataset/processed/edges_case_involves.csv (Txn 3478561)
        │           - Edges appended to: dataset/processed/edges_case_on_card.csv (Card C13487-K1)
        │
        ▼
[Graph Readback]    case_management/graph_readback.py (CaseReadbackService)
        │           Verification: Status: VERIFIED (Level B)
        │
        ▼
[API Exposure]      api/routes/investigations.py
                    GET /api/investigations/HHG-014 -> Returns full syndicate graph & evidence
```

---

## 4. Stage-by-Stage Lineage Provenance Matrix

| Investigation Stage | Software Component | Data Source in Live Mode (Level A) | Data Source in Current Runtime (Level B) |
|---|---|---|---|
| **Alert Trigger** | `dataset/raw/case_pack.csv` | Challenge CSV input | Challenge CSV input |
| **Agent FSM Orchestration** | `agent/core/orchestrator.py` | In-memory FSM | In-memory FSM |
| **MCP Tool Interface** | `mcp/tools/investigation_mcp_client.py` | pyTigerGraph client | pyTigerGraph client wrapper |
| **Graph Traversal** | TigerGraph Engine vs. Pandas Simulation | TigerGraph RESTPP (:443/9000) | `dataset/processed/*.csv` via Pandas |
| **GSQL Query Logic** | `tigergraph/queries/*.gsql` | Compiled GSQL in database | Emulated in Python methods |
| **Graph Evidence Normalization** | `agent/graph_rag/graph_context_builder.py` | Dynamic evidence items | Dynamic evidence items |
| **GraphRAG Precedent Retrieval**| `agent/graph_rag/case_memory.py` | `ClosedCase` vertices | `dataset/processed/closed_cases.csv` (5,565 rows) |
| **Policy Evaluation** | `agent/policy/policy_rules.py` | Rules R1–R10 document store | Rules R1–R10 document store |
| **Action & Governance** | `agent/policy/next_best_action.py` | Policy Engine | Policy Engine |
| **Dynamic Case Store** | `case_management/case_repository.py` | `data/cases/*.json` | `data/cases/*.json` |
| **Graph Writeback** | `case_management/graph_writeback.py` | TigerGraph upsert query | `dataset/processed/dynamic_cases.csv` + edges |
| **Graph Readback** | `case_management/graph_readback.py` | TigerGraph vertex query | `dataset/processed/dynamic_cases.csv` + edges |
| **REST API Serving** | `api/routes/*.py` | FastAPI services | FastAPI services |
