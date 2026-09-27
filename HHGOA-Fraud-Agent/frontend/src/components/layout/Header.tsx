import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, X, ArrowRight, UserCheck, Shield, Sparkles } from 'lucide-react';
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
    <header className="h-16 bg-[#0B0F17]/90 backdrop-blur-xl border-b border-slate-800/60 text-white flex items-center justify-between px-6 z-40 sticky top-0 font-sans shadow-2xl transition-all">
      {/* Brand & Logos Section */}
      <div className="flex items-center gap-4">
        <div 
          className="relative flex items-center justify-center hover:scale-105 transition-transform duration-200 cursor-pointer" 
          onClick={() => navigate('/')}
        >
          {/* Base Logo */}
          <img
            src={hackerHouseLogo}
            alt="Hacker House Logo"
            className="h-10 w-auto object-contain block"
          />
          
          {/* Goa Hindi Logo - Placed EXACTLY in the center of Hacker House Logo */}
          <img
            src={goaHindiLogo}
            alt="Goa Logo"
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-7 h-7 object-contain drop-shadow-[0_0_12px_rgba(56,189,248,0.7)] pointer-events-none"
          />
        </div>

        <div className="h-6 w-px bg-slate-800/80" />

        <div className="flex flex-col justify-center">
          <div className="flex items-center gap-2">
            <span className="font-extrabold tracking-tight text-sm bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              HHGOA Fraud Agent
            </span>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center gap-1">
              <Sparkles className="w-2.5 h-2.5" />
              v2.4
            </span>
          </div>
          <span className="text-[11px] text-slate-400 font-normal">
            TigerGraph Agentic Intelligence
          </span>
        </div>
      </div>

      {/* Global Tactical Search Bar */}
      <div className="relative w-96" ref={dropdownRef}>
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none transition-colors group-focus-within:text-sky-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => {
              if (searchResult) setShowSearchDropdown(true);
            }}
            placeholder="Search Case ID, Customer, Card, or Txn..."
            className="w-full h-10 pl-10 pr-9 bg-slate-900/60 border border-slate-800/80 rounded-xl text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-sky-500/60 focus:ring-2 focus:ring-sky-500/20 transition-all shadow-inner backdrop-blur-md"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 text-slate-400 hover:text-slate-200 transition-colors p-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {showSearchDropdown && searchResult && (
          <div className="absolute left-0 right-0 top-12 bg-[#0F1523]/95 border border-slate-800 rounded-2xl shadow-2xl text-slate-200 z-50 overflow-hidden text-xs backdrop-blur-2xl">
            <div className="p-3 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/50">
              <span className="font-medium text-slate-300 text-xs">
                Search Results for &quot;{searchResult.query}&quot; ({searchResult.total_matches})
              </span>
              {isSearching && <span className="text-sky-400 animate-pulse text-xs font-medium">Querying Graph...</span>}
            </div>

            <div className="max-h-80 overflow-y-auto custom-scrollbar p-2 divide-y divide-slate-800/40">
              {/* Cases */}
              {searchResult.cases.length > 0 && (
                <div className="py-2">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-2">
                    Identified Cases
                  </div>
                  {searchResult.cases.map((c) => (
                    <button
                      key={c.case_id}
                      onClick={() => handleSelectCase(c.case_id)}
                      className="w-full text-left px-3 py-2.5 rounded-xl hover:bg-slate-800/50 flex items-center justify-between group transition-all"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="font-semibold text-sky-400 group-hover:text-sky-300">{c.case_id}</span>
                        <span className="text-xs text-slate-400">({c.pattern || 'No Typology'})</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="font-medium px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                          {c.verdict}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 transition-transform group-hover:translate-x-1" />
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Customers */}
              {searchResult.customers.length > 0 && (
                <div className="py-2">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-2">
                    Matched Entities
                  </div>
                  {searchResult.customers.map((cu) => (
                    <button
                      key={cu.customer_id}
                      onClick={() => handleSelectCase(cu.related_case)}
                      className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800/50 flex items-center justify-between transition-all"
                    >
                      <span className="text-slate-300 font-medium">{cu.customer_id}</span>
                      <span className="text-xs text-slate-400">Linked Case: <strong className="text-sky-400 font-semibold">{cu.related_case}</strong></span>
                    </button>
                  ))}
                </div>
              )}

              {/* Transactions */}
              {searchResult.transactions.length > 0 && (
                <div className="py-2">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-2">
                    Transaction Logs
                  </div>
                  {searchResult.transactions.map((t) => (
                    <button
                      key={t.transaction_id}
                      onClick={() => handleSelectCase(t.related_case)}
                      className="w-full text-left px-3 py-2 rounded-xl hover:bg-slate-800/50 flex items-center justify-between transition-all"
                    >
                      <span className="text-slate-300 font-medium">Txn #{t.transaction_id}</span>
                      <span className="text-xs text-slate-400">Linked Case: <strong className="text-sky-400 font-semibold">{t.related_case}</strong></span>
                    </button>
                  ))}
                </div>
              )}

              {searchResult.total_matches === 0 && (
                <div className="p-5 text-center text-slate-400 text-xs">
                  No matching graph telemetry records found.
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Runtime Provenance & Operator Profile */}
      <div className="flex items-center gap-4">
        <ProvenanceBanner />

        {/* Notification Bell */}
        <div className="relative" ref={notificationRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2.5 text-slate-400 hover:text-white rounded-xl bg-slate-900/60 border border-slate-800/80 hover:bg-slate-800/80 transition-all relative active:scale-95"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-amber-400 rounded-full ring-4 ring-[#0B0F17] animate-pulse" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-12 w-80 bg-[#0F1523]/95 border border-slate-800 rounded-2xl shadow-2xl text-slate-200 z-50 p-4 text-xs backdrop-blur-2xl">
              <div className="font-semibold text-slate-200 border-b border-slate-800 pb-2.5 mb-3 flex justify-between items-center text-xs">
                <span className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-sky-400" />
                  System Notifications
                </span>
                <span
                  className="text-slate-400 hover:text-slate-200 cursor-pointer text-[11px] font-medium transition-colors"
                  onClick={() => setShowNotifications(false)}
                >
                  Dismiss
                </span>
              </div>
              <div className="space-y-2.5">
                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-200">
                  <div className="font-semibold text-xs text-amber-400 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                    Pending Approvals Required
                  </div>
                  <div className="text-[11px] text-amber-200/80 mt-1 leading-relaxed">
                    High-exposure card blocks require Lead Analyst sign-off.
                  </div>
                </div>

                <div className="p-3 bg-sky-500/10 border border-sky-500/20 rounded-xl text-sky-200">
                  <div className="font-semibold text-xs text-sky-400 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-sky-400" />
                    TigerGraph Engine Synced
                  </div>
                  <div className="text-[11px] text-sky-200/80 mt-1 leading-relaxed">
                    FraudInvestigationGraph active with sub-second latencies.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="h-6 w-px bg-slate-800/80" />

        {/* Active Operator Badge */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500/20 to-blue-600/10 border border-sky-500/30 flex items-center justify-center text-sky-400 shadow-lg shadow-sky-500/10">
            <UserCheck className="w-4 h-4" />
          </div>
          <div className="text-left text-xs">
            <div className="font-bold text-slate-100 leading-tight">Fraud Lead Analyst</div>
            <div className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Authorized (L1/L2)
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};