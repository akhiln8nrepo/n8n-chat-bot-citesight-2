import { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from '@/components/LandingPage';
import Dashboard from '@/components/Dashboard';
import ContentManagement from '@/components/ContentManagement';
import KeywordMonitoring from '@/components/KeywordMonitoring';
import Recommendations from '@/components/Recommendations';
import CompetitorAnalysis from '@/components/CompetitorAnalysis';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/content" element={<ContentManagement />} />
          <Route path="/keywords" element={<KeywordMonitoring />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/competitors" element={<CompetitorAnalysis />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;