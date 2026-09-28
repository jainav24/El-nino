import React, { useEffect, useState } from 'react';
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
        <h1 className="text-2xl font-bold text-slate-900">PMFBY Risk Intelligence Dashboard</h1>
        <p className="text-slate-500 mt-1">El Niño-aware agricultural risk assessment for insurers and government scheme administrators.</p>
      </div>

      {/* PMFBY Context Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-xl p-5 flex items-start justify-between">
        <div>
          <p className="font-bold text-lg">Pradhan Mantri Fasal Bima Yojana (PMFBY) Risk Engine</p>
          <p className="text-blue-100 text-sm mt-1 max-w-xl">
            This platform helps empaneled insurers and state agriculture departments price risk accurately under El Niño weather anomalies —
            ensuring PMFBY claims are assessed fairly and settled faster for enrolled farmers.
          </p>
        </div>
        <div className="ml-4 flex-shrink-0 bg-white/20 rounded-lg px-4 py-2 text-center">
          <p className="text-xs text-blue-100">Farmer Premium</p>
          <p className="text-2xl font-bold">1.5–2%</p>
          <p className="text-xs text-blue-100">Govt pays rest</p>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Policies Assessed" value={stats?.total_policies || 0} icon={Shield} color="text-indigo-600" bg="bg-indigo-100" />
        <StatCard title="Total Claims Filed" value={stats?.total_claims || 0} icon={FileText} color="text-rose-600" bg="bg-rose-100" />
        <StatCard title="Claim Rate" value={`${stats?.claim_rate_percentage || 0}%`} icon={Activity} color="text-amber-600" bg="bg-amber-100" />
        <StatCard title="Enrolled Farmers" value={stats?.total_farmers || 0} icon={Users} color="text-blue-600" bg="bg-blue-100" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-1">Claims Over Time</h3>
          <p className="text-xs text-slate-500 mb-4">Monthly claim volume — used by insurers to assess reserve adequacy</p>
          <div className="h-56">
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
            ) : <EmptyState message="No claims data. Upload CSV data to begin." />}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800 mb-1">Portfolio Survival Probability</h3>
          <p className="text-xs text-slate-500 mb-4">Cox PH model baseline — probability of no claim over time across portfolio</p>
          <div className="h-56">
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

      {/* Who Uses This Platform */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-base font-semibold text-slate-800 mb-4">Who Uses This Platform</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: Shield, title: "Insurance Companies", desc: "AIC, Bajaj Allianz, HDFC ERGO — use risk scores for premium pricing and reserve allocation under PMFBY.", color: "text-indigo-600", bg: "bg-indigo-50 border-indigo-100" },
            { icon: Users, title: "State Agri Departments", desc: "Track district-level ENSO risk exposure, flag high-risk zones, and plan early intervention before crop failure.", color: "text-blue-600", bg: "bg-blue-50 border-blue-100" },
            { icon: Activity, title: "Agricultural Banks", desc: "Kisan Credit Card (KCC) lenders assess collateral risk before extending crop loans in drought-prone districts.", color: "text-green-600", bg: "bg-green-50 border-green-100" },
          ].map(({ icon: Icon, title, desc, color, bg }) => (
            <div key={title} className={`p-4 rounded-xl border ${bg}`}>
              <Icon className={`w-5 h-5 ${color} mb-2`} />
              <p className="font-semibold text-slate-800 text-sm">{title}</p>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">{desc}</p>
            </div>
          ))}
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
