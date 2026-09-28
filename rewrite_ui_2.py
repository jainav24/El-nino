import os

FRONTEND_PAGES_DIR = r"c:/Users/Jainav/OneDrive/Desktop/Ty Mini Project/frontend/src/pages"

policies_content = """import React, { useState, useEffect } from 'react';
import { Search, Filter, Loader2, Info, ChevronRight, Shield } from 'lucide-react';
import { coreApi } from '../services/api';

export default function Policies() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    coreApi.getPolicies().then(setPolicies).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Active Policies</h1>
          <p className="text-slate-500">View and manage all active insurance policies across regions.</p>
        </div>
      </div>
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-slate-400" />
          <input type="text" placeholder="Search by policy ID..." className="pl-10 pr-4 py-2 w-full border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
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
                <th className="px-6 py-4 font-medium">Policy ID</th>
                <th className="px-6 py-4 font-medium">Farmer ID</th>
                <th className="px-6 py-4 font-medium">Crop</th>
                <th className="px-6 py-4 font-medium">Region</th>
                <th className="px-6 py-4 font-medium">Premium</th>
                <th className="px-6 py-4 font-medium">Coverage</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? <tr><td colSpan={7} className="px-6 py-12 text-center"><Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" /></td></tr> :
               error ? <tr><td colSpan={7} className="px-6 py-12 text-center text-rose-500">{error}</td></tr> :
               policies.length === 0 ? <tr><td colSpan={7} className="px-6 py-12 text-center text-slate-500"><Shield className="w-8 h-8 text-slate-300 mx-auto mb-2"/>No policies found.</td></tr> :
               policies.map((p, i) => (
                <tr key={i} className="hover:bg-slate-50 cursor-pointer group transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-900">{p.policy_id}</td>
                  <td className="px-6 py-4 text-slate-700">{p.farmer_id}</td>
                  <td className="px-6 py-4"><span className="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-semibold">{p.crop_type}</span></td>
                  <td className="px-6 py-4 text-slate-600">{p.region}</td>
                  <td className="px-6 py-4 font-medium text-slate-800">${p.premium.toFixed(0)}</td>
                  <td className="px-6 py-4 font-medium text-slate-800">${p.insured_amount.toFixed(0)}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-600 hover:text-blue-800 font-medium text-sm opacity-0 group-hover:opacity-100 transition-opacity">View Details</button>
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

claims_content = """import React, { useState, useEffect } from 'react';
import { Search, Filter, Loader2, Info, ChevronRight, FileText } from 'lucide-react';
import { coreApi } from '../services/api';

