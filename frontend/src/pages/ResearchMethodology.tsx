import React from 'react';
import { Database, Activity, Map, Settings, Play, CheckCircle } from 'lucide-react';

export default function ResearchMethodology() {
  const steps = [
    {
      title: '1. Data Collection',
      desc: 'Agricultural records, historical insurance claims, ONI indices (ENSO), and weather station anomalies are aggregated into a unified repository.',
      icon: <Database className="w-6 h-6 text-blue-500" />
    },
    {
      title: '2. Preprocessing & Feature Engineering',
      desc: 'Missing values are handled. Climate anomalies are calculated. Categorical variables (crop, region) are dummy-encoded. Interaction terms (e.g. ENSO × Rainfall) are generated.',
      icon: <Settings className="w-6 h-6 text-emerald-500" />
    },
    {
      title: '3. Survival Dataset Construction',
      desc: 'Each policy is transformed into a survival timeline: Duration (time-to-claim or censoring) and Event (Claim Occurred = 1, Censored = 0).',
      icon: <Map className="w-6 h-6 text-amber-500" />
    },
    {
      title: '4. Non-Parametric Estimation (Kaplan-Meier)',
      desc: 'Base survival probabilities are estimated across distinct groups (e.g., El Niño vs La Niña) to observe macroscopic differences without covariate interference.',
      icon: <Activity className="w-6 h-6 text-purple-500" />
    },
    {
      title: '5. Semi-Parametric Modeling (Cox PH)',
      desc: 'A Cox Proportional Hazards model is fitted using a penalized maximum likelihood approach. Hazard ratios for continuous covariates are extracted.',
      icon: <Play className="w-6 h-6 text-rose-500" />
    },
    {
      title: '6. Real-Time Risk Prediction',
      desc: 'The trained model receives new policy applications, calculates partial hazards, and emits a predictive survival curve and overall risk category.',
      icon: <CheckCircle className="w-6 h-6 text-indigo-500" />
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Research Methodology</h1>
        <p className="text-slate-500 mt-2 max-w-2xl">
          This platform utilizes Survival Analysis (Time-to-Event Modeling) to estimate the probability and timing of agricultural insurance claims driven by climatological phenomena such as the El Niño-Southern Oscillation (ENSO).
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
        <h2 className="text-lg font-bold text-slate-800 mb-6">Analytical Pipeline</h2>
        
        <div className="relative border-l-2 border-slate-200 ml-3 space-y-8">
          {steps.map((step, idx) => (
            <div key={idx} className="relative pl-8">
              <div className="absolute -left-[17px] top-1 bg-white p-1 rounded-full border-2 border-slate-200">
                {step.icon}
              </div>
              <h3 className="font-semibold text-slate-800 text-lg">{step.title}</h3>
              <p className="text-slate-600 mt-1">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
          <h3 className="font-bold text-slate-800 mb-3">Core Inputs</h3>
          <ul className="list-disc list-inside space-y-2 text-slate-600">
            <li>Meteorological Anomalies (Rainfall, Temp)</li>
            <li>ENSO Oceanic Niño Index (ONI)</li>
            <li>Agricultural Variables (Crop, Area, Soil)</li>
            <li>Insurance Policy Timelines</li>
          </ul>
        </div>
        <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
          <h3 className="font-bold text-slate-800 mb-3">Model Outputs</h3>
          <ul className="list-disc list-inside space-y-2 text-slate-600">
            <li>Dynamic Survival Probability Function</li>
            <li>Relative Hazard Ratios (Risk Multipliers)</li>
            <li>Statistical Feature Significance (p-values)</li>
            <li>Categorical Risk Estimations (Low/Medium/High)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
