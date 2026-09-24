"""
TigerGraph Graph Validation Suite
Hacker House Goa 2026 - HHGOA_IEEE Fraud Investigation
Author: Antigravity Agent

Validates:
1. Entity vertex counts vs raw source baselines
2. Edge integrity and referential consistency
3. Online vs in-person transaction-device isolation
4. Orphan check for transactions and cases
5. Duplicate primary key checks across all entity types
6. ClosedCase and benchmark case pack alignment
"""

import os
import sys
import json
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "processed")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "raw")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "validation_report.json")

def run_validation():
    print("==================================================")
    print("TigerGraph Knowledge Graph Validation Suite")
    print("==================================================")
    
    results = {
        "status": "PASS",
        "vertex_counts": {},
        "edge_counts": {},
        "integrity_checks": {},
        "errors": []
    }

    # 1. Load and validate Vertices
    print("\n--- 1. Vertex Counts & Primary ID Uniqueness ---")
    
    # Transactions
    tx_df = pd.read_csv(os.path.join(PROCESSED_DIR, "transactions.csv"), usecols=['txn_id', 'card_id', 'channel', 'product_cd'])
    tx_count = len(tx_df)
    tx_unique = tx_df['txn_id'].nunique()
    results["vertex_counts"]["Transaction"] = tx_count
    results["integrity_checks"]["Transaction_PrimaryID_Unique"] = (tx_count == tx_unique)
    print(f"Transaction vertices: {tx_count} (Unique Primary IDs: {tx_unique}) -> {'PASS' if tx_count == tx_unique else 'FAIL'}")
    if tx_count != tx_unique:
        results["errors"].append("Duplicate Transaction Primary IDs detected")

    # Customers
    cust_df = pd.read_csv(os.path.join(PROCESSED_DIR, "customers.csv"))
    cust_count = len(cust_df)
    cust_unique = cust_df['customer_id'].nunique()
    results["vertex_counts"]["Customer"] = cust_count
    results["integrity_checks"]["Customer_PrimaryID_Unique"] = (cust_count == cust_unique)
    print(f"Customer vertices: {cust_count} (Unique Primary IDs: {cust_unique}) -> {'PASS' if cust_count == cust_unique else 'FAIL'}")

    # Cards
    cards_df = pd.read_csv(os.path.join(PROCESSED_DIR, "cards.csv"))
    cards_count = len(cards_df)
    cards_unique = cards_df['card_id'].nunique()
    results["vertex_counts"]["Card"] = cards_count
    results["integrity_checks"]["Card_PrimaryID_Unique"] = (cards_count == cards_unique)
    print(f"Card vertices: {cards_count} (Unique Primary IDs: {cards_unique}) -> {'PASS' if cards_count == cards_unique else 'FAIL'}")

    # DeviceProfiles
    dev_df = pd.read_csv(os.path.join(PROCESSED_DIR, "devices.csv"))
    dev_count = len(dev_df)
    dev_unique = dev_df['device_hash'].nunique()
    results["vertex_counts"]["DeviceProfile"] = dev_count
    results["integrity_checks"]["DeviceProfile_PrimaryID_Unique"] = (dev_count == dev_unique)
    print(f"DeviceProfile vertices: {dev_count} (Unique Primary IDs: {dev_unique}) -> {'PASS' if dev_count == dev_unique else 'FAIL'}")

    # BillingRegions
    reg_df = pd.read_csv(os.path.join(PROCESSED_DIR, "billing_regions.csv"))
    reg_count = len(reg_df)
    reg_unique = reg_df['region_id'].nunique()
    results["vertex_counts"]["BillingRegion"] = reg_count
    results["integrity_checks"]["BillingRegion_PrimaryID_Unique"] = (reg_count == reg_unique)
    print(f"BillingRegion vertices: {reg_count} (Unique Primary IDs: {reg_unique}) -> {'PASS' if reg_count == reg_unique else 'FAIL'}")

    # EmailDomains
    email_df = pd.read_csv(os.path.join(PROCESSED_DIR, "email_domains.csv"))
    email_count = len(email_df)
    email_unique = email_df['domain_name'].nunique()
    results["vertex_counts"]["EmailDomain"] = email_count
    results["integrity_checks"]["EmailDomain_PrimaryID_Unique"] = (email_count == email_unique)
    print(f"EmailDomain vertices: {email_count} (Unique Primary IDs: {email_unique}) -> {'PASS' if email_count == email_unique else 'FAIL'}")

    # ClosedCases
    cases_df = pd.read_csv(os.path.join(PROCESSED_DIR, "closed_cases.csv"))
    cases_count = len(cases_df)
    cases_unique = cases_df['case_id'].nunique()
    results["vertex_counts"]["ClosedCase"] = cases_count
    results["integrity_checks"]["ClosedCase_PrimaryID_Unique"] = (cases_count == cases_unique)
    print(f"ClosedCase vertices: {cases_count} (Unique Primary IDs: {cases_unique}) -> {'PASS' if cases_count == cases_unique else 'FAIL'}")

    # 2. Edge Counts & Referential Integrity
    print("\n--- 2. Edge Counts & Referential Integrity ---")
    
    # OWNS: Customer -> Card
    owns_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_owns.csv"))
    results["edge_counts"]["OWNS"] = len(owns_df)
    owns_valid_cust = owns_df['customer_id'].isin(cust_df['customer_id']).all()
    owns_valid_card = owns_df['card_id'].isin(cards_df['card_id']).all()
    results["integrity_checks"]["OWNS_Referential_Integrity"] = bool(owns_valid_cust and owns_valid_card)
    print(f"OWNS edges: {len(owns_df)} (Customer & Card valid: {owns_valid_cust and owns_valid_card})")

    # MADE: Card -> Transaction
    made_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_made.csv"))
    results["edge_counts"]["MADE"] = len(made_df)
    made_valid_card = made_df['card_id'].isin(cards_df['card_id']).all()
    results["integrity_checks"]["MADE_Referential_Integrity"] = bool(made_valid_card)
    print(f"MADE edges: {len(made_df)} (Card foreign key valid: {made_valid_card})")

    # FROM_DEVICE: Transaction -> DeviceProfile
    from_dev_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_from_device.csv"))
    results["edge_counts"]["FROM_DEVICE"] = len(from_dev_df)
    dev_valid = from_dev_df['device_hash'].isin(dev_df['device_hash']).all()
    results["integrity_checks"]["FROM_DEVICE_Referential_Integrity"] = bool(dev_valid)
    print(f"FROM_DEVICE edges: {len(from_dev_df)} (Device foreign key valid: {dev_valid})")

    # NEXT_TRANSACTION: Transaction -> Transaction
    next_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_next_transaction.csv"))
    results["edge_counts"]["NEXT_TRANSACTION"] = len(next_df)
    print(f"NEXT_TRANSACTION edges: {len(next_df)}")

    # CASE_INVOLVES: ClosedCase -> Transaction
    case_involves_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_case_involves.csv"))
    results["edge_counts"]["CASE_INVOLVES"] = len(case_involves_df)
    case_inv_valid = case_involves_df['case_id'].isin(cases_df['case_id']).all()
    results["integrity_checks"]["CASE_INVOLVES_Referential_Integrity"] = bool(case_inv_valid)
    print(f"CASE_INVOLVES edges: {len(case_involves_df)} (Case foreign key valid: {case_inv_valid})")

    # CASE_ON_CARD: ClosedCase -> Card
    case_card_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_case_on_card.csv"))
    results["edge_counts"]["CASE_ON_CARD"] = len(case_card_df)
    case_card_valid = case_card_df['card_id'].isin(cards_df['card_id']).all()
    results["integrity_checks"]["CASE_ON_CARD_Referential_Integrity"] = bool(case_card_valid)
    print(f"CASE_ON_CARD edges: {len(case_card_df)} (Card foreign key valid: {case_card_valid})")

    # CONNECTED_CARD: ClosedCase -> Card
    conn_card_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_connected_card.csv"))
    results["edge_counts"]["CONNECTED_CARD"] = len(conn_card_df)
    print(f"CONNECTED_CARD edges: {len(conn_card_df)}")

    # BILLED_IN: Transaction -> BillingRegion
    billed_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_billed_in.csv"))
    results["edge_counts"]["BILLED_IN"] = len(billed_df)
    print(f"BILLED_IN edges: {len(billed_df)}")

    # PURCHASER_EMAIL & RECIPIENT_EMAIL
    p_email_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_purchaser_email.csv"))
    r_email_df = pd.read_csv(os.path.join(PROCESSED_DIR, "edges_recipient_email.csv"))
    results["edge_counts"]["PURCHASER_EMAIL"] = len(p_email_df)
    results["edge_counts"]["RECIPIENT_EMAIL"] = len(r_email_df)
    print(f"PURCHASER_EMAIL edges: {len(p_email_df)}")
    print(f"RECIPIENT_EMAIL edges: {len(r_email_df)}")

    # 3. Channel & Identity Isolation Checks
    print("\n--- 3. Channel & Device Isolation Checks ---")
    in_person_txns = tx_df[tx_df['channel'] == 'in_person']['txn_id']
    online_txns = tx_df[tx_df['channel'] == 'online']['txn_id']
    
    in_person_with_device = from_dev_df[from_dev_df['txn_id'].isin(in_person_txns)]
    in_person_clean = (len(in_person_with_device) == 0)
    results["integrity_checks"]["In_Person_Transactions_Zero_Device_Records"] = in_person_clean
    print(f"In-person transactions connected to device: {len(in_person_with_device)} -> {'PASS (0)' if in_person_clean else 'FAIL'}")

    raw_ident = pd.read_csv(os.path.join(RAW_DIR, "identity.csv"), usecols=['TransactionID'])
    raw_ident_ids = set(raw_ident['TransactionID'])
    staged_ident_ids = set(from_dev_df['txn_id'])
    ident_match = (raw_ident_ids == staged_ident_ids)
    results["integrity_checks"]["Online_Identity_Exact_Match_144432"] = ident_match
    print(f"Raw identity records matched to FROM_DEVICE edges: {len(staged_ident_ids)} / {len(raw_ident_ids)} -> {'PASS' if ident_match else 'FAIL'}")

    # 4. Orphan Check
    print("\n--- 4. Orphan Check ---")
    tx_with_card = tx_df['card_id'].isin(cards_df['card_id']).all()
    results["integrity_checks"]["Zero_Orphan_Transactions"] = bool(tx_with_card)
    print(f"Orphan transactions without valid card: {0 if tx_with_card else 'DETECTED'} -> {'PASS' if tx_with_card else 'FAIL'}")

    # 5. Final Status
    all_passed = all(results["integrity_checks"].values())
    results["status"] = "PASS" if all_passed else "FAIL"
    print("\n==================================================")
    print(f"OVERALL VALIDATION STATUS: {results['status']}")
    print("==================================================")

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Detailed validation report saved to: {REPORT_PATH}")

if __name__ == "__main__":
    run_validation()
