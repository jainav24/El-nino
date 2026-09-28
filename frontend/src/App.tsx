import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import RiskAssessment from './pages/RiskAssessment';
import SurvivalAnalysis from './pages/SurvivalAnalysis';
import ModelInsights from './pages/ModelInsights';
import DataUpload from './pages/DataUpload';
import ModelTraining from './pages/ModelTraining';
import Analytics from './pages/Analytics';
import Farmers from './pages/Farmers';
import Policies from './pages/Policies';
import Claims from './pages/Claims';
import Weather from './pages/Weather';
import ResearchMethodology from './pages/ResearchMethodology';
import FarmerAdvisory from './pages/FarmerAdvisory';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/data-upload" element={<DataUpload />} />
          <Route path="/model-training" element={<ModelTraining />} />
          <Route path="/risk-assessment" element={<RiskAssessment />} />
          <Route path="/survival-analysis" element={<SurvivalAnalysis />} />
          <Route path="/model-insights" element={<ModelInsights />} />
          {/* Data Management Pages */}
          <Route path="/farmers" element={<Farmers />} />
          <Route path="/policies" element={<Policies />} />
          <Route path="/claims" element={<Claims />} />
          <Route path="/weather" element={<Weather />} />
          <Route path="/methodology" element={<ResearchMethodology />} />
          <Route path="/farmer-advisory" element={<FarmerAdvisory />} />
        </Route>
      </Routes>
    </Router>
  );
}
