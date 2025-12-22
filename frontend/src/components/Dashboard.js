import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { toast } from 'sonner';
import { 
  Target, 
  TrendingUp, 
  Award,
  BarChart3,
  LogOut,
  Menu,
  X,
  Zap
} from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetchUserData();
    fetchStats();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await axios.get('/user/me');
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      if (error.response?.status === 401) {
        navigate('/auth/login');
      }
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/prompts/stats');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    toast.success('Logged out successfully');
    navigate('/auth/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className=\"min-h-screen bg-slate-50\">
      {/* Top Navigation */}
      <nav className=\"bg-white border-b border-slate-200 sticky top-0 z-50\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
          <div className=\"flex justify-between items-center h-16\">
            <div className=\"flex items-center gap-3\">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className=\"lg:hidden p-2 rounded-lg hover:bg-slate-100\"
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              <h1 className=\"text-2xl font-bold text-blue-600\">CiteSight</h1>
            </div>

            <div className=\"flex items-center gap-4\">
              <div className=\"text-right hidden sm:block\">
                <p className=\"text-sm font-medium text-slate-900\">{user?.first_name} {user?.last_name}</p>
                <p className=\"text-xs text-slate-500\">{user?.company_name}</p>
              </div>
              <button
                onClick={handleLogout}
                className=\"flex items-center gap-2 px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg transition-colors\"
              >
                <LogOut size={18} />
                <span className=\"hidden sm:inline\">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className=\"fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden\"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className=\"flex\">
        {/* Sidebar */}
        <aside className={`
          fixed lg:sticky top-16 h-[calc(100vh-4rem)] w-64 bg-white border-r border-slate-200 z-40
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}>
          <nav className=\"p-4 space-y-2\">
            <button
              onClick={() => navigate('/dashboard')}
              className=\"w-full flex items-center gap-3 px-4 py-3 text-blue-600 bg-blue-50 rounded-lg font-medium\"
            >
              <BarChart3 size={20} />
              Dashboard
            </button>
            
            <button
              onClick={() => navigate('/prompts')}
              className=\"w-full flex items-center gap-3 px-4 py-3 text-slate-700 hover:bg-slate-100 rounded-lg font-medium transition-colors\"
            >
              <Target size={20} />
              Prompt Monitoring
            </button>

            <div className=\"pt-4 mt-4 border-t border-slate-200\">
              <p className=\"px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider\">
                Coming Soon
              </p>
              <button
                disabled
                className=\"w-full flex items-center gap-3 px-4 py-3 text-slate-400 rounded-lg font-medium cursor-not-allowed\"
              >
                <TrendingUp size={20} />
                Competitor Analysis
              </button>
              <button
                disabled
                className=\"w-full flex items-center gap-3 px-4 py-3 text-slate-400 rounded-lg font-medium cursor-not-allowed\"
              >
                <Zap size={20} />
                AI Simulator
              </button>
            </div>
          </nav>
        </aside>

        {/* Main Content */}
        <main className=\"flex-1 p-6 lg:p-8 max-w-7xl\">
          {/* Welcome Section */}
          <div className=\"mb-8\">
            <h2 className=\"text-3xl font-bold text-slate-900 mb-2\">
              Welcome back, {user?.first_name}! 👋
            </h2>
            <p className=\"text-slate-600\">
              Here's your AI visibility overview for {user?.company_name}
            </p>
          </div>

          {/* Stats Grid */}
          <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8\">
            <div className=\"bg-white rounded-xl p-6 border border-slate-200 hover:border-blue-300 transition-colors\">
              <div className=\"flex items-center justify-between mb-4\">
                <div className=\"p-3 bg-blue-100 rounded-lg\">
                  <Target className=\"text-blue-600\" size={24} />
                </div>
                <span className=\"text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded-full\">
                  WEEKLY
                </span>
              </div>
              <p className=\"text-3xl font-bold text-slate-900 mb-1\">{stats?.total_prompts || 0}</p>
              <p className=\"text-sm text-slate-600\">Total Prompts</p>
            </div>

            <div className=\"bg-white rounded-xl p-6 border border-slate-200 hover:border-green-300 transition-colors\">
              <div className=\"flex items-center justify-between mb-4\">
                <div className=\"p-3 bg-green-100 rounded-lg\">
                  <Award className=\"text-green-600\" size={24} />
                </div>
                <span className=\"text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full\">
                  AVG
                </span>
              </div>
              <p className=\"text-3xl font-bold text-slate-900 mb-1\">{stats?.avg_business_value || 0}</p>
              <p className=\"text-sm text-slate-600\">Business Value</p>
            </div>

            <div className=\"bg-white rounded-xl p-6 border border-slate-200 hover:border-purple-300 transition-colors\">
              <div className=\"flex items-center justify-between mb-4\">
                <div className=\"p-3 bg-purple-100 rounded-lg\">
                  <TrendingUp className=\"text-purple-600\" size={24} />
                </div>
                <span className=\"text-xs font-semibold text-purple-600 bg-purple-50 px-2 py-1 rounded-full\">
                  AVG
                </span>
              </div>
              <p className=\"text-3xl font-bold text-slate-900 mb-1\">{stats?.avg_feasibility || 0}</p>
              <p className=\"text-sm text-slate-600\">Feasibility Score</p>
            </div>

            <div className=\"bg-white rounded-xl p-6 border border-slate-200 hover:border-orange-300 transition-colors\">
              <div className=\"flex items-center justify-between mb-4\">
                <div className=\"p-3 bg-orange-100 rounded-lg\">
                  <BarChart3 className=\"text-orange-600\" size={24} />
                </div>
                <span className=\"text-xs font-semibold text-orange-600 bg-orange-50 px-2 py-1 rounded-full\">
                  AVG
                </span>
              </div>
              <p className=\"text-3xl font-bold text-slate-900 mb-1\">{stats?.avg_citation_potential || 0}</p>
              <p className=\"text-sm text-slate-600\">Citation Potential</p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className=\"bg-white rounded-xl p-6 border border-slate-200 mb-8\">
            <h3 className=\"text-xl font-bold text-slate-900 mb-4\">Quick Actions</h3>
            <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
              <button
                onClick={() => navigate('/prompts')}
                className=\"flex items-center gap-4 p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg hover:from-blue-100 hover:to-blue-200 transition-colors group\"
              >
                <Target className=\"text-blue-600 group-hover:scale-110 transition-transform\" size={32} />
                <div className=\"text-left\">
                  <p className=\"font-semibold text-slate-900\">View All Prompts</p>
                  <p className=\"text-sm text-slate-600\">Browse and filter your 25 prompts</p>
                </div>
              </button>

              <div className=\"flex items-center gap-4 p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg opacity-60\">
                <TrendingUp className=\"text-slate-400\" size={32} />
                <div className=\"text-left\">
                  <p className=\"font-semibold text-slate-700\">Competitor Analysis</p>
                  <p className=\"text-sm text-slate-500\">Coming soon</p>
                </div>
              </div>
            </div>
          </div>

          {/* Source Breakdown */}
          {stats?.source_breakdown && Object.keys(stats.source_breakdown).length > 0 && (
            <div className=\"bg-white rounded-xl p-6 border border-slate-200\">
              <h3 className=\"text-xl font-bold text-slate-900 mb-4\">Prompt Sources</h3>
              <div className=\"grid grid-cols-2 md:grid-cols-5 gap-4\">
                {Object.entries(stats.source_breakdown).map(([source, count]) => (
                  <div key={source} className=\"text-center p-4 bg-slate-50 rounded-lg\">
                    <p className=\"text-2xl font-bold text-slate-900\">{count}</p>
                    <p className=\"text-xs text-slate-600 mt-1 capitalize\">
                      {source.replace('_', ' ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Info Banner */}
          <div className=\"mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6\">
            <div className=\"flex items-start gap-4\">
              <div className=\"p-2 bg-blue-100 rounded-lg\">
                <Zap className=\"text-blue-600\" size={24} />
              </div>
              <div>
                <h4 className=\"font-semibold text-slate-900 mb-1\">Prompts Updated Weekly</h4>
                <p className=\"text-sm text-slate-600\">
                  Your prompts are automatically refreshed every Monday at 9 AM. We analyze your website, 
                  mine Reddit discussions, study competitors, and generate 25 fresh AI-optimized prompts.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
