import React, { useState, useEffect } from 'react';
import { mlApi } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Activity, Server } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function SurvivalAnalysis() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [groupBy, setGroupBy] = useState<string>('enso_phase');

  useEffect(() => {
    setLoading(true);
    mlApi.kaplanMeier(groupBy)
      .then(setData)
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load analysis'))
      .finally(() => setLoading(false));
  }, [groupBy]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Kaplan-Meier Survival Analysis</h1>
          <p className="text-slate-500 mt-1">Non-parametric estimator for policy survival probabilities over time.</p>
        </div>
        <div className="flex items-center space-x-3 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-sm font-medium text-slate-500 pl-3">Compare by:</span>
          <select value={groupBy} onChange={(e) => setGroupBy(e.target.value)} className="bg-slate-50 border-none text-slate-900 text-sm rounded-md py-1.5 px-3 focus:ring-0 cursor-pointer font-medium outline-none">
            <option value="enso_phase">ENSO Phase</option>
            <option value="crop">Crop</option>
            <option value="region">Region</option>
          </select>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-[500px] flex flex-col">
        <h3 className="font-semibold text-slate-800 mb-6">Survival Probability vs Days Since Policy Start</h3>
        <div className="flex-1">
          {loading ? (
            <div className="h-full flex items-center justify-center text-slate-500">Loading curve...</div>
          ) : error ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 bg-slate-50 rounded-lg">
                <Activity className="w-12 h-12 mb-3 text-amber-500 opacity-80" />
                <p className="font-medium text-slate-700">{error}</p>
                <Link to="/model-training" className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors flex items-center">
                  <Server className="w-4 h-4 mr-2" /> Go to Model Training
                </Link>
            </div>
          ) : data && data.timeline ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="time" type="number" domain={['dataMin', 'dataMax']} allowDuplicatedCategory={false} axisLine={false} tickLine={false} tick={{fill: '#64748B'}} label={{ value: 'Days', position: 'insideBottomRight', offset: 0, fill: '#94A3B8' }}/>
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B'}} domain={[0, 1]} label={{ value: 'Survival Probability', angle: -90, position: 'insideLeft', fill: '#94A3B8' }}/>
                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Legend verticalAlign="top" height={36}/>
                {data.groups.map((groupName: string, idx: number) => {
                  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
                  const lineData = data.timeline.map((t: number, i: number) => ({ time: t, probability: data.survival_probabilities[idx][i] }));
                  return <Line key={groupName} data={lineData} type="stepAfter" dataKey="probability" name={groupName} stroke={colors[idx % colors.length]} strokeWidth={3} dot={false} />;
                })}
              </LineChart>
            </ResponsiveContainer>
          ) : <div className="flex items-center justify-center h-full">No data available</div>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800 text-white p-6 rounded-xl shadow-sm">
          <h4 className="font-semibold mb-2 text-slate-300 uppercase text-xs tracking-wider">How to interpret</h4>
          <p className="text-sm text-slate-400 leading-relaxed">
            The Kaplan-Meier curve shows the probability of a policy "surviving" (not having a claim filed) over time. A steeper drop indicates a higher rate of claims being filed at that specific point in time. 
            If the lines for different groups (e.g., El Niño vs Neutral) diverge significantly, it implies that the grouping variable strongly influences risk.
          </p>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
          <h4 className="font-semibold text-slate-800 mb-1">Median Survival Time</h4>
          <p className="text-3xl font-bold text-slate-900 mt-2">N/A <span className="text-sm font-normal text-slate-500">days</span></p>
          <p className="text-xs text-slate-500 mt-2">Time at which 50% of policies file a claim.</p>
        </div>
        <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm flex flex-col justify-center">
           <h4 className="font-semibold text-slate-800 mb-4">Observation Summary</h4>
           <div className="flex justify-between items-center mb-2">
             <span className="text-slate-500">Total Policies:</span>
             <span className="font-bold text-slate-900">{data?.timeline ? 'Loaded' : '--'}</span>
           </div>
        </div>
      </div>
    </div>
  );
}
