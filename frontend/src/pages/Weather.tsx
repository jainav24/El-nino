import React, { useEffect, useState } from 'react';
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
