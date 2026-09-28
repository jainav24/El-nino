import React, { useState, useEffect } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, Play, Database, FileSpreadsheet, Server } from 'lucide-react';
import { dataApi, dashboardApi } from '../services/api';

export default function DataUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [datasetType, setDatasetType] = useState('weather');
  const [validation, setValidation] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);

  const fetchStats = async () => {
    try {
      const res = await dashboardApi.getStats();
      setStats(res);
    } catch (err) {}
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setValidation(null);
      setError(null);
      setSuccessMsg(null);
    }
  };

  const handleValidate = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setValidation(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_type', datasetType);

    try {
      const res = await dataApi.validateCsv(formData);
      setValidation(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Validation failed');
    } finally {
      setUploading(false);
    }
  };

  const handleStore = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_type', datasetType);

    try {
      const res = await dataApi.storeCsv(formData);
      setSuccessMsg(res.message);
      setFile(null);
      setValidation(null);
      fetchStats();
      // Reset file input
      const input = document.getElementById('file-upload') as HTMLInputElement;
      if (input) input.value = '';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Storage failed');
    } finally {
      setUploading(false);
    }
  };

  const handleSeedDemo = async () => {
    setUploading(true);
    setError(null);
    try {
      const res = await dataApi.seedDemo();
      setSuccessMsg(`Successfully injected demo dataset. Preprocessing completed. Check ML dashboard.`);
      fetchStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to seed demo data');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Data Management & Ingestion</h1>
          <p className="text-slate-500 mt-1">Upload raw CSV files for processing through the ML pipeline.</p>
        </div>
        <button
          onClick={handleSeedDemo}
          disabled={uploading}
          className="flex items-center px-4 py-2 bg-indigo-50 text-indigo-700 font-medium rounded-lg hover:bg-indigo-100 transition-colors"
        >
          <Database className="w-4 h-4 mr-2" />
          Seed Demo Data
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="font-semibold text-slate-800 mb-4 flex items-center">
              <UploadCloud className="w-5 h-5 mr-2 text-blue-500" />
              Upload File
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Dataset Type</label>
                <select 
                  value={datasetType} 
                  onChange={(e) => setDatasetType(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg p-2.5"
                >
                  <option value="weather">Weather Data</option>
                  <option value="enso">ENSO Data</option>
                  <option value="farmers">Agricultural Data (Farmers)</option>
                  <option value="policies">Insurance Policies</option>
                  <option value="claims">Insurance Claims</option>
                  <option value="master_survival">Master Survival Dataset</option>
                </select>
              </div>

              <div className="flex items-center justify-center w-full">
                <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <FileSpreadsheet className="w-8 h-8 mb-2 text-slate-500" />
                    <p className="text-sm text-slate-500 font-medium">{file ? file.name : "Click to upload CSV"}</p>
                  </div>
                  <input id="file-upload" type="file" accept=".csv" className="hidden" onChange={handleFileChange} />
                </label>
              </div>

              <button
                onClick={handleValidate}
                disabled={!file || uploading}
                className="w-full text-white bg-blue-600 hover:bg-blue-700 font-medium rounded-lg text-sm px-5 py-2.5 disabled:opacity-60 transition-colors"
              >
                {uploading ? 'Processing...' : 'Validate CSV'}
              </button>
            </div>
          </div>

          {/* Database Summary */}
          {stats && (
            <div className="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 shadow-sm">
              <h3 className="font-semibold mb-4 flex items-center text-blue-400">
                <Server className="w-5 h-5 mr-2" />
                Database Summary
              </h3>
              <ul className="space-y-3 text-sm">
                <li className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Farmers</span>
                  <span className="font-bold">{stats.total_farmers}</span>
                </li>
                <li className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Policies</span>
                  <span className="font-bold">{stats.total_policies}</span>
                </li>
                <li className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Weather Records</span>
                  <span className="font-bold">{stats.total_weather_records}</span>
                </li>
                <li className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">ENSO Records</span>
                  <span className="font-bold">{stats.total_enso_records}</span>
                </li>
                <li className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Claims</span>
                  <span className="font-bold">{stats.total_claims}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Survival Records</span>
                  <span className="font-bold">{stats.total_survival_records}</span>
                </li>
              </ul>
            </div>
          )}
        </div>

        {/* Validation Section */}
        <div className="lg:col-span-7">
          {error && (
            <div className="mb-4 bg-rose-50 text-rose-700 p-4 rounded-lg flex items-start border border-rose-200">
              <AlertCircle className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          {successMsg && (
            <div className="mb-4 bg-emerald-50 text-emerald-700 p-4 rounded-lg flex items-start border border-emerald-200">
              <CheckCircle className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
              <p>{successMsg}</p>
            </div>
          )}

          {validation && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-200">
                <h3 className="font-semibold text-slate-800 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-emerald-500" />
                  Validation Results
                </h3>
              </div>
              
              <div className="p-6 bg-slate-50 grid grid-cols-2 md:grid-cols-4 gap-4 border-b border-slate-200">
                <div className="bg-white p-4 rounded-lg border border-slate-200 text-center">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Rows</p>
                  <p className="text-2xl font-bold text-slate-900">{validation.row_count}</p>
                </div>
                <div className="bg-white p-4 rounded-lg border border-slate-200 text-center">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Required Missing</p>
                  <p className="text-2xl font-bold text-rose-600">{validation.required_missing ?? validation.missing_values}</p>
                </div>
                <div className="bg-white p-4 rounded-lg border border-slate-200 text-center">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Optional/Censored</p>
                  <p className="text-2xl font-bold text-slate-500">{validation.optional_missing ?? 0}</p>
                </div>
                <div className="bg-white p-4 rounded-lg border border-slate-200 text-center">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Duplicates</p>
                  <p className="text-2xl font-bold text-rose-600">{validation.duplicates}</p>
                </div>
              </div>

              {validation.errors && validation.errors.length > 0 && (
                <div className="p-4 bg-amber-50 border-b border-amber-200">
                  <h4 className="text-sm font-semibold text-amber-800 mb-2">Warnings & Errors</h4>
                  <ul className="list-disc list-inside text-sm text-amber-700">
                    {validation.errors.map((e: string, i: number) => <li key={i}>{e}</li>)}
                  </ul>
                </div>
              )}

              <div className="p-6">
                <h4 className="text-sm font-semibold text-slate-800 mb-3">Preview (First 20 rows)</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="uppercase bg-slate-100 text-slate-500">
                      <tr>
                        {validation.columns.map((col: string) => (
                          <th key={col} className="px-3 py-2 font-medium">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {validation.preview.map((row: any, idx: number) => (
                        <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                          {validation.columns.map((col: string) => (
                            <td key={col} className="px-3 py-2 text-slate-600 whitespace-nowrap">{row[col]}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    onClick={handleStore}
                    disabled={uploading}
                    className="flex items-center px-6 py-2.5 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-60"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Confirm & Store Dataset
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
