import React, { useState } from 'react';
import { Activity, ShieldCheck, Database, RefreshCw, FileText } from 'lucide-react';
import { mlApi } from '../services/api';

export default function ModelInsights() {
  const [training, setTraining] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    try {
      const res = await mlApi.train();
      setReport(res.report);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to train the model. Ensure dataset is available.');
    } finally {
      setTraining(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto print:max-w-none print:m-0 print:p-0">
      <div className="flex justify-between items-end print:hidden">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Cox Proportional Hazards Model</h1>
          <p className="text-slate-500 mt-1">Model interpretability and coefficient analysis.</p>
        </div>
        <div className="flex space-x-3">
          {report && (
            <button
              onClick={handlePrint}
              className="flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
            >
              <FileText className="w-4 h-4 mr-2" />
              Generate Analysis Report
            </button>
          )}
          <button
            onClick={handleTrain}
            disabled={training}
            className="flex items-center px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-70 transition-colors text-sm font-medium"
          >
            {training ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Database className="w-4 h-4 mr-2" />}
            {training ? 'Training...' : 'Retrain Pipeline'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 text-rose-700 rounded-lg border border-rose-200 print:hidden">
          {error}
        </div>
      )}

      {!report && !training && !error && (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm print:hidden">
          <ShieldCheck className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-1">No Model Loaded</h3>
          <p className="text-slate-500 max-w-md mx-auto mb-6">Train the pipeline using the current database records to view the coefficients and hazard ratios.</p>
          <button onClick={handleTrain} className="text-blue-600 bg-blue-50 px-4 py-2 rounded-lg font-medium hover:bg-blue-100 transition-colors">Start Training</button>
        </div>
      )}

      {training && (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm print:hidden">
          <RefreshCw className="w-10 h-10 text-blue-500 mx-auto mb-4 animate-spin" />
          <p className="text-slate-600 font-medium">Extracting features and training Survival Engine...</p>
        </div>
      )}

      {report && (
        <div className="space-y-6 print:hidden">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider mb-2">Concordance Index (C-Index)</h3>
              <div className="flex items-end">
                <span className="text-4xl font-bold text-slate-900">{report.c_index?.toFixed(4)}</span>
                <span className="ml-3 mb-1 text-sm text-emerald-600 font-medium">Model Fit</span>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider mb-2">Dataset Size</h3>
              <div className="flex items-center">
                <span className="text-4xl font-bold text-slate-900">{report.dataset_size}</span>
                <span className="ml-4 text-sm text-slate-600 truncate">Total Records Used</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-200 bg-slate-50">
              <h3 className="text-lg font-semibold text-slate-800">Cox PH Coefficients</h3>
              <p className="text-sm text-slate-500 mt-1">
                <strong>Interpretation:</strong> A Hazard Ratio {">"} 1 indicates a higher estimated hazard relative to the reference, while {"<"} 1 indicates a lower estimated hazard, subject to model assumptions.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Feature</th>
                    <th className="px-6 py-4 font-semibold text-right">Coefficient (β)</th>
                    <th className="px-6 py-4 font-semibold text-right text-blue-600">Hazard Ratio (exp(β))</th>
                    <th className="px-6 py-4 font-semibold text-right">P-value</th>
                  </tr>
                </thead>
                <tbody>
                  {report.summary && report.summary.map((row: any, idx: number) => {
                    const hr = row['exp(coef)'];
                    const p = row['p'];
                    
                    return (
                      <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-900">{row.covariate}</td>
                        <td className="px-6 py-4 text-right">{row.coef.toFixed(4)}</td>
                        <td className={`px-6 py-4 text-right font-bold ${hr > 1 ? 'text-rose-600' : 'text-emerald-600'}`}>{hr.toFixed(4)}x</td>
                        <td className={`px-6 py-4 text-right ${p < 0.05 ? 'font-bold text-slate-900' : 'text-slate-400'}`}>{p < 0.0001 ? '<0.0001' : p.toFixed(4)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Printable Report Section */}
      {report && (
        <div className="hidden print:block font-sans text-slate-900 bg-white p-8">
          <div className="border-b-2 border-slate-900 pb-6 mb-8">
            <h1 className="text-3xl font-bold uppercase tracking-tight">Agricultural Risk Analysis Report</h1>
            <p className="text-slate-500 mt-2 font-medium">Model Evaluation and Statistical Findings</p>
            <p className="text-sm mt-2 font-mono text-slate-400">Generated: {new Date().toLocaleString()}</p>
          </div>

          <div className="grid grid-cols-2 gap-8 mb-8">
            <div className="border border-slate-200 rounded-lg p-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Model Performance</h3>
              <table className="w-full text-sm">
                <tbody>
                  <tr className="border-b border-slate-100"><td className="py-2 text-slate-500">Concordance Index (C-Index)</td><td className="py-2 font-bold text-right">{report.c_index?.toFixed(4)}</td></tr>
                  <tr><td className="py-2 text-slate-500">Dataset Size (Records)</td><td className="py-2 font-bold text-right">{report.dataset_size}</td></tr>
                </tbody>
              </table>
            </div>

            <div className="border border-slate-200 rounded-lg p-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Core Discoveries</h3>
              <ul className="list-disc list-inside space-y-2 text-sm text-slate-700">
                <li>Primary methodology relies on Cox Proportional Hazards mapping ENSO to Time-to-Claim.</li>
                <li>Weather anomalies dynamically scale baseline hazard risk.</li>
                <li>Report uses available demonstration data only.</li>
              </ul>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 mb-4 border-b pb-2">Significant Hazard Drivers (P &lt; 0.05)</h3>
            <table className="w-full text-sm border border-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-left">Covariate</th>
                  <th className="px-4 py-2 text-right">Hazard Ratio</th>
                  <th className="px-4 py-2 text-right">P-Value</th>
                </tr>
              </thead>
              <tbody>
                {report.summary && report.summary.filter((r: any) => r.p < 0.05).map((row: any, idx: number) => (
                  <tr key={idx} className="border-b border-slate-100">
                    <td className="px-4 py-2">{row.covariate}</td>
                    <td className="px-4 py-2 text-right font-bold">{row['exp(coef)'].toFixed(4)}x</td>
                    <td className="px-4 py-2 text-right">{row.p < 0.0001 ? '<0.0001' : row.p.toFixed(4)}</td>
                  </tr>
                ))}
                {report.summary && report.summary.filter((r: any) => r.p < 0.05).length === 0 && (
                  <tr><td colSpan={3} className="px-4 py-4 text-center text-slate-500">No statistically significant drivers found in this dataset subset.</td></tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="mt-16 pt-8 border-t-2 border-slate-200 text-sm text-slate-500 text-justify">
            <p className="font-bold mb-2">LIMITATIONS & DISCLAIMER:</p>
            <p>
              This report provides model-based analytical estimates using the active dataset. 
              Data quality issues, unobserved confounders, and the proportional hazards assumption limit the certainty of these findings.
              Predictions should not be interpreted as guaranteed insurance claim outcomes or official underwriting decisions.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
