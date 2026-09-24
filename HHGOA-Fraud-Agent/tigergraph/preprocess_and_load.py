"""
TigerGraph Preprocessing and Staging Pipeline
Hacker House Goa 2026 - HHGOA_IEEE Fraud Investigation
Author: Antigravity Agent

Processes:
- dataset/raw/transactions.csv
- dataset/raw/identity.csv
- dataset/raw/closed_cases_history.csv
- dataset/raw/case_pack.csv (for reference and benchmark isolation)

Outputs staging files into dataset/processed/ without modifying raw data.
"""

import os
import sys
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

print("==================================================")
print("1. Loading Reference Cases and Ground Truth")
print("==================================================")

closed_cases_path = os.path.join(RAW_DIR, "closed_cases_history.csv")
case_pack_path = os.path.join(RAW_DIR, "case_pack.csv")

closed_cases_df = pd.read_csv(closed_cases_path)
case_pack_df = pd.read_csv(case_pack_path)

print(f"Loaded {len(closed_cases_df)} closed cases.")
print(f"Loaded {len(case_pack_df)} benchmark cases.")

# Build ground truth transaction -> card mapping from cases
# Format: txn_id -> card_id
gt_txn_to_card = {}
for _, r in closed_cases_df.iterrows():
    cid = r['customer_id']
    card = r['card_id']
    txns = str(r['txn_ids']).split('|')
    for tid in txns:
        if tid and tid.strip().isdigit():
            gt_txn_to_card[int(tid.strip())] = (cid, card)

for _, r in case_pack_df.iterrows():
    if pd.notnull(r['flagged_txn_id']):
        gt_txn_to_card[int(r['flagged_txn_id'])] = (r['customer_id'], r['card_id'])

print(f"Mapped {len(gt_txn_to_card)} transactions directly to ground-truth card identities.")

print("\n==================================================")
print("2. Processing Identity Records & Device Profiles")
print("==================================================")

identity_path = os.path.join(RAW_DIR, "identity.csv")
ident_df = pd.read_csv(identity_path)
print(f"Loaded {len(ident_df)} identity records.")

def generate_device_hash(row):
    d_info = str(row['DeviceInfo']).strip() if pd.notnull(row['DeviceInfo']) else ''
    os_val = str(row['id_30']).strip() if pd.notnull(row['id_30']) else ''
    browser = str(row['id_31']).strip() if pd.notnull(row['id_31']) else ''
    screen = str(row['id_33']).strip() if pd.notnull(row['id_33']) else ''
    raw_str = f"{d_info}|{os_val}|{browser}|{screen}"
    return "DEV_" + hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:16]

ident_df['device_hash'] = ident_df.apply(generate_device_hash, axis=1)

# Group unique device profiles
devices_df = ident_df[['device_hash', 'DeviceInfo', 'DeviceType', 'id_30', 'id_31', 'id_33', 'id_23', 'id_15']].drop_duplicates(subset=['device_hash']).copy()
devices_df.columns = ['device_hash', 'device_info', 'device_type', 'os', 'browser', 'screen_res', 'proxy_status', 'device_status']
devices_df.fillna('', inplace=True)

devices_csv = os.path.join(PROCESSED_DIR, "devices.csv")
devices_df.to_csv(devices_csv, index=False)
print(f"Wrote {len(devices_df)} unique DeviceProfile vertices to {devices_csv}")

# Map TransactionID -> Device metadata for fast lookup
txn_to_device = dict(zip(ident_df['TransactionID'], ident_df['device_hash']))
txn_to_id15 = dict(zip(ident_df['TransactionID'], ident_df['id_15'].fillna('')))
txn_to_id23 = dict(zip(ident_df['TransactionID'], ident_df['id_23'].fillna('')))
txn_to_id34 = dict(zip(ident_df['TransactionID'], ident_df['id_34'].fillna('')))

print("\n==================================================")
print("3. Card Identity Derivation & Mapping Discovery")
print("==================================================")

