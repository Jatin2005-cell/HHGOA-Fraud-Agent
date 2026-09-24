"""Graph Context Builder for GraphRAG.

Compresses raw graph traversals into a compact, LLM-ready investigation context
with structured entities, relationships, and provenanced claims.
"""

from typing import Any, Dict, List, Tuple
from agent.schemas.evidence_schema import EvidenceItem, EvidenceSourceEnum


class GraphContextBuilder:
    """Builds normalized graph evidence packets from MCP query outputs."""

    @classmethod
    def process_mcp_output(
        cls, tool_name: str, raw_output: Dict[str, Any], query_params: Dict[str, Any]
    ) -> Tuple[List[EvidenceItem], Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extracts factual claims, entities, and relationships from tool results.
        Returns:
            Tuple of (evidence_items, entities_dict, relationships_list)
        """
        evidence_items: List[EvidenceItem] = []
        entities: Dict[str, Any] = {}
        relationships: List[Dict[str, Any]] = []

        res = raw_output.get("results", {}) if isinstance(raw_output, dict) else raw_output
        if not isinstance(res, dict):
            return evidence_items, entities, relationships

        if tool_name == "get_transaction_context":
            txns = res.get("target_transaction", [])
            if txns:
                tx = txns[0]
                tid = str(tx.get("txn_id"))
                entities["target_transaction"] = tx
                cid = tx.get("card_id", "")
                cust = tx.get("customer_id") or (cid.split("-")[0] if "-" in cid else "")
                amt = float(tx.get("amount", 0.0))
                channel = tx.get("channel", "online")
                reg = tx.get("billing_region") or str(tx.get("addr1", ""))

                reg_str = f" in billing region {reg}" if reg and reg != "nan" else ""
                claim_text = (
                    f"Transaction {tid} amount ${amt:.2f} executed via {channel} channel on card {cid} "
                    f"for customer {cust}{reg_str}."
                )
                evidence_items.append(
                    EvidenceItem(
                        claim=claim_text,
                        source=EvidenceSourceEnum.GRAPH,
                        ref="query:transaction_investigation_query",
                        entity_ids=[tid, cid, cust],
                    )
                )

            # Devices
            devices = res.get("device_profile", [])
            if devices:
                dev = devices[0]
                dhash = dev.get("device_hash", "")
                entities["device_profile"] = dev
                dev_desc = f"{dev.get('device_info', '')} | {dev.get('os', '')} | {dev.get('browser', '')} | {dev.get('screen', '')}"
                evidence_items.append(
                    EvidenceItem(
                        claim=f"Online transaction operated from device profile {dhash} ({dev_desc}).",
                        source=EvidenceSourceEnum.GRAPH,
                        ref="query:transaction_investigation_query",
                        entity_ids=[dhash],
                    )
                )

            # Direct Case Links
            cases = res.get("connected_cases", [])
            if cases:
                entities["connected_cases"] = cases
                evidence_items.append(
                    EvidenceItem(
                        claim=f"Transaction directly linked to historical closed case records: {', '.join(cases)}.",
                        source=EvidenceSourceEnum.GRAPH,
                        ref="query:transaction_investigation_query",
                        entity_ids=cases,
                    )
                )

        elif tool_name == "get_card_transaction_window":
            cid = res.get("card_id", "")
            cnt = res.get("window_txn_count", 0)
            tot_amt = res.get("window_total_amount", 0.0)
            small_auths = res.get("sub_5_dollar_auth_count", 0)
            max_amt = res.get("max_txn_amount", 0.0)
            testing = res.get("card_testing_sequence_detected", False)

            claim_text = (
                f"Card {cid} 24-hour window: {cnt} transactions totaling ${tot_amt:.2f}. "
                f"{small_auths} sub-$5 online micro-authorizations observed, with peak single amount ${max_amt:.2f}."
            )
            if testing:
                claim_text += " Characteristic card-testing pattern (multiple sub-$5 authorizations preceding larger purchase) identified."

            evidence_items.append(
                EvidenceItem(
                    claim=claim_text,
                    source=EvidenceSourceEnum.GRAPH,
                    ref=f"query:card_window_query(card_id={cid})",
                    entity_ids=[cid],
                )
            )

        elif tool_name == "find_device_neighbors":
            dhash = res.get("device_hash", "")
            if dhash:
                cards_cnt = res.get("connected_cards_count", 0)
                txns_cnt = res.get("connected_transactions_count", 0)
                cases = res.get("linked_closed_cases", [])
                entities["device_syndicate"] = res

                claim_text = (
                    f"Device {dhash} is shared across {cards_cnt} distinct cards and {txns_cnt} transactions."
                )
                if cases:
                    claim_text += f" Connected to prior confirmed fraud cases: {', '.join(cases)}."
                evidence_items.append(
                    EvidenceItem(
                        claim=claim_text,
                        source=EvidenceSourceEnum.GRAPH,
                        ref="query:device_neighbors_query",
                        entity_ids=[dhash] + cases,
                    )
                )

        elif tool_name == "find_region_anomalies":
            cid = res.get("card_id", "")
            is_new = res.get("is_new_billing_region", False)
            p_cnt = res.get("flagged_region_prior_count", 0)
            t_cnt = res.get("total_in_person_history_count", 0)
            reg = res.get("flagged_region", "")

            claim_text = (
                f"Card {cid} in-person history shows {t_cnt} transactions across home regions. "
                f"Flagged region {reg} has {p_cnt} prior occurrences."
            )
            if is_new:
                claim_text += " Flagged transaction is in a completely novel billing region for this cardholder."
            evidence_items.append(
                EvidenceItem(
                    claim=claim_text,
                    source=EvidenceSourceEnum.GRAPH,
                    ref=f"query:region_anomaly_query(card_id={cid})",
                    entity_ids=[cid],
                )
            )

        elif tool_name == "get_customer_history":
            cust = res.get("customer_id") or query_params.get("customer_id", "")
            cards = res.get("cards", [])
            tot_tx = res.get("total_transaction_count", 0)
            tot_spend = res.get("total_spend", 0.0)
            avg_amt = res.get("avg_amount", 0.0)

            cards_str = f" ({', '.join(cards)})" if cards else ""
            claim_text = (
                f"Customer {cust} holds {len(cards)} card(s){cards_str}. "
                f"Historical baseline: {tot_tx} lifetime transactions totaling ${tot_spend:.2f} (average ${avg_amt:.2f}/txn)."
            )
            evidence_items.append(
                EvidenceItem(
                    claim=claim_text,
                    source=EvidenceSourceEnum.GRAPH,
                    ref=f"query:customer_history_query(customer={cust})",
                    entity_ids=[cust] + cards,
                )
            )

        elif tool_name == "find_connected_cards":
            cid = res.get("target_card", "")
            other_cards = res.get("same_customer_cards", [])
            if other_cards:
                claim_text = f"Card {cid} shares account ownership with {len(other_cards)} other card(s): {', '.join(other_cards)}."
                evidence_items.append(
                    EvidenceItem(
                        claim=claim_text,
                        source=EvidenceSourceEnum.GRAPH,
                        ref="query:connected_cards_query",
                        entity_ids=[cid] + other_cards,
                    )
                )

        elif tool_name == "analyze_temporal_pattern":
            chain_len = res.get("chain_length", 0)
            hops = res.get("hops", [])
            if chain_len > 0:
                short_hops = [h for h in hops if h.get("delta_seconds", 0) < 600]
                claim_text = f"Forward sequence analysis revealed {chain_len} consecutive transactions; {len(short_hops)} executed within 10 minutes."
                evidence_items.append(
                    EvidenceItem(
                        claim=claim_text,
                        source=EvidenceSourceEnum.GRAPH,
                        ref="query:temporal_pattern_query",
                        entity_ids=[str(h.get("to_txn_id")) for h in hops],
                    )
                )

        return evidence_items, entities, relationships
