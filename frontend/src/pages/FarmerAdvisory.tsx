import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Info, Leaf, MapPin, Droplets, ThumbsUp, ExternalLink, Phone, ChevronRight, CloudRain, Sun, Wind } from 'lucide-react';
import { advisoryApi } from '../services/api';

const STATES = ['Andhra Pradesh', 'Karnataka', 'Madhya Pradesh', 'Maharashtra', 'Punjab', 'Uttar Pradesh'];
const CROPS  = ['Cotton', 'Maize', 'Rice', 'Soybean', 'Sugarcane', 'Wheat'];
const SEASONS = ['Kharif', 'Rabi', 'Zaid'];

const RISK_STYLES: Record<string, { bg: string; border: string; text: string; badge: string; icon: React.ReactNode }> = {
  HIGH:         { bg: 'bg-red-50',    border: 'border-red-300',    text: 'text-red-800',    badge: 'bg-red-100 text-red-800 border-red-300',    icon: <AlertTriangle className="w-6 h-6 text-red-600" /> },
  'MEDIUM-HIGH':{ bg: 'bg-orange-50', border: 'border-orange-300', text: 'text-orange-800', badge: 'bg-orange-100 text-orange-800 border-orange-300', icon: <AlertTriangle className="w-6 h-6 text-orange-500" /> },
  MEDIUM:       { bg: 'bg-yellow-50', border: 'border-yellow-300', text: 'text-yellow-800', badge: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: <Info className="w-6 h-6 text-yellow-600" /> },
  'LOW-MEDIUM': { bg: 'bg-blue-50',   border: 'border-blue-300',   text: 'text-blue-800',   badge: 'bg-blue-100 text-blue-800 border-blue-300',   icon: <Info className="w-6 h-6 text-blue-500" /> },
  LOW:          { bg: 'bg-green-50',  border: 'border-green-300',  text: 'text-green-800',  badge: 'bg-green-100 text-green-800 border-green-300',  icon: <CheckCircle className="w-6 h-6 text-green-600" /> },
};

const ENSO_PHASE_STYLES: Record<string, { color: string; bg: string; icon: React.ReactNode }> = {
  'El Nino': { color: 'text-orange-700', bg: 'bg-orange-50 border-orange-200', icon: <Sun className="w-5 h-5 text-orange-500" /> },
  'La Nina': { color: 'text-blue-700',   bg: 'bg-blue-50 border-blue-200',     icon: <CloudRain className="w-5 h-5 text-blue-500" /> },
  'Neutral': { color: 'text-green-700',  bg: 'bg-green-50 border-green-200',   icon: <Wind className="w-5 h-5 text-green-500" /> },
};

