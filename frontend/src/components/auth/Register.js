import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Eye, EyeOff, User, Mail, Briefcase } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Register = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', email: '', phone: '', password: '',
    business_name: '', business_type: '', gst_tax_id: '', notes: ''
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Invalid email';
    if (!/^[+]?[0-9]{10,15}$/.test(formData.phone.replace(/[\s-]/g, ''))) newErrors.phone = 'Invalid phone';
    if (formData.password.length < 8 || !/[A-Z]/.test(formData.password) || !/[a-z]/.test(formData.password) || !/[0-9]/.test(formData.password) || !/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)) {
      newErrors.password = 'Password must be 8+ chars with uppercase, lowercase, number & special char';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) { toast.error('Please fix form errors'); return; }
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/register`, formData);
      toast.success('Registration successful! Please verify your email or phone.');
      navigate('/auth/verify', { state: { email: response.data.email, phone: response.data.phone, user_id: response.data.user_id }});
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 to-cyan-50 flex items-center justify-center py-12 px-4" data-testid="register-page">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Create Account</h1>
            <p className="text-slate-600">Join CiteSight to monitor your AI visibility</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2"><User size={20} className="text-sky-600" />Personal Information</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">First Name *</label>
                  <input data-testid="first-name-input" type="text" name="first_name" value={formData.first_name} onChange={handleChange} className={`form-input ${errors.first_name ? 'border-red-500' : ''}`} placeholder="John" />
                  {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>}
                </div>
                <div>
                  <label className="form-label">Last Name *</label>
                  <input data-testid="last-name-input" type="text" name="last_name" value={formData.last_name} onChange={handleChange} className={`form-input ${errors.last_name ? 'border-red-500' : ''}`} placeholder="Doe" />
                  {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>}
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2"><Mail size={20} className="text-sky-600" />Contact Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Email *</label>
                  <input data-testid="email-input" type="email" name="email" value={formData.email} onChange={handleChange} className={`form-input ${errors.email ? 'border-red-500' : ''}`} placeholder="john@example.com" />
                  {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                </div>
                <div>
                  <label className="form-label">Phone Number *</label>
                  <input data-testid="phone-input" type="tel" name="phone" value={formData.phone} onChange={handleChange} className={`form-input ${errors.phone ? 'border-red-500' : ''}`} placeholder="+1234567890" />
                  {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
                </div>
                <div>
                  <label className="form-label">Password *</label>
                  <div className="relative">
                    <input data-testid="password-input" type={showPassword ? 'text' : 'password'} name="password" value={formData.password} onChange={handleChange} className={`form-input pr-10 ${errors.password ? 'border-red-500' : ''}`} placeholder="Strong password" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600" data-testid="toggle-password">
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
                  <p className="text-xs text-slate-500 mt-1">Min 8 chars, uppercase, lowercase, number & special char</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2"><Briefcase size={20} className="text-sky-600" />Business Info <span className="text-sm font-normal text-slate-500">(Optional)</span></h3>
              <div className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Business Name</label>
                    <input data-testid="business-name-input" type="text" name="business_name" value={formData.business_name} onChange={handleChange} className="form-input" placeholder="Your Company Ltd." />
                  </div>
                  <div>
                    <label className="form-label">Business Type</label>
                    <select data-testid="business-type-select" name="business_type" value={formData.business_type} onChange={handleChange} className="form-input">
                      <option value="">Select type</option>
                      <option value="publisher">Publisher</option>
                      <option value="agency">SEO Agency</option>
                      <option value="marketing">Content Marketing</option>
                      <option value="media">Digital Media</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="form-label">GST/Tax ID</label>
                  <input data-testid="gst-input" type="text" name="gst_tax_id" value={formData.gst_tax_id} onChange={handleChange} className="form-input" placeholder="GST123456789" />
                </div>
                <div>
                  <label className="form-label">Notes</label>
                  <textarea data-testid="notes-input" name="notes" value={formData.notes} onChange={handleChange} className="form-input" rows="3" placeholder="Any additional information..." />
                </div>
              </div>
            </div>

            <button data-testid="register-button" type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600">Already have an account? <button onClick={() => navigate('/auth/login')} className="text-sky-600 font-semibold hover:text-sky-700" data-testid="go-to-login">Login here</button></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;