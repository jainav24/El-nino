import React, { useState, useEffect } from 'react';
import { mlApi, coreApi } from '../services/api';
import { Brain, AlertCircle, ShieldAlert, CheckCircle, Activity, Printer, Search, Calendar, CloudRain, Sun, Droplets, Wind, TrendingUp, IndianRupee, ShieldCheck } from 'lucide-react';

export default function RiskAssessment() {
  const [loadingRisk, setLoadingRisk] = useState(false);
  const [loadingQuote, setLoadingQuote] = useState(false);
  const [fetching, setFetching] = useState(false);

  const [riskResult, setRiskResult] = useState<any>(null);
  const [quoteResult, setQuoteResult] = useState<any>(null);

  const [error, setError] = useState<string | null>(null);
  const [policies, setPolicies] = useState<any[]>([]);

  const [formData, setFormData] = useState({
    farmer_id: '',
    policy_id: '',
    region: 'North',
    crop_type: 'Wheat',
    farm_area_acres: 1.0,
    soil_type: 'Loam',
    irrigation: 'Rainfed',
    policy_start: '',
    policy_end: '',
    duration_months: 6,
    sum_insured: 200000,
    premium_rate: 2.0,
    
    // Environmental
    rainfall_mm: 100,
    rainfall_anomaly_pct: 0,
    temperature_c: 25,
    temp_anomaly_c: 0,
    humidity_pct: 60,
    drought_index: 0,
    
    // ENSO
    enso_phase: 'Neutral',
    oni: 0.0,
    enso_intensity: 'Neutral'
  });

  useEffect(() => {
    coreApi.getPolicies().then(res => {
      setPolicies(res || []);
    }).catch(err => {
      console.error("Failed to load policies", err);
    });
  }, []);

  const handlePolicySelect = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const pId = e.target.value;
    if (!pId) return;

    setFetching(true);
    try {
      const context = await mlApi.getPolicyContext(pId);
      setFormData(prev => ({
        ...prev,
        ...context // Auto-loads mapped fields from policy DB
      }));
      setRiskResult(null);
      setQuoteResult(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch policy details.");
    } finally {
      setFetching(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCalculateRisk = async () => {
    setLoadingRisk(true);
    setError(null);
    try {
      const data = await mlApi.predict(formData);
      setRiskResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate risk prediction. Ensure model is trained.');
    } finally {
      setLoadingRisk(false);
    }
  };

  const getRiskColor = (category: string) => {
    switch (category) {
      case 'LOW': return 'text-emerald-600 bg-emerald-50/50 border-emerald-200';
      case 'MEDIUM': return 'text-amber-600 bg-amber-50/50 border-amber-200';
      case 'HIGH': return 'text-rose-600 bg-rose-50/50 border-rose-200';
      default: return 'text-slate-600 bg-slate-50 border-slate-200';
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Individual Risk Assessment</h1>
          <p className="text-slate-500 mt-2 font-medium">Insurance Quotation & Survival Analysis Engine</p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 p-4 rounded-xl border border-rose-200 flex items-center">
          <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}



      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* 1. INSURANCE QUOTE */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
          <div className="mb-5">
            <h3 className="text-lg font-bold text-slate-800 flex items-center">
              <ShieldCheck className="w-5 h-5 mr-2 text-emerald-500" />
              1. Insurance Quote
            </h3>
            <p className="text-sm text-slate-500 mt-1">Calculate the estimated premium for the selected insurance coverage.</p>
          </div>

          <div className="space-y-4 flex-grow">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Sum Insured (₹)</label>
              <input
                type="number"
                name="sum_insured"
                value={formData.sum_insured}
                onChange={handleChange}
                min="1"
                className="w-full bg-slate-50 border border-slate-200 text-slate-900 font-medium rounded-xl p-3 focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Policy Duration</label>
                <select
                  name="duration_months"
                  value={formData.duration_months}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500"
                >
                  <option value={3}>3 Months</option>
                  <option value={6}>6 Months</option>
                  <option value={9}>9 Months</option>
                  <option value={12}>12 Months</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Crop Type</label>
                <select
                  name="crop_type"
                  value={formData.crop_type}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="Wheat">Wheat</option>
                  <option value="Rice">Rice</option>
                  <option value="Cotton">Cotton</option>
                  <option value="Maize">Maize</option>
                  <option value="Sugarcane">Sugarcane</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Region</label>
                <select
                  name="region"
                  value={formData.region}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="North">North</option>
                  <option value="South">South</option>
                  <option value="East">East</option>
                  <option value="West">West</option>
                  <option value="Central">Central</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Configured Premium Rate (%)</label>
                <input
                  type="text"
                  inputMode="decimal"
                  name="premium_rate"
                  value={formData.premium_rate}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div className="mt-6 p-5 bg-gradient-to-br from-emerald-900 to-emerald-800 rounded-xl text-white shadow-md text-center animate-in fade-in zoom-in duration-300">
              <p className="text-emerald-200 text-sm uppercase tracking-widest font-semibold mb-1">Estimated Premium</p>
              <div className="text-4xl font-black">₹{((Number(formData.sum_insured) || 0) * (Number(formData.premium_rate) || 0) / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              <p className="text-xs text-emerald-300/80 mt-2">
                For ₹{(Number(formData.sum_insured) || 0).toLocaleString('en-IN')} coverage at {formData.premium_rate}% configured rate.
              </p>
            </div>

            <div className="text-[10px] text-slate-400 leading-tight mt-2 text-center">
              Premium shown is an estimated value based on the configured premium rate. Actual premium may vary according to the applicable insurance scheme, policy terms, crop, region and underwriting rules.
            </div>

          </div>
        </div>

        <div className="flex flex-col gap-6">
          {/* 2. WEATHER & ENVIRONMENTAL FACTORS */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col relative">
            {formData.policy_id && <span className="absolute top-4 right-4 bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">From Weather Data</span>}
            <div className="mb-5">
              <h3 className="text-lg font-bold text-slate-800 flex items-center">
                <CloudRain className="w-5 h-5 mr-2 text-emerald-500" />
                2. Weather & Environmental Factors
              </h3>
              <p className="text-sm text-slate-500 mt-1">Modify environmental scenario values for "what-if" risk analysis.</p>
            </div>
            
            <div className="space-y-4 flex-grow opacity-90">
               <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Rainfall (mm)</label>
                    <input type="text" inputMode="decimal" name="rainfall_mm" value={formData.rainfall_mm} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Rainfall Anomaly (%)</label>
                    <input type="text" inputMode="decimal" name="rainfall_anomaly_pct" value={formData.rainfall_anomaly_pct} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Temperature (°C)</label>
                    <input type="text" inputMode="decimal" name="temperature_c" value={formData.temperature_c} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Temp Anomaly (°C)</label>
                    <input type="text" inputMode="decimal" name="temp_anomaly_c" value={formData.temp_anomaly_c} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Humidity (%)</label>
                    <input type="text" inputMode="decimal" name="humidity_pct" value={formData.humidity_pct} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Drought Index</label>
                    <input type="text" inputMode="decimal" name="drought_index" value={formData.drought_index} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-emerald-500" />
                  </div>
                </div>
            </div>
          </div>

          {/* 3. ENSO / EL NIÑO CONDITIONS */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col relative">
            {formData.policy_id && <span className="absolute top-4 right-4 bg-orange-100 text-orange-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">From ENSO Data</span>}
            <div className="mb-5">
              <h3 className="text-lg font-bold text-slate-800 flex items-center">
                <Sun className="w-5 h-5 mr-2 text-orange-500" />
                3. ENSO / El Niño Conditions
              </h3>
              <p className="text-sm text-slate-500 mt-1">Adjust oceanic anomalies to observe macro-climate impact on risk.</p>
            </div>
            
            <div className="space-y-4 flex-grow opacity-90">
               <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-semibold text-slate-700 mb-1">ENSO Phase</label>
                    <select name="enso_phase" value={formData.enso_phase} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-orange-500">
                      <option value="El Niño">El Niño</option>
                      <option value="Neutral">Neutral</option>
                      <option value="La Niña">La Niña</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">ONI (Oceanic Niño Index)</label>
                    <input type="text" inputMode="decimal" name="oni" value={formData.oni} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-orange-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">ENSO Intensity</label>
                    <select name="enso_intensity" value={formData.enso_intensity} onChange={handleChange} className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-xl p-3 focus:ring-2 focus:ring-orange-500">
                      <option value="Weak">Weak</option>
                      <option value="Moderate">Moderate</option>
                      <option value="Strong">Strong</option>
                      <option value="Neutral">Neutral</option>
                    </select>
                  </div>
                </div>

                {/* Action Button Section 5: Risk Assessment Trigger */}
                <button
                  onClick={handleCalculateRisk}
                  disabled={loadingRisk}
                  className="w-full mt-8 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-bold rounded-xl text-sm px-5 py-3 text-center transition-all disabled:opacity-70 flex justify-center items-center shadow-sm"
                >
                  {loadingRisk ? <Activity className="w-5 h-5 animate-spin mr-2" /> : <Brain className="w-5 h-5 mr-2" />}
                  {loadingRisk ? 'Running Cox PH Model...' : 'Calculate Estimated Risk'}
                </button>
            </div>
          </div>
        </div>

      </div>

      {/* 4. RISK RESULT */}
      {riskResult && (
        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center border-b pb-4">
            <TrendingUp className="w-6 h-6 mr-2 text-indigo-600" />
            4. Risk Assessment Result
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

            {/* Risk Level Overview */}
            <div className={`p-6 rounded-2xl border flex flex-col justify-center items-center text-center shadow-sm transition-all ${getRiskColor(riskResult.risk_category)}`}>
              <p className="text-sm font-bold uppercase tracking-widest opacity-80 mb-2">Claim Risk Level</p>
              <h2 className="text-5xl font-black tracking-tight">{riskResult.risk_category}</h2>
              <div className="mt-4 bg-white/60 backdrop-blur-sm px-4 py-2 rounded-xl shadow-sm border border-black/5 inline-block">
                <p className="text-[10px] uppercase font-bold tracking-wider opacity-70 mb-0.5">Estimated Hazard</p>
                <p className="text-2xl font-black">{riskResult.hazard_ratio ? riskResult.hazard_ratio.toFixed(2) : (riskResult.relative_hazard ? riskResult.relative_hazard.toFixed(2) : '1.00')}×</p>
              </div>
            </div>

            {/* Survival Probability */}
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
              <h4 className="font-bold text-slate-800 mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-indigo-500" />
                Survival Probability
              </h4>
              <div className="space-y-3">
                {Object.entries(riskResult.survival_probabilities).map(([days, prob]: [string, any]) => (
                  <div key={days} className="flex justify-between items-center p-3 bg-white rounded-xl border border-slate-200 shadow-sm">
                    <span className="text-sm font-semibold text-slate-600 uppercase tracking-wider">{days.replace('_', ' ')}</span>
                    <span className="text-lg font-bold text-indigo-700">{(prob * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Factors */}
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
              <h4 className="font-bold text-slate-800 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-rose-500" />
                Key Risk Factors
              </h4>
              <div className="space-y-3">
                {riskResult.risk_factors && riskResult.risk_factors.map((factor: any, i: number) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-white rounded-xl border border-slate-200 shadow-sm">
                    <span className="text-sm font-medium text-slate-700 truncate mr-2" title={factor.factor}>{factor.factor}</span>
                    <span className="text-sm font-bold text-rose-600 bg-rose-50 px-2 py-1 rounded-md border border-rose-100">HR: {factor.hazard_ratio.toFixed(2)}</span>
                  </div>
                ))}
                {(!riskResult.risk_factors || riskResult.risk_factors.length === 0) && (
                  <p className="text-sm text-slate-500 p-4 text-center">No dominant risk factors identified.</p>
                )}
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
