import React, { useState, useEffect } from 'react';
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
