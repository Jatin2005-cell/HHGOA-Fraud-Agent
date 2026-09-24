import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { Investigate } from './pages/Investigate';
import { Cases } from './pages/Cases';
import { CaseDetails } from './pages/CaseDetails';
import { Approvals } from './pages/Approvals';
import { SarReports } from './pages/SarReports';
import { Benchmark } from './pages/Benchmark';
import { AuditLogs } from './pages/AuditLogs';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="investigate" element={<Investigate />} />
          <Route path="cases" element={<Cases />} />
          <Route path="cases/:id" element={<CaseDetails />} />
          <Route path="approvals" element={<Approvals />} />
          <Route path="sar" element={<SarReports />} />
          <Route path="benchmark" element={<Benchmark />} />
          <Route path="audit" element={<AuditLogs />} />
          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
