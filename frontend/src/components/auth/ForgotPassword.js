import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Key, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [identifier, setIdentifier] = useState('');
  const [step, setStep] = useState(1);
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSendOTP = async (e) => {
    e.preventDefault();
    if (!identifier) { toast.error('Please enter your email or phone number'); return; }
    setLoading(true);
    try {
      await axios.post(`${API}/auth/forgot-password`, { identifier });
      toast.success('Password reset codes sent to your email and phone!');
      setStep(2);
    } catch (error) {
      toast.error('Failed to send reset code');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (otpCode.length !== 6) { toast.error('Please enter the 6-digit OTP'); return; }
    if (newPassword !== confirmPassword) { toast.error('Passwords do not match'); return; }
    if (newPassword.length < 8) { toast.error('Password must be at least 8 characters'); return; }
    setLoading(true);
    try {
      await axios.post(`${API}/auth/reset-password`, { identifier, otp_code: otpCode, new_password: newPassword });
      toast.success('Password reset successful! Please login.');
      setTimeout(() => navigate('/auth/login'), 1500);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Password reset failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 to-cyan-50 flex items-center justify-center py-12 px-4" data-testid="forgot-password-page">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Key size={32} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Reset Password</h1>
            <p className="text-slate-600">{step === 1 ? 'Enter your email or phone to receive reset code' : 'Enter OTP and new password'}</p>
          </div>

          {step === 1 ? (
            <form onSubmit={handleSendOTP} className="space-y-6">
              <div>
                <label className="form-label">Email or Phone Number</label>
                <input data-testid="identifier-input" type="text" value={identifier} onChange={(e) => setIdentifier(e.target.value)} className="form-input" placeholder="john@example.com or +1234567890" />
              </div>
              <button data-testid="send-otp-button" type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed">
                {loading ? 'Sending...' : 'Send Reset Code'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="space-y-6">
              <div>
                <label className="form-label">Enter 6-digit OTP</label>
                <input data-testid="otp-input" type="text" value={otpCode} onChange={(e) => { const value = e.target.value.replace(/\D/g, '').slice(0, 6); setOtpCode(value); }} className="form-input text-center text-2xl tracking-widest" placeholder="000000" maxLength={6} />
              </div>
              <div>
                <label className="form-label">New Password</label>
                <input data-testid="new-password-input" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} className="form-input" placeholder="Enter new password" />
                <p className="text-xs text-slate-500 mt-1">Min 8 characters with uppercase, lowercase, number & special character</p>
              </div>
              <div>
                <label className="form-label">Confirm Password</label>
                <input data-testid="confirm-password-input" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="form-input" placeholder="Confirm new password" />
              </div>
              <button data-testid="reset-button" type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed">
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>
          )}

          <div className="mt-6 text-center">
            <button onClick={() => navigate('/auth/login')} className="text-sm text-slate-600 hover:text-slate-900 flex items-center justify-center gap-2 mx-auto" data-testid="back-to-login">
              <ArrowLeft size={16} />Back to Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;