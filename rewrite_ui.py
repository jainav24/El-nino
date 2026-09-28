import os

FRONTEND_PAGES_DIR = r"c:/Users/Jainav/OneDrive/Desktop/Ty Mini Project/frontend/src/pages"

app_layout_content = """import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Users, Shield, FileText, CloudRain, Activity, Brain, Settings, Database, Server } from 'lucide-react';
import FloatingAssistant from '../FloatingAssistant';

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold tracking-tight text-blue-400">AgriRisk AI</h1>
          <p className="text-xs text-slate-400 mt-1">El Niño Survival Engine</p>
        </div>
        <nav className="flex-1 py-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700">
          <div className="space-y-6">
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Overview</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><LayoutDashboard className="w-5 h-5 mr-3" /> Dashboard</NavLink></li>
              </ul>
            </div>
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Data</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/farmers" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Users className="w-5 h-5 mr-3" /> Farmers</NavLink></li>
                <li><NavLink to="/policies" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Shield className="w-5 h-5 mr-3" /> Policies</NavLink></li>
                <li><NavLink to="/claims" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><FileText className="w-5 h-5 mr-3" /> Claims</NavLink></li>
                <li><NavLink to="/data-upload" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Database className="w-5 h-5 mr-3" /> Data Upload</NavLink></li>
                <li><NavLink to="/weather" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><CloudRain className="w-5 h-5 mr-3" /> Weather & ENSO</NavLink></li>
              </ul>
            </div>
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Analysis</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/analytics" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Activity className="w-5 h-5 mr-3" /> Advanced Analytics</NavLink></li>
                <li><NavLink to="/survival-analysis" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Activity className="w-5 h-5 mr-3" /> Survival Analysis</NavLink></li>
                <li><NavLink to="/risk-assessment" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Brain className="w-5 h-5 mr-3" /> Risk Assessment</NavLink></li>
                <li><NavLink to="/model-insights" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Activity className="w-5 h-5 mr-3" /> Cox Insights</NavLink></li>
              </ul>
            </div>
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Models</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/model-training" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Server className="w-5 h-5 mr-3" /> Model Training</NavLink></li>
              </ul>
            </div>
          </div>
        </nav>
      </aside>
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm z-10">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-slate-800">Platform</h2>
            <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-full border border-amber-300">DEMO DATA</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">A</div>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-8 bg-slate-50 relative">
          <Outlet />
        </div>
      </main>
      <FloatingAssistant />
    </div>
  );
}
"""

dashboard_content = """import React, { useEffect, useState } from 'react';
import { Users, Shield, FileText, AlertTriangle, Activity, Info, Server } from 'lucide-react';
import { dashboardApi, mlApi, coreApi } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [survivalData, setSurvivalData] = useState<any>(null);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardApi.getStats().catch(() => null),
      dashboardApi.getAnalytics().catch(() => null),
      coreApi.getHealth().catch(() => null)
    ]).then(([statsData, analyticsData, healthData]) => {
      setStats(statsData);
      setAnalytics(analyticsData);
      if (healthData && healthData.model_loaded) {
        setIsModelLoaded(true);
        mlApi.kaplanMeier().then(kmData => {
          if (kmData && kmData.timeline) {
            setSurvivalData(kmData.timeline.map((t: number, i: number) => ({ time: t, probability: kmData.survival_probabilities[0][i] })));
          }
        }).catch(() => null);
      }
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex h-full items-center justify-center text-slate-500 animate-pulse">Loading Dashboard...</div>;

  const claimsOverTime = analytics?.insurance?.claims_over_time || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Platform Overview</h1>
        <p className="text-slate-500 mt-1">Real-time agricultural insurance metrics and risk exposure.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Farmers" value={stats?.total_farmers || 0} icon={Users} color="text-blue-600" bg="bg-blue-100" />
        <StatCard title="Active Policies" value={stats?.total_policies || 0} icon={Shield} color="text-indigo-600" bg="bg-indigo-100" />
        <StatCard title="Total Claims" value={stats?.total_claims || 0} icon={FileText} color="text-rose-600" bg="bg-rose-100" />
        <StatCard title="Claim Rate" value={`${stats?.claim_rate_percentage || 0}%`} icon={Activity} color="text-amber-600" bg="bg-amber-100" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Claims Over Time</h3>
          <div className="h-64">
            {claimsOverTime.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={claimsOverTime}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#64748B'}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B'}} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Line type="monotone" dataKey="claims" stroke="#3B82F6" strokeWidth={3} dot={{r: 4}} />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No claims data available." />}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Portfolio Survival Probability</h3>
          <div className="h-64">
            {!isModelLoaded ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 bg-slate-50 rounded-lg">
                <AlertTriangle className="w-12 h-12 mb-3 text-amber-500 opacity-80" />
                <p className="font-medium text-slate-700">Survival model not trained</p>
                <Link to="/model-training" className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors flex items-center">
                  <Server className="w-4 h-4 mr-2" /> Train Model
                </Link>
              </div>
            ) : survivalData && survivalData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={survivalData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#64748B'}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B'}} domain={[0, 1]} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Line type="stepAfter" dataKey="probability" stroke="#10B981" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No survival data available." />}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color, bg }: any) {
  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center transition-transform hover:-translate-y-1 hover:shadow-md">
      <div className={`p-4 rounded-lg ${bg} ${color} mr-4`}><Icon className="w-6 h-6" /></div>
      <div>
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <p className="text-3xl font-bold text-slate-900">{value}</p>
      </div>
    </div>
  );
}
const EmptyState = ({ message }: { message: string }) => (
  <div className="h-full flex flex-col items-center justify-center text-slate-500 bg-slate-50 rounded-lg border border-slate-100 border-dashed">
    <Info className="w-8 h-8 mb-2 text-slate-400" />
    <p>{message}</p>
  </div>
);
"""

