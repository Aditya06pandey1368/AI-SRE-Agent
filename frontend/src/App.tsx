import React, { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { Activity, ShieldAlert, CheckCircle, Terminal, PlayCircle } from 'lucide-react';
import axios from 'axios';

// --- Dashboard Component ---
const Dashboard = () => {
  return (
    <div className="p-8 animate-in fade-in duration-500">
      <header className="mb-10">
        <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Incident Dashboard</h1>
        <p className="text-muted">Monitor and respond to production incidents autonomously.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div className="glass-panel p-6 border-t-4 border-t-primary">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-muted">Active Incidents</h3>
            <Activity className="text-primary w-6 h-6" />
          </div>
          <p className="text-3xl font-bold mt-2">1</p>
        </div>
        <div className="glass-panel p-6 border-t-4 border-t-danger">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-muted">Critical</h3>
            <ShieldAlert className="text-danger w-6 h-6" />
          </div>
          <p className="text-3xl font-bold mt-2 text-danger">1</p>
        </div>
        <div className="glass-panel p-6 border-t-4 border-t-success">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-muted">Resolved (24h)</h3>
            <CheckCircle className="text-success w-6 h-6" />
          </div>
          <p className="text-3xl font-bold mt-2 text-success">5</p>
        </div>
        <div className="glass-panel p-6 border-t-4 border-t-accent">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-muted">AI LLM Calls</h3>
            <Terminal className="text-accent w-6 h-6" />
          </div>
          <p className="text-3xl font-bold mt-2">14</p>
        </div>
      </div>

      <div className="glass-panel p-6">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-warning" />
          Recent Incidents
        </h2>
        
        {/* We'll populate this with real data in the next step */}
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/10 text-muted">
                <th className="pb-3 font-medium">ID</th>
                <th className="pb-3 font-medium">Service</th>
                <th className="pb-3 font-medium">Severity</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Started</th>
                <th className="pb-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {/* Dummy row */}
              <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td className="py-4 font-mono text-sm">INC-DEMO</td>
                <td className="py-4 font-medium">payment-api</td>
                <td className="py-4"><span className="px-2 py-1 rounded bg-danger/20 text-danger text-xs font-bold uppercase">Critical</span></td>
                <td className="py-4"><span className="text-warning flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-warning animate-pulse"></span> Investigating</span></td>
                <td className="py-4 text-muted">Just now</td>
                <td className="py-4">
                  <button className="glass-button text-sm py-1">View</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// --- Simulator Component ---
const Simulator = () => {
  const [loading, setLoading] = useState(false);
  const triggerScenario = async (scenario: string) => {
    setLoading(true);
    try {
      // In production, this would point to the backend or simulator API
      await axios.post(`http://localhost:8001/simulate/${scenario}`);
      
      // If we trigger a scenario, we should also trigger an alert webhook
      if (scenario !== 'normal') {
        setTimeout(async () => {
          try {
             await axios.post('http://localhost:8000/api/v1/alerts/webhook', {
               source: "prometheus-simulator",
               service: "payment-api",
               severity: "critical",
               alert_name: `Simulated-${scenario}`,
               timestamp: new Date().toISOString()
             });
          } catch(e) {
            console.error("Failed to send webhook", e);
          }
        }, 1000);
      }
      
      alert(`Scenario ${scenario} triggered!`);
    } catch (e) {
      console.error(e);
      alert("Failed to trigger scenario.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <header className="mb-10">
        <h1 className="text-4xl font-bold text-white mb-2">Simulator Controls</h1>
        <p className="text-muted">Trigger synthetic production incidents.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 flex flex-col gap-4 items-start">
          <h3 className="font-bold text-lg">Bad Deployment</h3>
          <p className="text-sm text-muted mb-4 flex-grow">Simulates a deployment that immediately causes high error rates and latency.</p>
          <button disabled={loading} onClick={() => triggerScenario('bad_deployment')} className="glass-button w-full flex justify-center items-center gap-2">
            <PlayCircle className="w-4 h-4" /> Trigger
          </button>
        </div>
        
        <div className="glass-panel p-6 flex flex-col gap-4 items-start">
          <h3 className="font-bold text-lg">High CPU</h3>
          <p className="text-sm text-muted mb-4 flex-grow">Simulates a CPU spike causing service degradation.</p>
          <button disabled={loading} onClick={() => triggerScenario('high_cpu')} className="glass-button w-full flex justify-center items-center gap-2">
            <PlayCircle className="w-4 h-4" /> Trigger
          </button>
        </div>

        <div className="glass-panel p-6 flex flex-col gap-4 items-start">
          <h3 className="font-bold text-lg">Database Exhaustion</h3>
          <p className="text-sm text-muted mb-4 flex-grow">Simulates DB connection pool exhaustion.</p>
          <button disabled={loading} onClick={() => triggerScenario('db_exhaustion')} className="glass-button w-full flex justify-center items-center gap-2">
            <PlayCircle className="w-4 h-4" /> Trigger
          </button>
        </div>

        <div className="glass-panel p-6 flex flex-col gap-4 items-start border-t-2 border-success">
          <h3 className="font-bold text-lg text-success">Restore Normal</h3>
          <p className="text-sm text-muted mb-4 flex-grow">Resets the simulator back to healthy state.</p>
          <button disabled={loading} onClick={() => triggerScenario('normal')} className="glass-button w-full flex justify-center items-center gap-2">
            Restore
          </button>
        </div>
      </div>
    </div>
  );
};

// --- App Layout ---
function App() {
  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar */}
      <div className="w-64 glass-panel border-r border-white/5 flex flex-col m-4 mr-0 p-4 sticky top-4 h-[calc(100vh-2rem)]">
        <div className="flex items-center gap-3 mb-10 px-2 mt-4">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-primary to-accent flex items-center justify-center font-bold shadow-[0_0_15px_rgba(139,92,246,0.5)]">
            AI
          </div>
          <h2 className="text-xl font-bold tracking-wider">SRE Platform</h2>
        </div>
        
        <nav className="flex flex-col gap-2">
          <Link to="/" className="px-4 py-3 rounded-lg hover:bg-white/5 transition-colors flex items-center gap-3 text-muted hover:text-white font-medium">
            <Activity className="w-5 h-5" /> Dashboard
          </Link>
          <Link to="/simulator" className="px-4 py-3 rounded-lg hover:bg-white/5 transition-colors flex items-center gap-3 text-muted hover:text-white font-medium">
            <Terminal className="w-5 h-5" /> Simulator
          </Link>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/simulator" element={<Simulator />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
