import React, { useEffect, useState } from 'react';
import { Database, RefreshCw, Activity, CheckCircle, Clock, Users, FileText, Cloud, AlertTriangle, ShieldCheck } from 'lucide-react';
import { mlApi, dashboardApi } from '../services/api';

export default function ModelTraining() {
  const [training, setTraining] = useState(false);
  const [versions, setVersions] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  const fetchVersions = async () => {
    try {
      const data = await mlApi.getVersions();
      setVersions(data);
    } catch (err: any) {
      console.error(err);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchVersions();
    fetchStats();
  }, []);

  const handleTrain = async (algorithm: string) => {
    setTraining(true);
    setError(null);
    try {
      // Current API trains Cox by default
      await mlApi.train();
      await fetchVersions();
      await fetchStats(); // Refresh stats in case survival dataset size changed
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to train the model. Ensure dataset is available.');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Model Training & Versioning</h1>
          <p className="text-slate-500 mt-1">Manage, train, and deploy survival models.</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => handleTrain('cox')}
            disabled={training}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-70 transition-colors text-sm font-medium"
          >
            {training ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Database className="w-4 h-4 mr-2" />}
            Train Cox Model
          </button>
          <button
            onClick={() => handleTrain('rsf')}
            disabled={training}
            className="flex items-center px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-70 transition-colors text-sm font-medium"
          >
            <Activity className="w-4 h-4 mr-2" />
            Train RSF (Experimental)
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-700 rounded-lg border border-rose-200">
          {error}
        </div>
      )}

      {/* Dataset Summary */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Current Database Readiness</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between">
             <div>
                <p className="text-xs text-slate-500 font-medium uppercase">Farmers</p>
                <p className="text-2xl font-bold text-slate-800">{stats?.total_farmers || 0}</p>
             </div>
             <Users className="w-8 h-8 text-slate-300" />
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between">
             <div>
                <p className="text-xs text-slate-500 font-medium uppercase">Policies</p>
                <p className="text-2xl font-bold text-slate-800">{stats?.total_policies || 0}</p>
             </div>
             <FileText className="w-8 h-8 text-slate-300" />
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between">
             <div>
                <p className="text-xs text-slate-500 font-medium uppercase">Claims</p>
                <p className="text-2xl font-bold text-slate-800">{stats?.total_claims || 0}</p>
             </div>
             <AlertTriangle className="w-8 h-8 text-slate-300" />
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between">
             <div>
                <p className="text-xs text-slate-500 font-medium uppercase">Weather & ENSO</p>
                <p className="text-2xl font-bold text-slate-800">{(stats?.total_weather_records || 0) + (stats?.total_enso_records || 0)}</p>
             </div>
             <Cloud className="w-8 h-8 text-slate-300" />
          </div>
        </div>

        <div className="mt-4 p-4 bg-blue-50/50 rounded-lg border border-blue-100 flex justify-between items-center">
            <div>
               <h4 className="text-sm font-semibold text-blue-900 flex items-center"><ShieldCheck className="w-4 h-4 mr-1"/> Computed Survival Records</h4>
               <p className="text-xs text-blue-700 mt-1">Generated by backend pipeline from joined policies.</p>
            </div>
            <div className="flex space-x-6 text-right">
               <div>
                  <p className="text-xs text-blue-500 font-medium uppercase">Total</p>
                  <p className="text-lg font-bold text-blue-900">{stats?.total_survival_records || 0}</p>
               </div>
               <div>
                  <p className="text-xs text-rose-500 font-medium uppercase">Events (Claimed)</p>
                  <p className="text-lg font-bold text-rose-700">{stats?.total_events || 0}</p>
               </div>
               <div>
                  <p className="text-xs text-emerald-600 font-medium uppercase">Censored (No Claim)</p>
                  <p className="text-lg font-bold text-emerald-700">{stats?.total_censored || 0}</p>
               </div>
            </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200 bg-slate-50">
          <h3 className="text-lg font-semibold text-slate-800">Model Registry</h3>
          <p className="text-sm text-slate-500 mt-1">
            Compare model versions and activate the best performing model for predictions.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-semibold">Version ID</th>
                <th className="px-6 py-4 font-semibold">Algorithm</th>
                <th className="px-6 py-4 font-semibold text-right">Dataset Size</th>
                <th className="px-6 py-4 font-semibold text-right text-blue-600">C-Index</th>
                <th className="px-6 py-4 font-semibold">Trained At</th>
                <th className="px-6 py-4 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              {versions.map((v) => (
                <tr key={v.id} className={`border-b border-slate-100 hover:bg-slate-50 transition-colors ${v.is_active ? 'bg-blue-50/30' : ''}`}>
                  <td className="px-6 py-4 font-medium text-slate-900">{v.version}</td>
                  <td className="px-6 py-4 text-slate-600">{v.algorithm}</td>
                  <td className="px-6 py-4 text-right text-slate-600">{v.dataset_size}</td>
                  <td className="px-6 py-4 text-right font-bold text-slate-900">{v.c_index?.toFixed(4)}</td>
                  <td className="px-6 py-4 text-slate-500 flex items-center">
                    <Clock className="w-4 h-4 mr-2 opacity-50" />
                    {new Date(v.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {v.is_active ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        <CheckCircle className="w-3 h-3 mr-1" /> Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                        Archived
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {versions.length === 0 && !training && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No models trained yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
