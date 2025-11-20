import { useNavigate } from 'react-router-dom';
import { TrendingUp, Menu, X, User, LogOut } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

const MarketingNav = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const navItems = [
    { label: 'Home', path: '/home' },
    { label: 'Features', path: '/features' },
    { label: 'Pricing', path: '/pricing' },
    { label: 'About', path: '/about' },
    { label: 'Contact', path: '/contact' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out successfully');
    navigate('/home');
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/home')}>
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg">
              <TrendingUp size={24} className="text-white" />
            </div>
            <span className="text-2xl font-bold text-slate-900">CiteSight</span>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className="text-slate-700 hover:text-blue-600 font-medium transition-colors"
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Desktop CTAs */}
          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="flex items-center gap-2 text-slate-700 hover:text-blue-600 font-semibold transition-colors"
                >
                  <User size={18} />
                  {user.first_name}
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 text-slate-700 hover:text-red-600 font-semibold transition-colors"
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => navigate('/auth/login')}
                  className="text-slate-700 hover:text-blue-600 font-semibold transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={() => navigate('/auth/register')}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2.5 rounded-lg font-semibold hover:shadow-lg transition-all"
                >
                  Get Started
                </button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-slate-700"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 space-y-3">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => { navigate(item.path); setMobileMenuOpen(false); }}
                className="block w-full text-left text-slate-700 hover:text-blue-600 font-medium py-2"
              >
                {item.label}
              </button>
            ))}
            <button
              onClick={() => { navigate('/auth/login'); setMobileMenuOpen(false); }}
              className="block w-full text-left text-slate-700 font-semibold py-2"
            >
              Sign In
            </button>
            <button
              onClick={() => { navigate('/auth/register'); setMobileMenuOpen(false); }}
              className="block w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2.5 rounded-lg font-semibold text-center"
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default MarketingNav;