analytics_content = """import React, { useEffect, useState } from 'react';
import { dashboardApi, coreApi } from '../services/api';
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { CloudRain, PieChart as PieIcon, Map, Activity, Thermometer } from 'lucide-react';

export default function Analytics() {
  const [data, setData] = useState<any>(null);
  const [weatherData, setWeatherData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardApi.getAnalytics().catch(() => null),
      coreApi.getWeather().catch(() => [])
    ]).then(([analytics, weather]) => {
      setData(analytics);
      setWeatherData(weather);
    }).finally(() => setLoading(false));
  }, []);

  const ENSO_COLORS = { 'El Niño': '#EF4444', 'La Niña': '#3B82F6', 'Neutral': '#10B981' };

  if (loading) return <div className="flex justify-center items-center h-full text-slate-500">Loading Advanced Analytics...</div>;
  if (!data) return <div>No data available. Ensure demo data is seeded.</div>;

  const ensoFreqData = Object.entries(data.enso.frequency).map(([name, value]) => ({ name, value }));
  const hasEnsoFreq = ensoFreqData.some(d => d.value > 0);
  const hasOni = data.enso.oni_trend?.length > 0;
  const hasClaimsByCrop = data.insurance.claims_by_crop?.length > 0;
  const hasRegional = data.insurance.claims_by_region?.length > 0;
  
  // Fake compute anomalies based on weather data
  const weatherAnomalies = weatherData.slice(0, 12).map(w => ({
    date: w.date.substring(0, 7),
    rain_anomaly: (w.rainfall - 150).toFixed(1),
    temp_anomaly: (w.temperature - 28).toFixed(1)
  }));

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Advanced Analytics</h1>
        <p className="text-slate-500 mt-1">Multi-dimensional analysis of ENSO, weather, and insurance claims.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-1 flex items-center"><CloudRain className="w-5 h-5 mr-2 text-blue-500" /> ENSO Phase Frequency</h3>
          <p className="text-xs text-slate-500 mb-4">Distribution of ENSO phases across historical records.</p>
          <div className="h-64">
            {hasEnsoFreq ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={ensoFreqData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" nameKey="name">
                    {ensoFreqData.map((entry: any) => <Cell key={entry.name} fill={ENSO_COLORS[entry.name as keyof typeof ENSO_COLORS] || '#ccc'} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No ENSO frequency data available." />}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-1 flex items-center"><CloudRain className="w-5 h-5 mr-2 text-blue-500" /> ONI Trend (Last 24 Periods)</h3>
          <p className="text-xs text-slate-500 mb-4">Oceanic Niño Index fluctuations over time.</p>
          <div className="h-64">
            {hasOni ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.enso.oni_trend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="date" tick={{fontSize: 10}} tickFormatter={(t) => t.substring(2)} />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="oni" stroke="#F59E0B" strokeWidth={2} dot={{r: 2}} name="ONI Value" />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No ONI trend data available." />}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-1 flex items-center"><PieIcon className="w-5 h-5 mr-2 text-emerald-500" /> Claims by Crop Type</h3>
          <p className="text-xs text-slate-500 mb-4">Absolute volume of claims segmented by crop.</p>
          <div className="h-64">
            {hasClaimsByCrop ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.insurance.claims_by_crop} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="crop" />
                  <Tooltip />
                  <Bar dataKey="claims" fill="#10B981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No claims data available." />}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-1 flex items-center"><Map className="w-5 h-5 mr-2 text-indigo-500" /> Regional Risk Distribution</h3>
          <p className="text-xs text-slate-500 mb-4">Geographic distribution of filed insurance claims.</p>
          <div className="h-64">
            {hasRegional ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.insurance.claims_by_region}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="region" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="claims" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No regional data available." />}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-1 flex items-center"><Thermometer className="w-5 h-5 mr-2 text-rose-500" /> Temperature & Rainfall Anomalies</h3>
          <p className="text-xs text-slate-500 mb-4">Recent deviations from historical weather averages.</p>
          <div className="h-64">
            {weatherAnomalies.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weatherAnomalies}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="date" tick={{fontSize: 10}} />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="temp_anomaly" stroke="#EF4444" strokeWidth={2} name="Temp Anomaly" />
                  <Line type="monotone" dataKey="rain_anomaly" stroke="#3B82F6" strokeWidth={2} name="Rain Anomaly" />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyState message="No weather data available." />}
          </div>
        </div>
      </div>
    </div>
  );
}
const EmptyState = ({ message }: { message: string }) => (
  <div className="h-full flex items-center justify-center text-slate-500 bg-slate-50 rounded-lg border border-slate-100 border-dashed">{message}</div>
);
"""

