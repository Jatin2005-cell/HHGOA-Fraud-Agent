# TigerGraph Model Context Protocol (MCP) Integration Layer

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Component:** `mcp`  
**Package:** `pyTigerGraph-mcp` (v1.0.1) / MCP Protocol v2.2.0  
**Status:** Validated (9/9 Tests Passing)

---

## 1. Overview

The `mcp/` directory houses the Model Context Protocol (MCP) integration layer that enables AI agents to query TigerGraph safely and deterministically without bypassing pre-compiled, security-vetted GSQL investigation queries.

### Key Architecture:
- **Server:** Official `tigergraph_mcp` server.
- **Client & Tool Wrapper:** `mcp/tools/investigation_mcp_client.py` enforcing strict regex input validation, bounded pagination, latency tracking, and audit logging.
- **Security:** Strict read-only enforcement (`TG_ALLOWED_TOOLS="query,read-only"`, `TG_BLOCKED_TOOLS="destructive"`).
- **Audit Logging:** Every query is logged with timestamp and sanitized arguments to `mcp/audit.log`.

---

## 2. Directory Layout

```
mcp/
├── README.md                  # This file
├── audit.log                  # Structured JSON audit trail
├── config/
│   └── example.env            # Template environment variables
├── tools/
│   ├── investigation_mcp_client.py # Validated, safe MCP client layer
│   └── tool_mapping.md        # Comprehensive GSQL-to-MCP tool mapping
└── tests/
    ├── mcp_test_plan.md       # Integration test specifications
    ├── run_mcp_tests.py       # Automated test suite
    └── MCP_TEST_REPORT.md     # Test execution report (100% PASS)
```

---

## 3. Quickstart

### 3.1 Configure Environment
Copy `mcp/config/example.env` to `mcp/config/.env` and provide your TigerGraph credentials:
```bash
cp mcp/config/example.env mcp/config/.env
```

### 3.2 Launch Official TigerGraph MCP Server
```powershell
python -m tigergraph_mcp.main --env-file mcp/config/.env
```

### 3.3 Run MCP Test Suite
```powershell
python HHGOA-Fraud-Agent/mcp/tests/run_mcp_tests.py
```
*Expected Result: `MCP TEST SUITE RESULT: PASS (9/9)`*
