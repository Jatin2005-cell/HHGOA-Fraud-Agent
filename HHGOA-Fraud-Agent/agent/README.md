# AI Agent + GraphRAG + Investigation Orchestrator

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Component:** `agent/`  
**Phase:** Phase 5  

---

## 1. Architecture Overview

The autonomous agent executes an explicit 17-state finite state machine orchestrating TigerGraph MCP tool calls, GraphRAG memory retrieval, evidence evaluation, policy validation, and FinCEN SAR generation:

```
Trigger
   ↓
Agent Investigation State Machine
   ↓
TigerGraph MCP Tools (Phase 4 Adapter)
   ↓
Graph Evidence Extraction
   ↓
GraphRAG / Historical Case Memory Retrieval
   ↓
Risk + Fraud Pattern Assessment
   ↓
Uncertainty Assessment
   ↓
Need More Evidence?
   ├── YES → Customer / Analyst Verification Request → Reassess
   └── NO
          ↓
Initial & Final Next Best Actions
          ↓
Deterministic Policy Engine (R1 - R10)
          ↓
Approval Routing (auto / L1 / L2)
          ↓
Case Summary & SAR Generation
          ↓
Graph Memory Update (DynamicCase)
          ↓
Final 3-Part JSON Answer (case, sar, next_best_actions)
```

---

## 2. Directory Layout

```
agent/
├── README.md
├── config/
│   └── example.env
├── core/
│   ├── investigation_agent.py
│   ├── investigation_state.py
│   ├── investigation_orchestrator.py
│   ├── tool_selector.py
│   ├── evidence_manager.py
│   ├── uncertainty_manager.py
│   ├── evidence_requester.py
│   ├── stop_manager.py
│   └── explanation_builder.py
├── graph_rag/
│   ├── retriever.py
│   ├── graph_context_builder.py
│   ├── case_memory.py
│   ├── evidence_ranker.py
│   └── document_store.py
├── policy/
│   ├── policy_engine.py
│   ├── action_validator.py
│   ├── approval_router.py
│   └── policy_rules.py
├── tools/
│   ├── mcp_tools.py
│   └── tool_registry.py
├── schemas/
│   ├── investigation_schema.py
│   ├── evidence_schema.py
│   ├── action_schema.py
│   └── agent_output_schema.py
├── prompts/
│   ├── system_prompt.md
│   ├── investigation_prompt.md
│   ├── evidence_prompt.md
│   └── explanation_prompt.md
├── evaluation/
│   ├── benchmark_runner.py
│   ├── benchmark_cases.py
│   ├── evaluation_metrics.py
│   └── evaluation_report.py
└── tests/
    ├── test_state_machine.py
    ├── test_tool_selection.py
    ├── test_policy_engine.py
    ├── test_graph_rag.py
    ├── test_stop_conditions.py
    └── test_agent_integration.py
```
