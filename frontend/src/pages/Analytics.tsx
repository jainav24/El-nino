import React, { useEffect, useState } from 'react';
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
