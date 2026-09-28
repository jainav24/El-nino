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
