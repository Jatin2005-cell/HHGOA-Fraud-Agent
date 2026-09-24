import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  SearchCode,
  Briefcase,
  CheckSquare,
  FileSpreadsheet,
  Award,
  ScrollText,
  Activity,
  ChevronLeft,
  ChevronRight,
  Database,
  Cpu,
  Server,
  Zap,
} from 'lucide-react';
import { getDependencyHealth, getSystemHealth } from '../../api/health';

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'degraded' | 'offline'>('healthy');
  const [dataMode, setDataMode] = useState<'LIVE_TIGERGRAPH' | 'OFFLINE_STAGED_SIMULATION'>('OFFLINE_STAGED_SIMULATION');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const h = await getSystemHealth();
        if (h.status === 'healthy') {
          setHealthStatus('healthy');
        } else {
          setHealthStatus('degraded');
        }
        const d = await getDependencyHealth();
        if (d.data_mode) {
          setDataMode(d.data_mode);
        }
      } catch {
        setHealthStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/investigate', label: 'Investigate', icon: SearchCode },
    { to: '/cases', label: 'Cases', icon: Briefcase },
    { to: '/approvals', label: 'Approvals', icon: CheckSquare },
    { to: '/sar', label: 'SAR Reports', icon: FileSpreadsheet },
    { to: '/benchmark', label: 'Benchmark', icon: Award },
    { to: '/audit', label: 'Audit Logs', icon: ScrollText },
  ];

  return (
    <aside
      className={`bg-[#0B0F17] border-r border-slate-800/80 text-slate-300 flex flex-col justify-between transition-all duration-200 z-20 select-none font-sans ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Navigation Header & Items */}
      <div className="py-4">
        <div className="flex items-center justify-between px-4 mb-4">
          {!collapsed && (
            <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest">
              SOC Navigation
            </span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 text-slate-400 hover:text-white rounded-md bg-slate-900/80 border border-slate-800 hover:bg-slate-800 transition-colors mx-auto"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4 text-sky-400" /> : <ChevronLeft className="w-4 h-4 text-sky-400" />}
          </button>
        </div>

        <nav className="space-y-1 px-2 font-mono">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-sky-500/10 text-sky-400 border-l-2 border-sky-400 font-semibold shadow-[0_0_12px_rgba(56,189,248,0.15)]'
                      : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
                  } ${collapsed ? 'justify-center' : ''}`
                }
                title={collapsed ? item.label : undefined}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {!collapsed && <span className="tracking-wide text-[11px]">{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Real-time System Telemetry Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/80 font-mono">
        {!collapsed ? (
          <div>
            <div className="flex items-center justify-between mb-2.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-sky-400" />
                Telemetry Health
              </span>
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full uppercase flex items-center gap-1 ${
                  healthStatus === 'healthy'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : healthStatus === 'degraded'
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                {healthStatus}
              </span>
            </div>

            <div className="space-y-2 text-[10px]">
              <div className="flex items-center justify-between text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Database className="w-3 h-3 text-sky-400" /> TigerGraph
                </span>
                <span className={`font-semibold ${dataMode === 'LIVE_TIGERGRAPH' ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {dataMode === 'LIVE_TIGERGRAPH' ? 'Live Cluster' : 'Offline Staged'}
                </span>
              </div>

              <div className="flex items-center justify-between text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-sky-400" /> TigerGraph MCP
                </span>
                <span className={`font-semibold ${dataMode === 'LIVE_TIGERGRAPH' ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {dataMode === 'LIVE_TIGERGRAPH' ? 'RESTPP Live' : 'Local Adapter'}
                </span>
              </div>

              <div className="flex items-center justify-between text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Cpu className="w-3 h-3 text-sky-400" /> Agent Engine
                </span>
                <span className="text-emerald-400 font-semibold">Ready</span>
              </div>

              <div className="flex items-center justify-between text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Server className="w-3 h-3 text-sky-400" /> REST API
                </span>
                <span className="text-emerald-400 font-semibold">Healthy</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2" title={`System Health: ${healthStatus.toUpperCase()}`}>
            <span
              className={`w-3 h-3 rounded-full relative flex items-center justify-center ${
                healthStatus === 'healthy' ? 'bg-emerald-400' : 'bg-rose-500'
              }`}
            >
              <span className={`absolute w-full h-full rounded-full animate-ping opacity-75 ${
                healthStatus === 'healthy' ? 'bg-emerald-400' : 'bg-rose-500'
              }`} />
            </span>
          </div>
        )}
      </div>
    </aside>
  );
};