export default function FarmerAdvisory() {
  const [state,   setState]   = useState('Maharashtra');
  const [crop,    setCrop]    = useState('Rice');
  const [season,  setSeason]  = useState('Kharif');
  const [result,  setResult]  = useState<any>(null);
  const [enso,    setEnso]    = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  // Load current ENSO status on mount
  useEffect(() => {
    advisoryApi.getEnsoStatus()
      .then(setEnso)
      .catch(() => null);
  }, []);

  const handleGetAdvisory = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await advisoryApi.getAdvisory(state, crop, season);
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to fetch advisory. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const riskStyle = result ? (RISK_STYLES[result.risk?.level] || RISK_STYLES['MEDIUM']) : null;
  const ensoStyle = enso ? (ENSO_PHASE_STYLES[enso.enso_phase] || ENSO_PHASE_STYLES['Neutral']) : null;

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <div className="flex items-center space-x-3 mb-1">
          <div className="p-2 bg-green-100 rounded-lg">
            <Leaf className="w-6 h-6 text-green-700" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Farmer Risk Advisory</h1>
            <p className="text-slate-500 text-sm">Free, publicly accessible. No login required.</p>
          </div>
        </div>
        <p className="text-slate-600 mt-2 text-sm leading-relaxed bg-green-50 border border-green-200 rounded-lg p-3">
          This advisory helps farmers and agricultural extension workers understand El Niño related crop risks and take preventive action —
          even before filing an insurance claim. Powered by the AgriRisk AI survival analysis model.
        </p>
      </div>

      {/* Live ENSO Status Banner */}
      {enso && ensoStyle && (
        <div className={`flex items-center justify-between p-4 rounded-xl border ${ensoStyle.bg}`}>
          <div className="flex items-center space-x-3">
            {ensoStyle.icon}
            <div>
              <p className={`font-semibold ${ensoStyle.color}`}>Current Global ENSO: {enso.enso_label}</p>
              <p className="text-xs text-slate-500">ONI Index: {enso.oni_value > 0 ? '+' : ''}{enso.oni_value} · Source: {enso.data_source}</p>
            </div>
          </div>
          <span className={`text-xs font-bold px-3 py-1 rounded-full border ${ensoStyle.bg} ${ensoStyle.color}`}>
            India Kharif Risk: {enso.risk_to_india_kharif}
          </span>
        </div>
      )}

      {/* Input Form */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Get Advisory for Your Farm</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              <MapPin className="w-4 h-4 inline mr-1 text-slate-400" />State
            </label>
            <select
              id="advisory-state"
              value={state}
              onChange={e => setState(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
            >
              {STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              <Leaf className="w-4 h-4 inline mr-1 text-slate-400" />Crop Type
            </label>
            <select
              id="advisory-crop"
              value={crop}
              onChange={e => setCrop(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
            >
              {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              <Droplets className="w-4 h-4 inline mr-1 text-slate-400" />Season
            </label>
            <select
              id="advisory-season"
              value={season}
              onChange={e => setSeason(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
            >
              {SEASONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>
        <button
          id="get-advisory-btn"
          onClick={handleGetAdvisory}
          disabled={loading}
          className="w-full md:w-auto px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Fetching Advisory...
            </>
          ) : (
            <>Get Advisory <ChevronRight className="w-4 h-4 ml-1" /></>
          )}
        </button>
        {error && (
          <p className="mt-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
        )}
      </div>

      {/* Result */}
      {result && result.success && riskStyle && (
        <div className="space-y-4 animate-in fade-in duration-300">

          {/* Risk Level Banner */}
          <div className={`rounded-xl border-2 p-5 ${riskStyle.bg} ${riskStyle.border}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                {riskStyle.icon}
                <div>
                  <p className={`font-bold text-lg ${riskStyle.text}`}>
                    {result.risk.level} RISK
                  </p>
                  <p className={`text-sm ${riskStyle.text} opacity-80`}>
                    {result.location.state} · {result.crop.type} · {result.crop.season}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-3xl font-bold ${riskStyle.text}`}>
                  {Math.round(result.risk.claim_probability_estimate * 100)}%
                </p>
                <p className={`text-xs ${riskStyle.text} opacity-70`}>Est. claim probability</p>
              </div>
            </div>
            <p className={`mt-3 text-sm leading-relaxed ${riskStyle.text}`}>
              {result.advisory.summary}
            </p>
          </div>

          {/* Zone & Model Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center">
                <MapPin className="w-4 h-4 mr-2 text-slate-400" />Location Context
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">State</span>
                  <span className="font-medium text-slate-800">{result.location.state}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">PMFBY Zone</span>
                  <span className="font-medium text-slate-800 text-right">{result.location.pmfby_zone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">El Niño Vulnerability</span>
                  <span className={`font-bold ${result.location.el_nino_vulnerability === 'High' ? 'text-red-600' : result.location.el_nino_vulnerability === 'Medium' ? 'text-yellow-600' : 'text-green-600'}`}>
                    {result.location.el_nino_vulnerability}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Current ENSO</span>
                  <span className="font-medium text-orange-700">{result.enso.label} (ONI: {result.enso.oni_value > 0 ? '+' : ''}{result.enso.oni_value})</span>
                </div>
              </div>
            </div>

            {/* PMFBY Info */}
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center">
                <Info className="w-4 h-4 mr-2 text-slate-400" />PMFBY Insurance Info
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Your Premium Share</span>
                  <span className="font-bold text-green-700">{result.pmfby.premium_farmer_share}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Enrollment Cutoff</span>
                  <span className="font-medium text-slate-800 text-right">{result.pmfby.enrollment_cutoff}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Helpline</span>
                  <a href={`tel:${result.pmfby.helpline}`} className="font-medium text-blue-600 flex items-center">
                    <Phone className="w-3 h-3 mr-1" />{result.pmfby.helpline}
                  </a>
                </div>
                <a
                  href={result.pmfby.info_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center w-full mt-2 py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Visit PMFBY Portal <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>
            </div>
          </div>

          {/* Recommended Actions */}
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="text-base font-semibold text-slate-800 mb-1 flex items-center">
              <ThumbsUp className="w-4 h-4 mr-2 text-green-600" />Recommended Actions
            </h3>
            <p className="text-xs text-slate-500 mb-4">{result.advisory.risk_note}</p>
            <ul className="space-y-3">
              {result.advisory.recommended_actions.map((action: string, i: number) => (
                <li key={i} className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 text-green-700 text-xs font-bold flex items-center justify-center mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-sm text-slate-700 leading-relaxed">{action}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Disclaimer */}
          <p className="text-xs text-slate-400 bg-slate-50 border border-slate-200 rounded-lg p-3 leading-relaxed">
            ⚠️ {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
