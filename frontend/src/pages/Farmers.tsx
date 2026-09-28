import React, { useState, useEffect } from 'react';
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
