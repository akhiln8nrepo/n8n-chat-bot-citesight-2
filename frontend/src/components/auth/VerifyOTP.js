import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Mail, Phone, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VerifyOTP = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [activeTab, setActiveTab] = useState('email'); // 'email' or 'sms'
  const [otpCode, setOtpCode] = useState('');
  
  const { email, phone } = location.state || {};

  useEffect(() => {
    if (!email && !phone) {
      toast.error('No verification info found');
      navigate('/auth/register');
    }
  }, [email, phone, navigate]);

  const handleVerify = async (e) => {
    e.preventDefault();

    if (otpCode.length !== 6) {
      toast.error('Please enter a 6-digit OTP');
      return;
    }

    setLoading(true);

    try {
      const identifier = activeTab === 'email' ? email : phone;
      await axios.post(`${API}/auth/verify-otp`, {
        identifier,
        otp_code: otpCode,
        otp_type: activeTab
      });
      
      toast.success(`${activeTab === 'email' ? 'Email' : 'Phone'} verified successfully!`);
      
      // Navigate to login
      setTimeout(() => {
        navigate('/auth/login');
      }, 1500);
    } catch (error) {
      const message = error.response?.data?.detail || 'Verification failed';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);

    try {
      const identifier = activeTab === 'email' ? email : phone;
      await axios.post(`${API}/auth/resend-otp`, {
        identifier,
        otp_type: activeTab
      });
      
      toast.success('OTP resent successfully!');
    } catch (error) {
      toast.error('Failed to resend OTP');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 to-cyan-50 flex items-center justify-center py-12 px-4" data-testid="verify-otp-page">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CheckCircle size={32} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Verify Your Account</h1>
            <p className="text-slate-600">Enter the OTP sent to your {activeTab}</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              data-testid="email-tab"
              onClick={() => {setActiveTab('email'); setOtpCode('');}}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all ${
                activeTab === 'email'
                  ? 'bg-sky-500 text-white shadow-lg'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Mail size={18} />
              Email
            </button>
            <button
              data-testid="sms-tab"
              onClick={() => {setActiveTab('sms'); setOtpCode('');}}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all ${
                activeTab === 'sms'
                  ? 'bg-sky-500 text-white shadow-lg'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Phone size={18} />
              SMS
            </button>
          </div>

          {/* OTP sent to */}
          <div className="bg-sky-50 border border-sky-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-slate-700">
              OTP sent to: <span className="font-bold">{activeTab === 'email' ? email : phone}</span>
            </p>
          </div>

          {/* OTP Input */}
          <form onSubmit={handleVerify} className="space-y-6">
            <div>
              <label className="form-label">Enter 6-digit OTP</label>
              <input
                data-testid="otp-input"
                type="text"
                value={otpCode}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setOtpCode(value);
                }}
                className="form-input text-center text-2xl tracking-widest"
                placeholder="000000"
                maxLength={6}
              />
              <p className="text-xs text-slate-500 mt-2 text-center">
                Check your {activeTab === 'email' ? 'email inbox' : 'phone messages'} for the OTP
              </p>
            </div>

            <button
              data-testid="verify-button"
              type="submit"
              disabled={loading || otpCode.length !== 6}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Verifying...' : 'Verify OTP'}
            </button>
          </form>

          {/* Resend */}
          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600 mb-2">
              Didn't receive the code?
            </p>
            <button
              data-testid="resend-button"
              onClick={handleResend}
              disabled={resending}
              className="text-sky-600 font-semibold hover:text-sky-700 disabled:opacity-50"
            >
              {resending ? 'Resending...' : 'Resend OTP'}
            </button>
          </div>

          {/* Back to Login */}
          <div className="mt-6 text-center">
            <button
              onClick={() => navigate('/auth/login')}
              className="text-sm text-slate-600 hover:text-slate-900"
              data-testid="back-to-login"
            >
              ← Back to Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyOTP;