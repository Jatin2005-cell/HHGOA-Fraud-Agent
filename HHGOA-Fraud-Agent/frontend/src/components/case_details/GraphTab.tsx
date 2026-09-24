import React, { useState, useEffect } from 'react';
import { fetchInvestigationGraph } from '../../api/investigations';
import type { GraphNode, GraphEdge } from '../../types/evidence';
import { Skeleton } from '../common/Skeleton';
import { Network, Database, ShieldAlert, User, CreditCard, Laptop, Hash, Archive, Info, HelpCircle } from 'lucide-react';

interface GraphTabProps {
  caseId: string;
}

export const GraphTab: React.FC<GraphTabProps> = ({ caseId }) => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);

  useEffect(() => {
    const loadGraph = async () => {
      setIsLoading(true);
      try {
        const data = await fetchInvestigationGraph(caseId);
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
        if (data.nodes?.length > 0) {
          setSelectedNode(data.nodes[0]);
        }
        if (data.edges?.length > 0) {
          setSelectedEdge(data.edges[0]);
        }
      } catch (err) {
        console.error('Failed to load investigation graph', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadGraph();
  }, [caseId]);

  if (isLoading) {
    return <Skeleton className="h-96 w-full rounded-lg" />;
  }

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'DynamicCase':
        return ShieldAlert;
      case 'Customer':
        return User;
      case 'Card':
        return CreditCard;
      case 'Transaction':
        return Hash;
      case 'DeviceProfile':
        return Laptop;
      case 'ClosedCase':
        return Archive;
      default:
        return Database;
    }
  };

  const getNodeColor = (type: string, isSelected: boolean) => {
    const base = isSelected ? 'ring-2 ring-sky-500 scale-105 ' : '';
    switch (type) {
      case 'DynamicCase':
        return base + 'bg-red-50 border-red-300 text-red-800';
      case 'Customer':
        return base + 'bg-blue-50 border-blue-300 text-blue-800';
      case 'Card':
        return base + 'bg-amber-50 border-amber-300 text-amber-800';
      case 'Transaction':
        return base + 'bg-purple-50 border-purple-300 text-purple-800';
      case 'DeviceProfile':
        return base + 'bg-emerald-50 border-emerald-300 text-emerald-800';
      case 'ClosedCase':
        return base + 'bg-slate-100 border-slate-300 text-slate-700';
      default:
        return base + 'bg-slate-50 border-slate-200 text-slate-800';
    }
  };

  const getEdgeReasoning = (edge: GraphEdge) => {
    switch (edge.relationship) {
      case 'FROM_DEVICE':
        return {
          category: 'Shared Device Hardware Fingerprint',
          explanation: `Transaction executed from browser/hardware profile ${edge.target}. If multiple cards originate from this profile within a short window, this indicates bot velocity or card-testing syndicates.`,
          provenance: 'edges_from_device.csv (Verified Staged Topology)',
        };
      case 'MADE':
        return {
          category: 'Card Authorization',
          explanation: `Payment card ${edge.source} was debited for this transaction. GSQL card window analysis evaluates whether prior sub-$5 micro-authorizations occurred.`,
          provenance: 'transactions.csv (Verified Staged Topology)',
        };
      case 'OWNS':
        return {
          category: 'Account Ownership',
          explanation: `Customer ${edge.source} is the verified cardholder account owner. Multi-card graph traversal checks for sibling cards sharing this customer profile.`,
          provenance: 'cards.csv (Verified Staged Topology)',
        };
      case 'BILLED_IN':
        return {
          category: 'Geographical Billing Jurisdiction',
          explanation: `In-person or terminal transaction billed in region ${edge.target}. The agent computes historical frequency to identify out-of-region card-present anomalies.`,
          provenance: 'edges_billed_in.csv (Verified Staged Topology)',
        };
      case 'CASE_INVOLVES':
        return {
          category: 'Historical Fraud Incident Connection',
          explanation: `Transaction is formally connected to investigation record ${edge.source}. Historical closed cases provide precedent for confirmed fraud or cleared false alarms.`,
          provenance: 'edges_case_involves.csv (Verified Staged Topology)',
        };
      case 'CASE_ON_CARD':
        return {
          category: 'Payment Instrument Investigation Link',
          explanation: `Card has been subject to previous closed fraud investigations, indicating repeat compromise risk or recurring dispute activity.`,
          provenance: 'edges_case_on_card.csv (Verified Staged Topology)',
        };
      case 'NEXT_TRANSACTION':
        return {
          category: 'High-Velocity Temporal Sequence',
          explanation: `Chronologically adjacent transaction occurring within rapid succession. Sequence analysis evaluates velocity, amount deltas, and cross-channel stepping.`,
          provenance: 'edges_next_transaction.csv (Verified Staged Topology)',
        };
      default:
        return {
          category: 'Graph Relationship',
          explanation: 'Topological relationship established through graph traversal.',
          provenance: 'FraudInvestigationGraph (Staged Dataset)',
        };
    }
  };

  return (
    <div className="space-y-4 text-left">
      {/* Graph Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-sky-600" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Topological Subgraph ({nodes.length} Vertices, {edges.length} Edges)
          </h4>
        </div>
        <span className="text-[11px] text-slate-500">
          Source: FraudInvestigationGraph (Genuine HHGOA_IEEE Staged Dataset)
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Visual Graph Layout Canvas */}
        <div className="lg:col-span-8 bg-slate-900 rounded-lg p-5 border border-slate-800 relative min-h-[440px] flex flex-col justify-between overflow-hidden shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs border-b border-slate-800 pb-3 z-10">
            <span className="font-mono text-slate-300">Topology Canvas</span>
            <div className="flex items-center gap-3 text-[10px]">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-red-400" /> DynamicCase
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-blue-400" /> Customer
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-400" /> Card
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-purple-400" /> Txn
              </span>
            </div>
          </div>

          {/* Interactive Node Grid Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 my-auto py-4 z-10">
            {nodes.map((node) => {
              const Icon = getNodeIcon(node.type);
              const isSelected = selectedNode?.id === node.id;
              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3 rounded-lg border text-left flex items-start gap-2.5 transition-all shadow-sm ${getNodeColor(
                    node.type,
                    isSelected
                  )}`}
                >
                  <Icon className="w-4 h-4 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <div className="text-[10px] font-mono uppercase opacity-75">{node.type}</div>
                    <div className="text-xs font-bold font-mono truncate">{node.id}</div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Connected Edges Table / Ticker */}
          <div className="border-t border-slate-800 pt-3 z-10">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
              Select Edge to inspect &quot;Why Connected?&quot; ({edges.length}):
            </span>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto custom-scrollbar">
              {edges.map((edge, idx) => {
                const isSelected =
                  selectedEdge?.source === edge.source &&
                  selectedEdge?.target === edge.target &&
                  selectedEdge?.relationship === edge.relationship;
                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedEdge(edge)}
                    className={`text-[10px] font-mono px-2 py-1 rounded border transition-all ${
                      isSelected
                        ? 'bg-sky-950 text-sky-300 border-sky-500 ring-1 ring-sky-500 font-bold'
                        : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
                    }`}
                  >
                    {edge.source} <span className="text-sky-400">&mdash;[{edge.relationship}]&rarr;</span> {edge.target}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Vertex Inspector + Why Connected Panel */}
        <div className="lg:col-span-4 space-y-4">
          {/* Why Connected Explainer */}
          {selectedEdge && (
            <div className="bg-sky-950/40 p-4 rounded-lg border border-sky-800/60 shadow-sm text-xs">
              <div className="flex items-center gap-2 text-sky-400 font-bold uppercase tracking-wider text-[11px] mb-2 border-b border-sky-800/40 pb-1.5">
                <HelpCircle className="w-4 h-4 shrink-0" />
                <span>Why Connected?</span>
              </div>
              {(() => {
                const reasoning = getEdgeReasoning(selectedEdge);
                return (
                  <div className="space-y-2">
                    <div className="flex items-center gap-1.5 text-slate-200 font-mono text-[11px]">
                      <span className="font-semibold text-white">{selectedEdge.source}</span>
                      <span className="text-sky-400 font-bold">&rarr; {selectedEdge.relationship} &rarr;</span>
                      <span className="font-semibold text-white">{selectedEdge.target}</span>
                    </div>
                    <div className="text-[11px] font-semibold text-sky-300">
                      Category: {reasoning.category}
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed bg-slate-900/60 p-2.5 rounded border border-slate-800">
                      {reasoning.explanation}
                    </p>
                    <div className="text-[10px] text-slate-400 flex items-center gap-1">
                      <Database className="w-3 h-3 text-sky-400 shrink-0" />
                      <span>Lineage: {reasoning.provenance}</span>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Selected Vertex Inspector Panel */}
          <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm text-xs">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-2">
              <Info className="w-4 h-4 text-sky-600" />
              <h5 className="text-xs font-bold uppercase tracking-wider text-slate-700">Vertex Inspector</h5>
            </div>

            {selectedNode ? (
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400 font-medium">Type:</span>
                  <span className="font-mono text-slate-900 font-bold">{selectedNode.type}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-slate-400 font-medium">Primary ID:</span>
                  <span className="font-mono text-sky-800 font-bold bg-sky-50 px-1.5 py-0.5 rounded border border-sky-200">
                    {selectedNode.id}
                  </span>
                </div>

                {selectedNode.metadata && (
                  <div className="pt-2 border-t border-slate-100">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                      Attributes
                    </span>
                    <div className="bg-slate-50 p-2 rounded border border-slate-200 font-mono text-[10px] space-y-1">
                      {Object.entries(selectedNode.metadata).map(([k, v]) => (
                        <div key={k} className="flex justify-between border-b border-slate-100 pb-0.5">
                          <span className="text-slate-500">{k}:</span>
                          <span className="text-slate-900 font-medium truncate max-w-[140px]">
                            {String(v)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6 text-slate-400 text-xs">
                Select a vertex to inspect properties.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