# First pass over transactions: map (customer_id, card1..card6) -> card_id
transactions_path = os.path.join(RAW_DIR, "transactions.csv")

# We collect all distinct card tuples per customer and record first appearance ts
print("Reading transactions to resolve card tuples...")
chunk_size = 100000
chunks = pd.read_csv(transactions_path, chunksize=chunk_size,
                     usecols=['TransactionID', 'customer_id', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6', 'ts'])

cust_card_tuples = {} # cust -> dict of tuple -> {'min_ts': ..., 'card_id': ...}
txn_card_map = {}

for chunk in chunks:
    for _, row in chunk.iterrows():
        tid = row['TransactionID']
        cust = row['customer_id']
        tup = (row['card1'], row['card2'], row['card3'], row['card4'], row['card5'], row['card6'])
        ts_val = row['ts']

        if cust not in cust_card_tuples:
            cust_card_tuples[cust] = {}

        if tup not in cust_card_tuples[cust]:
            cust_card_tuples[cust][tup] = {'min_ts': ts_val, 'card_id': None}
        else:
            if ts_val < cust_card_tuples[cust][tup]['min_ts']:
                cust_card_tuples[cust][tup]['min_ts'] = ts_val

        # If this transaction is in ground truth, attach the card_id
        if tid in gt_txn_to_card:
            _, assigned_card = gt_txn_to_card[tid]
            cust_card_tuples[cust][tup]['card_id'] = assigned_card

# Second pass: resolve any unassigned card tuples deterministically
# For each customer, check assigned suffixes ('K1', 'K2', etc.)
# Then assign lowest available suffix sorted by min_ts
all_cards_records = [] # for cards.csv
tuple_to_card_resolved = {}

for cust, t_dict in cust_card_tuples.items():
    assigned_suffixes = set()
    for tup, info in t_dict.items():
        if info['card_id'] is not None:
            suffix = info['card_id'].split('-')[-1]
            assigned_suffixes.add(suffix)

    # Sort remaining unassigned tuples by min_ts
    unassigned = [tup for tup, info in t_dict.items() if info['card_id'] is None]
    unassigned.sort(key=lambda t: t_dict[t]['min_ts'])

    k_idx = 1
    for tup in unassigned:
        while f"K{k_idx}" in assigned_suffixes:
            k_idx += 1
        card_id = f"{cust}-K{k_idx}"
        assigned_suffixes.add(f"K{k_idx}")
        t_dict[tup]['card_id'] = card_id
        k_idx += 1

    # Record cards
    for tup, info in t_dict.items():
        card_id = info['card_id']
        tuple_to_card_resolved[(cust, tup)] = card_id
        all_cards_records.append({
            'card_id': card_id,
            'customer_id': cust,
            'card1': tup[0],
            'card2': tup[1],
            'card3': tup[2],
            'card4': tup[3],
            'card5': tup[4],
            'card6': tup[5],
            'min_ts': info['min_ts'],
            'status': 'active'
        })

cards_df = pd.DataFrame(all_cards_records).drop_duplicates(subset=['card_id']).copy()
cards_csv = os.path.join(PROCESSED_DIR, "cards.csv")
cards_df.to_csv(cards_csv, index=False)
print(f"Wrote {len(cards_df)} unique Card vertices to {cards_csv}")

# Customers vertices
cust_counts = cards_df.groupby('customer_id')['card_id'].count().to_dict()
customers_df = pd.DataFrame([
    {'customer_id': cid, 'total_cards': cnt}
    for cid, cnt in cust_counts.items()
])
customers_csv = os.path.join(PROCESSED_DIR, "customers.csv")
customers_df.to_csv(customers_csv, index=False)
print(f"Wrote {len(customers_df)} Customer vertices to {customers_csv}")

print("\n==================================================")
print("4. Staging Transactions & Edges")
print("==================================================")

tx_cols = [
    'TransactionID', 'customer_id', 'TransactionAmt', 'ProductCD', 'channel',
    'risk_score', 'addr1', 'addr2', 'dist1', 'dist2', 'P_emaildomain',
    'R_emaildomain', 'ts', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6',
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9'
]

chunks = pd.read_csv(transactions_path, chunksize=chunk_size, usecols=tx_cols)

tx_out_path = os.path.join(PROCESSED_DIR, "transactions.csv")
edges_owns_path = os.path.join(PROCESSED_DIR, "edges_owns.csv")
edges_made_path = os.path.join(PROCESSED_DIR, "edges_made.csv")
edges_from_device_path = os.path.join(PROCESSED_DIR, "edges_from_device.csv")
edges_billed_in_path = os.path.join(PROCESSED_DIR, "edges_billed_in.csv")
edges_p_email_path = os.path.join(PROCESSED_DIR, "edges_purchaser_email.csv")
edges_r_email_path = os.path.join(PROCESSED_DIR, "edges_recipient_email.csv")

# Create edge files with headers
with open(edges_owns_path, 'w', encoding='utf-8') as f:
    f.write("customer_id,card_id,is_primary\n")
with open(edges_made_path, 'w', encoding='utf-8') as f:
    f.write("card_id,txn_id,ts\n")
with open(edges_from_device_path, 'w', encoding='utf-8') as f:
    f.write("txn_id,device_hash,id_15_status,id_23_proxy,match_status\n")
with open(edges_billed_in_path, 'w', encoding='utf-8') as f:
    f.write("txn_id,region_id,dist1\n")
with open(edges_p_email_path, 'w', encoding='utf-8') as f:
    f.write("txn_id,domain_name\n")
with open(edges_r_email_path, 'w', encoding='utf-8') as f:
    f.write("txn_id,domain_name\n")

# Process OWNS edges once from cards_df
owns_records = []
for _, r in cards_df.iterrows():
    cid = r['customer_id']
    card_id = r['card_id']
    is_primary = (card_id.endswith('-K1'))
    owns_records.append(f"{cid},{card_id},{is_primary}\n")

with open(edges_owns_path, 'a', encoding='utf-8') as f:
    f.writelines(owns_records)

# Process transactions in chunks
total_txns = 0
unique_regions = set()
unique_domains = set()

# Temporary storage for NEXT_TRANSACTION calculation (card_id -> list of (txn_id, ts, amount, region))
card_txn_chains = {}

first_chunk = True
for chunk in chunks:
    clean_txns = []
    made_lines = []
    device_lines = []
    billed_lines = []
    p_email_lines = []
    r_email_lines = []

    for _, row in chunk.iterrows():
        tid = row['TransactionID']
        cust = row['customer_id']
        tup = (row['card1'], row['card2'], row['card3'], row['card4'], row['card5'], row['card6'])
        card_id = tuple_to_card_resolved.get((cust, tup), f"{cust}-K1")
        ts_val = row['ts']
        amt = row['TransactionAmt']
        prod = row['ProductCD']
        chan = row['channel']
        rscore = row['risk_score'] if pd.notnull(row['risk_score']) else 0.0
        a1 = row['addr1'] if pd.notnull(row['addr1']) else ''
        a2 = row['addr2'] if pd.notnull(row['addr2']) else ''
        d1 = row['dist1'] if pd.notnull(row['dist1']) else ''
        d2 = row['dist2'] if pd.notnull(row['dist2']) else ''
        p_email = str(row['P_emaildomain']).strip() if pd.notnull(row['P_emaildomain']) else ''
        r_email = str(row['R_emaildomain']).strip() if pd.notnull(row['R_emaildomain']) else ''

        # Combine M1-M9 into condensed flag string
        m_flags = "_".join([str(row[f'M{i}']) if pd.notnull(row[f'M{i}']) else 'NA' for i in range(1, 10)])

        reg_id = f"REG_{a1}" if a1 != '' else ''

        clean_txns.append({
            'txn_id': tid,
            'card_id': card_id,
            'ts': ts_val,
            'amount': amt,
            'product_cd': prod,
            'channel': chan,
            'risk_score': rscore,
            'addr1': a1,
            'addr2': a2,
            'dist1': d1,
            'dist2': d2,
            'p_emaildomain': p_email,
            'r_emaildomain': r_email,
            'm_flags': m_flags
        })

        made_lines.append(f"{card_id},{tid},{ts_val}\n")

        if tid in txn_to_device:
            dev_hash = txn_to_device[tid]
            id15 = txn_to_id15.get(tid, '')
            id23 = txn_to_id23.get(tid, '')
            id34 = txn_to_id34.get(tid, '')
            device_lines.append(f"{tid},{dev_hash},{id15},{id23},{id34}\n")

        if reg_id:
            unique_regions.add((reg_id, a1, a2))
            billed_lines.append(f"{tid},{reg_id},{d1}\n")

        if p_email:
            unique_domains.add(p_email)
            p_email_lines.append(f"{tid},{p_email}\n")

        if r_email:
            unique_domains.add(r_email)
            r_email_lines.append(f"{tid},{r_email}\n")

        # Collect for temporal sequence
        if card_id not in card_txn_chains:
            card_txn_chains[card_id] = []
        card_txn_chains[card_id].append((tid, ts_val, amt, a1))

    # Append to files
    pd.DataFrame(clean_txns).to_csv(tx_out_path, mode='w' if first_chunk else 'a', index=False, header=first_chunk)
    first_chunk = False

    with open(edges_made_path, 'a', encoding='utf-8') as f:
        f.writelines(made_lines)
    with open(edges_from_device_path, 'a', encoding='utf-8') as f:
        f.writelines(device_lines)
    with open(edges_billed_in_path, 'a', encoding='utf-8') as f:
        f.writelines(billed_lines)
    with open(edges_p_email_path, 'a', encoding='utf-8') as f:
        f.writelines(p_email_lines)
    with open(edges_r_email_path, 'a', encoding='utf-8') as f:
        f.writelines(r_email_lines)

    total_txns += len(clean_txns)
    print(f"Processed {total_txns} transactions...")

print(f"Completed transaction staging: {total_txns} transactions.")

# Save Billing Regions and Email Domains
regions_dict = {}
for r in unique_regions:
    rid, a1, a2 = r
    if rid not in regions_dict:
        regions_dict[rid] = {'region_id': rid, 'region_code': a1, 'country_code': a2}

regions_df = pd.DataFrame(list(regions_dict.values()))
regions_csv = os.path.join(PROCESSED_DIR, "billing_regions.csv")
regions_df.to_csv(regions_csv, index=False)
print(f"Wrote {len(regions_df)} unique BillingRegion vertices.")

email_df = pd.DataFrame([
    {'domain_name': d, 'is_disposable': (d in ['anonymous.com', 'tempmail.com', 'mailinator.com'])}
    for d in unique_domains
])
email_csv = os.path.join(PROCESSED_DIR, "email_domains.csv")
email_df.to_csv(email_csv, index=False)
print(f"Wrote {len(email_df)} EmailDomain vertices.")

print("\n==================================================")
print("5. Generating NEXT_TRANSACTION Temporal Edges")
print("==================================================")

edges_next_path = os.path.join(PROCESSED_DIR, "edges_next_transaction.csv")
next_lines = []
total_next_edges = 0

with open(edges_next_path, 'w', encoding='utf-8') as f:
    f.write("from_txn_id,to_txn_id,delta_seconds,delta_amount,same_region\n")

    for card_id, t_list in card_txn_chains.items():
        if len(t_list) < 2:
            continue
        # Sort by timestamp
        t_list.sort(key=lambda x: x[1])
        card_next_lines = []
        for i in range(len(t_list) - 1):
            t1 = t_list[i]
            t2 = t_list[i+1]
            dt1 = datetime.strptime(t1[1], "%Y-%m-%d %H:%M:%S")
            dt2 = datetime.strptime(t2[1], "%Y-%m-%d %H:%M:%S")
            delta_sec = int((dt2 - dt1).total_seconds())
            delta_amt = round(float(t2[2]) - float(t1[2]), 2)
            same_reg = (t1[3] == t2[3] and t1[3] != '')
            card_next_lines.append(f"{t1[0]},{t2[0]},{delta_sec},{delta_amt},{same_reg}\n")
        f.writelines(card_next_lines)
        total_next_edges += len(card_next_lines)

print(f"Wrote {total_next_edges} NEXT_TRANSACTION edges to {edges_next_path}.")

print("\n==================================================")
print("6. Staging Historical Closed Cases & Case Edges")
print("==================================================")

clean_cases = []
edges_case_txn = []
edges_case_card = []
edges_connected_card = []

for _, row in closed_cases_df.iterrows():
    cid = row['case_id']
    cust = row['customer_id']
    card = row['card_id']
    op_at = row['opened_at']
    cl_at = row['closed_at']
    outc = row['outcome']
    pat = row['pattern'] if pd.notnull(row['pattern']) else 'none'
    first_txn = str(row['first_fraud_txn_id']).strip() if pd.notnull(row['first_fraud_txn_id']) else ''
    ntx = row['n_txns']
    exp = row['exposure_usd']
    act = row['actions_taken'] if pd.notnull(row['actions_taken']) else ''
    rep = row['report_filed'] if pd.notnull(row['report_filed']) else 'No'
    notes = str(row['analyst_notes']).replace('"', '""') if pd.notnull(row['analyst_notes']) else ''

    clean_cases.append({
        'case_id': cid,
        'customer_id': cust,
        'card_id': card,
        'opened_at': op_at,
        'closed_at': cl_at,
        'outcome': outc,
        'pattern': pat,
        'first_fraud_txn_id': first_txn,
        'n_txns': ntx,
        'exposure_usd': exp,
        'actions_taken': act,
        'report_filed': rep,
        'analyst_notes': f'"{notes}"'
    })

    # Case on Card edge
    edges_case_card.append(f"{cid},{card}\n")

    # Case involves Transaction edges
    if pd.notnull(row['txn_ids']):
        tids = str(row['txn_ids']).split('|')
        for t in tids:
            t = t.strip()
            if t.isdigit():
                is_first = (t == first_txn)
                edges_case_txn.append(f"{cid},{t},{is_first},False\n")

    # Connected Cards edges
    if pd.notnull(row['connected_card_ids']):
        conn_cards = str(row['connected_card_ids']).split('|')
        for c in conn_cards:
            c = c.strip()
            if c:
                edges_connected_card.append(f"{cid},{c},shared_syndicate\n")

cases_csv = os.path.join(PROCESSED_DIR, "closed_cases.csv")
pd.DataFrame(clean_cases).to_csv(cases_csv, index=False)
print(f"Wrote {len(clean_cases)} ClosedCase vertices to {cases_csv}.")

edges_case_txn_path = os.path.join(PROCESSED_DIR, "edges_case_involves.csv")
with open(edges_case_txn_path, 'w', encoding='utf-8') as f:
    f.write("case_id,txn_id,is_first_fraud,is_flagged_trigger\n")
    f.writelines(edges_case_txn)
print(f"Wrote {len(edges_case_txn)} CASE_INVOLVES edges.")

edges_case_card_path = os.path.join(PROCESSED_DIR, "edges_case_on_card.csv")
with open(edges_case_card_path, 'w', encoding='utf-8') as f:
    f.write("case_id,card_id\n")
    f.writelines(edges_case_card)
print(f"Wrote {len(edges_case_card)} CASE_ON_CARD edges.")

edges_connected_card_path = os.path.join(PROCESSED_DIR, "edges_connected_card.csv")
with open(edges_connected_card_path, 'w', encoding='utf-8') as f:
    f.write("case_id,card_id,connection_reason\n")
    f.writelines(edges_connected_card)
print(f"Wrote {len(edges_connected_card)} CONNECTED_CARD edges.")

print("\n==================================================")
print("Pipeline Completed Successfully!")
print("==================================================")
