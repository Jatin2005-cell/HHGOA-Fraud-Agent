export interface EvidenceItem {
  id?: string;
  evidence_type: string;
  description: string;
  source: string;
  tool: string;
  entity_ids: string[];
  investigation_step: number;
  confidence: number;
  epistemic_status: 'OBSERVED' | 'INFERENCE' | 'UNCERTAINTY' | string;
  provenance_verified?: boolean;
}

export interface GraphNode {
  id: string;
  type: 'DynamicCase' | 'Customer' | 'Card' | 'Transaction' | 'DeviceProfile' | 'ClosedCase' | string;
  label: string;
  metadata?: Record<string, any>;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
}

export interface InvestigationGraph {
  case_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}
