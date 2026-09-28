import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Users, Shield, FileText, CloudRain, Activity, Brain, Settings, Database, Server } from 'lucide-react';
import FloatingAssistant from '../FloatingAssistant';

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold tracking-tight text-blue-400">AgriRisk AI</h1>
          <p className="text-xs text-slate-400 mt-1">El Niño Survival Engine</p>
        </div>
        <nav className="flex-1 py-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700">
          <div className="space-y-6">
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Overview</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><LayoutDashboard className="w-5 h-5 mr-3" /> Dashboard</NavLink></li>
                <li><NavLink to="/methodology" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><FileText className="w-5 h-5 mr-3" /> Methodology</NavLink></li>
              </ul>
            </div>
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Data</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/farmers" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Users className="w-5 h-5 mr-3" /> Farmers</NavLink></li>
                <li><NavLink to="/policies" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Shield className="w-5 h-5 mr-3" /> Policies</NavLink></li>
                <li><NavLink to="/claims" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><FileText className="w-5 h-5 mr-3" /> Claims</NavLink></li>
                <li><NavLink to="/data-upload" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Database className="w-5 h-5 mr-3" /> Data Upload</NavLink></li>
                <li><NavLink to="/weather" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><CloudRain className="w-5 h-5 mr-3" /> Weather & ENSO</NavLink></li>
              </ul>
            </div>
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Analysis</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/analytics" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Activity className="w-5 h-5 mr-3" /> Advanced Analytics</NavLink></li>
                <li><NavLink to="/survival-analysis" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Activity className="w-5 h-5 mr-3" /> Survival Analysis</NavLink></li>
                <li><NavLink to="/risk-assessment" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Brain className="w-5 h-5 mr-3" /> Risk Assessment</NavLink></li>
                <li><NavLink to="/model-insights" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Activity className="w-5 h-5 mr-3" /> Cox Insights</NavLink></li>
              </ul>
            </div>
            <div>
              <p className="px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Models</p>
              <ul className="space-y-1 px-3">
                <li><NavLink to="/model-training" className={({ isActive }) => `flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400 font-medium' : 'text-slate-300 hover:bg-slate-800 hover:text-white'}`}><Server className="w-5 h-5 mr-3" /> Model Training</NavLink></li>
              </ul>
            </div>
            
            <div className="px-6 pt-4 pb-2">
              <p className="text-[10px] text-slate-500 leading-tight">
                Disclaimer: This platform provides model-based analytical estimates from the available dataset. Predictions should not be interpreted as guaranteed insurance claim outcomes or official underwriting decisions.
              </p>
            </div>
          </div>
        </nav>
      </aside>
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm z-10">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-slate-800">Platform</h2>
            <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-full border border-amber-300">DEMO DATA</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold">A</div>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-8 bg-slate-50 relative">
          <Outlet />
        </div>
      </main>
      <FloatingAssistant />
    </div>
  );
}
