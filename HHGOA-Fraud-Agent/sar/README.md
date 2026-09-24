# Suspicious Activity Report (SAR) Generation & Validation Engine

**Project:** HHGOA_IEEE TigerGraph Agentic Fraud Investigation  
**Component:** `sar/`  
**Phase:** Phase 6  

---

## 1. Overview

The `sar/` module generates and validates regulatory Suspicious Activity Reports pursuant to FinCEN standards and Bank Fraud Policy v1.0.

### Standards & Constraints:
1. **Evidence-Grounded Only:** Narratives are constructed strictly from verified graph entities (Customer, Card, Transaction, DeviceProfile, BillingRegion). Zero hallucinated accounts, amounts, or external identities.
2. **Policy Thresholds:** Reports are generated ONLY when mandated by Policy R2/R6/R9 or when unauthorized exposure reaches $\ge \$1,000$. Legitimate and low-exposure cases yield `file: false`.
3. **Standalone Completeness:** The narrative independently explains who, what, when, where, how, and why the activity is suspicious.
4. **Hackathon Scope:** No live submissions are dispatched to regulatory authorities.
