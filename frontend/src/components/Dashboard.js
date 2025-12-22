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
  Zap,
  Eye,
  Bell,
  ChevronRight,
  Activity,
  PieChart
} from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetchUserData();
    fetchStats();
    fetchPrompts();
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
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchPrompts = async () => {
    try {
      const response = await axios.get('/prompts');
      setPrompts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching prompts:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    toast.success('Logged out successfully');
    navigate('/auth/login');
  };

  const getCategoryLabel = (intent) => {
    const labels = {
      'information_seeking': 'INFO',
      'recommendation_seeking': 'REC',
      'instructions': 'INS',
      'problem_solving': 'SOLVE',
      'creative': 'CREATE',
      'research': 'RES'
    };
    return labels[intent] || intent;
  };

  const getCategoryColor = (intent) => {
    const colors = {
      'informational': 'bg-blue-100 text-blue-700',
      'navigational': 'bg-gray-100 text-gray-700',
      'commercial_investigation': 'bg-green-100 text-green-700',
      'transactional': 'bg-purple-100 text-purple-700',
      'local': 'bg-yellow-100 text-yellow-700',
      'support': 'bg-orange-100 text-orange-700',
      // Legacy
      'information_seeking': 'bg-blue-100 text-blue-700',
      'recommendation_seeking': 'bg-green-100 text-green-700',
      'instructions': 'bg-yellow-100 text-yellow-700',
      'problem_solving': 'bg-red-100 text-red-700',
      'creative': 'bg-purple-100 text-purple-700',
      'research': 'bg-indigo-100 text-indigo-700'
    };
    return colors[intent] || 'bg-gray-100 text-gray-700';
  };

  const getSourceColor = (source) => {
    const colors = {
      'category_search': '#3B82F6',
      'product_discovery': '#8B5CF6',
      'competitor_comparison': '#EF4444',
      'use_case': '#10B981',
      'persona_based': '#6366F1',
      'problem_solution': '#F59E0B',
      'feature_discovery': '#14B8A6',
      'reddit_mining': '#F97316',
      // Legacy
      'ai_testing': '#3B82F6',
      'customer_surveys': '#8B5CF6',
      'keyword_conversion': '#10B981',
      'competitor_analysis': '#EF4444'
    };
    return colors[source] || '#6B7280';
  };

  // Calculate monitored prompts (simulated for now)
  const monitoredCount = Math.floor((stats?.total_prompts || 0) * 0.48);
  const brandMentionRate = stats?.total_prompts > 0 ? 58.5 : 0;
  const avgScore = stats?.avg_overall_score || ((stats?.avg_business_value || 0) * 0.25 + (stats?.avg_feasibility || 0) * 0.15).toFixed(1);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-slate-100"
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              <div className="flex items-center gap-2">
                <Target className="text-blue-600" size={28} />
                <h1 className="text-xl font-bold text-slate-900">GEO Monitor</h1>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <button onClick={() => navigate('/dashboard')} className="text-blue-600 font-medium">Dashboard</button>
              <button onClick={() => navigate('/prompts')} className="text-slate-600 hover:text-slate-900">Prompts</button>
              <button className="text-slate-400 cursor-not-allowed">Monitoring</button>
              <button className="text-slate-400 cursor-not-allowed">Analytics</button>
            </div>

            <div className="flex items-center gap-4">
              <button className="p-2 rounded-lg hover:bg-slate-100 relative">
                <Bell size={20} className="text-slate-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </div>
                <button
                  onClick={handleLogout}
                  className="text-slate-600 hover:text-slate-900"
                >
                  <LogOut size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-500">Total Prompts</span>
              <Target className="text-blue-500" size={20} />
            </div>
            <p className="text-3xl font-bold text-slate-900">{stats?.total_prompts || 0}</p>
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <TrendingUp size={14} />
              <span>+5 new</span>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-500">Monitored Prompts</span>
              <Eye className="text-green-500" size={20} />
            </div>
            <p className="text-3xl font-bold text-slate-900">{monitoredCount}</p>
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <Activity size={14} />
              <span>+3 active</span>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-500">Brand Mentions</span>
              <Award className="text-purple-500" size={20} />
            </div>
            <p className="text-3xl font-bold text-slate-900">{brandMentionRate}%</p>
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <TrendingUp size={14} />
              <span>↑ 5.2%</span>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-500">Avg Score</span>
              <BarChart3 className="text-orange-500" size={20} />
            </div>
            <p className="text-3xl font-bold text-slate-900">{avgScore}</p>
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <TrendingUp size={14} />
              <span>↑ 0.3</span>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Prompts by Category */}
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <PieChart size={20} className="text-blue-600" />
              PROMPTS BY CATEGORY
            </h3>
            {stats?.intent_breakdown && Object.keys(stats.intent_breakdown).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.intent_breakdown).map(([intent, count]) => (
                  <div key={intent} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${getCategoryColor(intent).split(' ')[0]}`}></div>
                      <span className="text-sm text-slate-600 capitalize">{intent.replace('_', ' ')}</span>
                    </div>
                    <span className="text-sm font-medium text-slate-900">({count})</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">No category data available</div>
            )}
          </div>

          {/* Prompts by Source */}
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BarChart3 size={20} className="text-green-600" />
              PROMPTS BY SOURCE
            </h3>
            {stats?.source_breakdown && Object.keys(stats.source_breakdown).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.source_breakdown).map(([source, count]) => (
                  <div key={source} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-600 capitalize">{source.replace('_', ' ')}</span>
                      <span className="font-medium text-slate-900">{count}</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full" 
                        style={{ 
                          width: `${(count / (stats?.total_prompts || 1)) * 100}%`,
                          backgroundColor: getSourceColor(source)
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">No source data available</div>
            )}
          </div>
        </div>

        {/* Top Ranked Prompts */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm mb-8">
          <div className="p-6 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">TOP RANKED PROMPTS</h3>
            <button 
              onClick={() => navigate('/prompts')}
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              View All <ChevronRight size={16} />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">#</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Prompt</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {prompts.slice(0, 5).map((prompt, index) => (
                  <tr key={prompt.id || index} className="hover:bg-slate-50">
                    <td className="px-6 py-4 text-sm font-medium text-slate-900">{index + 1}</td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-slate-900 line-clamp-2 max-w-md">{prompt.prompt}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(prompt.intent)}`}>
                        {getCategoryLabel(prompt.intent)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-semibold text-slate-900">{Math.round(prompt.overall_score)}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => navigate('/prompts')}
                          className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Eye size={16} />
                        </button>
                        <button className="p-1.5 text-slate-400 hover:text-green-600 hover:bg-green-50 rounded">
                          <BarChart3 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="p-6 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">RECENT ALERTS</h3>
            <button className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
              View All <ChevronRight size={16} />
            </button>
          </div>
          <div className="divide-y divide-slate-100">
            <div className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-slate-700">Brand mentioned in ChatGPT for "best PM tool"</span>
              </div>
              <span className="text-xs text-slate-500">2 hours ago</span>
            </div>
            <div className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm text-slate-700">Competitor gained mention for "PM comparison"</span>
              </div>
              <span className="text-xs text-slate-500">5 hours ago</span>
            </div>
            <div className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-slate-700">Position improved: "project management tips"</span>
              </div>
              <span className="text-xs text-slate-500">1 day ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