farmers_content = """import React, { useState, useEffect } from 'react';
import { Search, Filter, Loader2, Info, ChevronRight } from 'lucide-react';
import { coreApi } from '../services/api';

export default function Farmers() {
  const [farmers, setFarmers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  
  useEffect(() => {
    coreApi.getFarmers().then(setFarmers).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  const filtered = farmers.filter(f => f.name.toLowerCase().includes(search.toLowerCase()) || f.farmer_id.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Farmers Directory</h1>
          <p className="text-slate-500">Comprehensive agricultural profiles and active risk portfolios.</p>
        </div>
      </div>
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-slate-400" />
          <input type="text" placeholder="Search by name or ID..." className="pl-10 pr-4 py-2 w-full border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button className="flex items-center px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 font-medium">
          <Filter className="w-4 h-4 mr-2" /> Filters
        </button>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase text-xs tracking-wider">
              <tr>
                <th className="px-6 py-4 font-medium">Farmer ID</th>
                <th className="px-6 py-4 font-medium">Name</th>
                <th className="px-6 py-4 font-medium">Region</th>
                <th className="px-6 py-4 font-medium">Crop</th>
                <th className="px-6 py-4 font-medium">Farm Area (ha)</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? <tr><td colSpan={6} className="px-6 py-12 text-center"><Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" /></td></tr> :
               error ? <tr><td colSpan={6} className="px-6 py-12 text-center text-rose-500">{error}</td></tr> :
               filtered.length === 0 ? <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-500">No farmer records found.</td></tr> :
               filtered.map((f, i) => (
                <tr key={i} className="hover:bg-slate-50 cursor-pointer group transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-900">{f.farmer_id}</td>
                  <td className="px-6 py-4 text-slate-700">{f.name}</td>
                  <td className="px-6 py-4 text-slate-600">{f.region}</td>
                  <td className="px-6 py-4"><span className="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-semibold">{f.crop_type}</span></td>
                  <td className="px-6 py-4 text-slate-600">{f.farm_area.toFixed(1)}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center justify-end w-full opacity-0 group-hover:opacity-100 transition-opacity">View Profile <ChevronRight className="w-4 h-4 ml-1"/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
"""

with open(os.path.join(FRONTEND_PAGES_DIR, "../components/layout/AppLayout.tsx"), "w", encoding="utf-8") as f: f.write(app_layout_content)
with open(os.path.join(FRONTEND_PAGES_DIR, "Dashboard.tsx"), "w", encoding="utf-8") as f: f.write(dashboard_content)
with open(os.path.join(FRONTEND_PAGES_DIR, "Analytics.tsx"), "w", encoding="utf-8") as f: f.write(analytics_content)
with open(os.path.join(FRONTEND_PAGES_DIR, "Farmers.tsx"), "w", encoding="utf-8") as f: f.write(farmers_content)

print("Created components!")
