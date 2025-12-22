import { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from '@/pages/Home';
import About from '@/pages/About';
import Features from '@/pages/Features';
import Pricing from '@/pages/Pricing';
import Contact from '@/pages/Contact';
import Logout from '@/pages/Logout';
import Dashboard from '@/components/Dashboard';
import PromptMonitoring from '@/components/PromptMonitoring';
import Register from '@/components/auth/Register';
import Login from '@/components/auth/Login';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/home" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/features" element={<Features />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/logout" element={<Logout />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/prompts" element={<PromptMonitoring />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;