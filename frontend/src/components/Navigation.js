import { useNavigate, useLocation } from 'react-router-dom';
import { TrendingUp, LayoutDashboard, FileText, Target, Lightbulb, Users } from 'lucide-react';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
    { path: '/content', label: 'Content', icon: <FileText size={18} /> },
    { path: '/keywords', label: 'Keywords', icon: <Target size={18} /> },
    { path: '/recommendations', label: 'Recommendations', icon: <Lightbulb size={18} /> },
    { path: '/competitors', label: 'Competitors', icon: <Users size={18} /> },
  ];

  return (
    <nav className="dashboard-nav" data-testid="main-navigation">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <TrendingUp size={24} className="text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">CiteSight</span>
          </div>

          <div className="flex gap-2">
            {navItems.map((item) => (
              <button
                key={item.path}
                data-testid={`nav-${item.label.toLowerCase()}`}
                onClick={() => navigate(item.path)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  location.pathname === item.path
                    ? 'bg-sky-500 text-white shadow-lg'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {item.icon}
                <span className="hidden sm:inline">{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;