export default function Claims() {
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    coreApi.getClaims().then(setClaims).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Insurance Claims</h1>
          <p className="text-slate-500">Track and assess agricultural insurance claims.</p>
        </div>
      </div>
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-slate-400" />
          <input type="text" placeholder="Search claims..." className="pl-10 pr-4 py-2 w-full border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
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
                <th className="px-6 py-4 font-medium">Claim ID</th>
                <th className="px-6 py-4 font-medium">Policy ID</th>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium">Reason</th>
                <th className="px-6 py-4 font-medium">Amount</th>
                <th className="px-6 py-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? <tr><td colSpan={6} className="px-6 py-12 text-center"><Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" /></td></tr> :
               error ? <tr><td colSpan={6} className="px-6 py-12 text-center text-rose-500">{error}</td></tr> :
               claims.length === 0 ? <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-500"><FileText className="w-8 h-8 text-slate-300 mx-auto mb-2"/>No claims found.</td></tr> :
               claims.map((c, i) => (
                <tr key={i} className="hover:bg-slate-50 cursor-pointer group transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-900">{c.claim_id}</td>
                  <td className="px-6 py-4 text-blue-600 hover:underline">{c.policy_id}</td>
                  <td className="px-6 py-4 text-slate-600">{c.claim_date}</td>
                  <td className="px-6 py-4 text-slate-600">{c.claim_reason}</td>
                  <td className="px-6 py-4 font-medium text-slate-800">${c.claim_amount.toFixed(0)}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${c.claim_status === 'Approved' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'}`}>
                      {c.claim_status}
                    </span>
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

weather_content = """import React, { useEffect, useState } from 'react';
import { coreApi } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CloudRain, Thermometer, Wind, Droplets } from 'lucide-react';

export default function Weather() {
  const [weather, setWeather] = useState<any[]>([]);
  const [enso, setEnso] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([coreApi.getWeather(), coreApi.getEnso()])
      .then(([w, e]) => { setWeather(w); setEnso(e); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center items-center h-full text-slate-500">Loading Weather & ENSO...</div>;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Weather & ENSO Overview</h1>
        <p className="text-slate-500 mt-1">Climatological drivers of agricultural risk.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border shadow-sm"><div className="flex items-center space-x-3 mb-2"><CloudRain className="text-blue-500"/><h3 className="font-semibold text-slate-700">Avg Rainfall</h3></div><p className="text-3xl font-bold">120<span className="text-sm font-normal text-slate-400 ml-1">mm</span></p></div>
        <div className="bg-white p-6 rounded-xl border shadow-sm"><div className="flex items-center space-x-3 mb-2"><Thermometer className="text-rose-500"/><h3 className="font-semibold text-slate-700">Avg Temp</h3></div><p className="text-3xl font-bold">28.4<span className="text-sm font-normal text-slate-400 ml-1">°C</span></p></div>
        <div className="bg-white p-6 rounded-xl border shadow-sm"><div className="flex items-center space-x-3 mb-2"><Droplets className="text-indigo-500"/><h3 className="font-semibold text-slate-700">Avg Humidity</h3></div><p className="text-3xl font-bold">65<span className="text-sm font-normal text-slate-400 ml-1">%</span></p></div>
        <div className="bg-blue-600 p-6 rounded-xl shadow-md text-white"><div className="flex items-center space-x-3 mb-2"><Wind className="text-blue-200"/><h3 className="font-semibold text-blue-100">Current ENSO</h3></div><p className="text-3xl font-bold">{enso[0]?.enso_phase || 'Unknown'}</p><p className="text-sm mt-1 text-blue-200">ONI: {enso[0]?.oni_value.toFixed(2) || 'N/A'}</p></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-4">Historical Rainfall Trend</h3>
          <div className="h-64">
             {weather.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weather.slice(0,12)}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" tick={{fontSize: 10}} tickFormatter={t=>t.substring(0,7)}/>
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="rainfall" stroke="#3B82F6" strokeWidth={2} dot={false}/>
                </LineChart>
              </ResponsiveContainer>
            ) : <div className="flex items-center justify-center h-full text-slate-400">No data</div>}
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <h3 className="font-semibold text-slate-800 mb-4">What is ENSO?</h3>
          <div className="prose prose-sm text-slate-600">
            <p>The El Niño-Southern Oscillation (ENSO) is a recurring climate pattern involving changes in the temperature of waters in the central and eastern tropical Pacific Ocean. On periods ranging from about three to seven years, the surface waters across a large swath of the tropical Pacific Ocean warm or cool by anywhere from 1°C to 3°C, compared to normal.</p>
            <p className="mt-2 font-medium text-slate-800">What does ONI represent?</p>
            <p>The Oceanic Niño Index (ONI) is NOAA's primary indicator for monitoring the El Niño-Southern Oscillation. It tracks the rolling 3-month average sea surface temperature anomalies. Values above +0.5 indicate El Niño, while values below -0.5 indicate La Niña.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

survival_analysis_content = """import React, { useState, useEffect } from 'react';
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
"""

with open(os.path.join(FRONTEND_PAGES_DIR, "Policies.tsx"), "w", encoding="utf-8") as f: f.write(policies_content)
with open(os.path.join(FRONTEND_PAGES_DIR, "Claims.tsx"), "w", encoding="utf-8") as f: f.write(claims_content)
with open(os.path.join(FRONTEND_PAGES_DIR, "Weather.tsx"), "w", encoding="utf-8") as f: f.write(weather_content)
with open(os.path.join(FRONTEND_PAGES_DIR, "SurvivalAnalysis.tsx"), "w", encoding="utf-8") as f: f.write(survival_analysis_content)

print("Created components 2!")
