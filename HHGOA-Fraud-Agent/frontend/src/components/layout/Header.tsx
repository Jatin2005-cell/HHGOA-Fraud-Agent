import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, X, ArrowRight, UserCheck, Shield } from 'lucide-react';
import { performGlobalSearch } from '../../api/search';
import type { SearchResult } from '../../types/api';
import { ProvenanceBanner } from './ProvenanceBanner';

import hackerHouseLogo from '../../assets/hacker-house.png';
import goaHindiLogo from '../../assets/goa_hindi.svg';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowSearchDropdown(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (!searchTerm.trim()) {
      setSearchResult(null);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await performGlobalSearch(searchTerm);
        setSearchResult(res);
        setShowSearchDropdown(true);
      } catch (err) {
        console.error('Search failed', err);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleSelectCase = (caseId: string) => {
    setShowSearchDropdown(false);
    setSearchTerm('');
    navigate(`/cases/${caseId}`);
  };

  return (
    <header className="h-16 bg-[#0B0F17]/95 backdrop-blur-md border-b border-slate-800/80 text-white flex items-center justify-between px-6 z-40 sticky top-0 font-sans shadow-lg">
      {/* Brand & Logos Section */}
      <div className="flex items-center gap-3">
        <div className="relative w-28 h-12 flex items-center justify-center shrink-0">
          <img
            src={hackerHouseLogo}
            alt="Hacker House Logo"
            className="w-28 h-12 object-contain"
          />
          <img
            src={goaHindiLogo}
            alt="Goa Logo"
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 object-contain drop-shadow-[0_0_8px_rgba(56,189,248,0.5)] pointer-events-none"
          />
        </div>

        <div className="border-l border-slate-800 pl-3">
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold tracking-tight text-xs text-white uppercase">
              HHGOA Fraud Intelligence
            </span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
              SOC v2.4
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono block -mt-0.5">
            TigerGraph Agentic Security Operations
          </span>
        </div>
      </div>

      {/* Global Tactical Search Bar */}
      <div className="relative w-96" ref={dropdownRef}>
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => {
              if (searchResult) setShowSearchDropdown(true);
            }}
            placeholder="Search Case ID, Customer, Card, or Txn..."
            className="w-full h-9 pl-9 pr-8 bg-slate-950/80 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/80 focus:ring-1 focus:ring-sky-500/50 transition-all shadow-inner"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2 text-slate-400 hover:text-slate-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Search Results Cyber Dropdown */}
        {showSearchDropdown && searchResult && (
          <div className="absolute left-0 right-0 top-11 bg-[#0B0F17] border border-slate-800 rounded-xl shadow-2xl text-slate-200 z-50 overflow-hidden text-xs backdrop-blur-md">
            <div className="p-2.5 border-b border-slate-800/80 flex justify-between items-center bg-slate-950/60 font-mono">
              <span className="font-semibold text-slate-300 text-[11px]">
                Query Results: &quot;{searchResult.query}&quot; ({searchResult.total_matches})
              </span>
              {isSearching && <span className="text-sky-400 animate-pulse text-[10px]">Querying Graph...</span>}
            </div>

            <div className="max-h-80 overflow-y-auto custom-scrollbar p-2 divide-y divide-slate-800/50">
              {/* Cases */}
              {searchResult.cases.length > 0 && (
                <div className="py-1">
                  <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1 px-2">
                    Cases Identified
                  </div>
                  {searchResult.cases.map((c) => (
                    <button
                      key={c.case_id}
                      onClick={() => handleSelectCase(c.case_id)}
                      className="w-full text-left px-2 py-2 rounded-lg hover:bg-slate-800/60 flex items-center justify-between group transition-colors font-mono"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sky-400 group-hover:underline">{c.case_id}</span>
                        <span className="text-[10px] text-slate-400">({c.pattern || 'No Typology'})</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-[10px]">
                        <span className="font-semibold px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
                          {c.verdict}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-500 group-hover:text-sky-400 transition-transform group-hover:translate-x-0.5" />
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Customers */}
              {searchResult.customers.length > 0 && (
                <div className="py-1">
                  <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1 px-2">
                    Matched Entities
                  </div>
                  {searchResult.customers.map((cu) => (
                    <button
                      key={cu.customer_id}
                      onClick={() => handleSelectCase(cu.related_case)}
                      className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-slate-800/60 flex items-center justify-between transition-colors font-mono"
                    >
                      <span className="text-slate-300">{cu.customer_id}</span>
                      <span className="text-[10px] text-slate-500">Linked Case: <strong className="text-sky-400">{cu.related_case}</strong></span>
                    </button>
                  ))}
                </div>
              )}

              {/* Transactions */}
              {searchResult.transactions.length > 0 && (
                <div className="py-1">
                  <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1 px-2">
                    Transaction Logs
                  </div>
                  {searchResult.transactions.map((t) => (
                    <button
                      key={t.transaction_id}
                      onClick={() => handleSelectCase(t.related_case)}
                      className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-slate-800/60 flex items-center justify-between transition-colors font-mono"
                    >
                      <span className="text-slate-300">Txn #{t.transaction_id}</span>
                      <span className="text-[10px] text-slate-500">Linked Case: <strong className="text-sky-400">{t.related_case}</strong></span>
                    </button>
                  ))}
                </div>
              )}

              {searchResult.total_matches === 0 && (
                <div className="p-4 text-center text-slate-500 text-xs font-mono">
                  No matching graph telemetry records found.
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Runtime Provenance & Operator profile */}
      <div className="flex items-center gap-4">
        <ProvenanceBanner />

        {/* Notification Bell */}
        <div className="relative" ref={notificationRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-slate-400 hover:text-white rounded-lg bg-slate-900/80 border border-slate-800 hover:bg-slate-800 transition-colors relative"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-amber-500 rounded-full ring-2 ring-[#0B0F17] animate-pulse" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-11 w-80 bg-[#0B0F17] border border-slate-800 rounded-xl shadow-2xl text-slate-200 z-50 p-3.5 text-xs font-mono backdrop-blur-md">
              <div className="font-bold text-slate-300 border-b border-slate-800 pb-2 mb-2 flex justify-between items-center text-[11px]">
                <span className="flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-sky-400" />
                  SYSTEM ALERTS & NOTIFICATIONS
                </span>
                <span
                  className="text-slate-500 hover:text-slate-300 cursor-pointer text-[10px]"
                  onClick={() => setShowNotifications(false)}
                >
                  DISMISS
                </span>
              </div>
              <div className="space-y-2">
                <div className="p-2.5 bg-amber-950/30 border border-amber-500/30 rounded-lg text-amber-200">
                  <div className="font-bold text-[11px] text-amber-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                    Pending L2 Approvals
                  </div>
                  <div className="text-[10px] text-amber-300/80 mt-1 leading-relaxed">
                    High-exposure card blocks require Fraud Manager sign-off.
                  </div>
                </div>

                <div className="p-2.5 bg-sky-950/30 border border-sky-500/30 rounded-lg text-sky-200">
                  <div className="font-bold text-[11px] text-sky-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-sky-400" />
                    TigerGraph MCP Synced
                  </div>
                  <div className="text-[10px] text-sky-300/80 mt-1 leading-relaxed">
                    FraudInvestigationGraph verified and ready for real-time queries.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="h-6 w-px bg-slate-800" />

        {/* Active Operator Badge */}
        <div className="flex items-center gap-2.5 font-mono">
          <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-sky-400 shadow-inner">
            <UserCheck className="w-4 h-4" />
          </div>
          <div className="text-left text-xs">
            <div className="font-bold text-slate-200 leading-tight">Fraud Lead Analyst</div>
            <div className="text-[9px] text-emerald-400 flex items-center gap-1 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              AUTHORIZED (L1/L2)
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};