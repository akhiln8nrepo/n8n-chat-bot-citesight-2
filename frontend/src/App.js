import { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from '@/pages/Home';
import Dashboard from '@/components/Dashboard';
import ContentManagement from '@/components/ContentManagement';
import KeywordMonitoring from '@/components/KeywordMonitoring';
import Recommendations from '@/components/Recommendations';
import CompetitorAnalysis from '@/components/CompetitorAnalysis';
import Register from '@/components/auth/Register';
import Login from '@/components/auth/Login';
import VerifyOTP from '@/components/auth/VerifyOTP';
import ForgotPassword from '@/components/auth/ForgotPassword';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/home" element={<Home />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/verify" element={<VerifyOTP />} />
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
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