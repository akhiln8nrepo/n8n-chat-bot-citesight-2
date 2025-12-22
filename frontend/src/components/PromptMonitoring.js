import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { toast } from 'sonner';
import { 
  Loader2, 
  Filter, 
  TrendingUp, 
  Target, 
  Award,
  BarChart3,
  Search,
  RefreshCw,
  Eye,
  Trash2,
  Edit3,
  ChevronLeft,
  ChevronRight,
  X,
  Bell,
  LogOut,
  Menu,
  Activity,
  ShoppingCart,
  FileText,
  Lightbulb,
  HelpCircle,
  Microscope,
  CheckCircle2
} from 'lucide-react';

const PromptMonitoring = () => {
  const navigate = useNavigate();
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [user, setUser] = useState(null);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [monitoredPrompts, setMonitoredPrompts] = useState(new Set());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const [filters, setFilters] = useState({
    category: 'all',
    source: 'all',
    sortBy: 'overall_score',
    order: 'desc',
    showMonitoredOnly: false
  });

  useEffect(() => {
    fetchUserData();
    checkOnboardingStatus();
  }, []);

  useEffect(() => {
    if (onboardingComplete) {
      fetchPrompts();
    }
  }, [onboardingComplete]);

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

  const checkOnboardingStatus = async () => {
    try {
      const response = await axios.get('/onboarding/status');
      setOnboardingComplete(response.data.completed);
      
      if (!response.data.completed) {
        setTimeout(checkOnboardingStatus, 5000);
      }
    } catch (error) {
      console.error('Error checking onboarding:', error);
    }
  };

  const fetchPrompts = async () => {
    try {
      const response = await axios.get('/prompts');
      setPrompts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching prompts:', error);
      toast.error('Failed to load prompts');
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    toast.success('Logged out successfully');
    navigate('/auth/login');
  };

  const toggleMonitor = (promptId) => {
    setMonitoredPrompts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(promptId)) {
        newSet.delete(promptId);
        toast.success('Prompt removed from monitoring');
      } else {
        newSet.add(promptId);
        toast.success('Prompt added to monitoring');
      }
      return newSet;
    });
  };

  const getFilteredPrompts = () => {
    let filtered = [...prompts];
    
    if (filters.category !== 'all') {
      filtered = filtered.filter(p => p.intent === filters.category);
    }
    if (filters.source !== 'all') {
      filtered = filtered.filter(p => p.source === filters.source);
    }
    if (filters.showMonitoredOnly) {
      filtered = filtered.filter(p => monitoredPrompts.has(p.id));
    }
    
    // Sort
    filtered.sort((a, b) => {
      const aVal = a[filters.sortBy] || 0;
      const bVal = b[filters.sortBy] || 0;
      return filters.order === 'desc' ? bVal - aVal : aVal - bVal;
    });
    
    return filtered;
  };

  const getCategoryIcon = (intent) => {
    const icons = {
      'information_seeking': <HelpCircle size={14} />,
      'recommendation_seeking': <Target size={14} />,
      'instructions': <FileText size={14} />,
      'problem_solving': <Lightbulb size={14} />,
      'creative': <Lightbulb size={14} />,
      'research': <Microscope size={14} />
    };
    return icons[intent] || <HelpCircle size={14} />;
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
    return labels[intent] || intent?.toUpperCase()?.slice(0, 4);
  };

  const getCategoryColor = (intent) => {
    const colors = {
      'information_seeking': 'bg-blue-100 text-blue-700',
      'recommendation_seeking': 'bg-green-100 text-green-700',
      'instructions': 'bg-yellow-100 text-yellow-700',
      'problem_solving': 'bg-red-100 text-red-700',
      'creative': 'bg-purple-100 text-purple-700',
      'research': 'bg-indigo-100 text-indigo-700'
    };
    return colors[intent] || 'bg-gray-100 text-gray-700';
  };

  const getSourceLabel = (source) => {
    const labels = {
      'ai_testing': 'AI TEST',
      'reddit_mining': 'REDDIT',
      'customer_surveys': 'SURVEY',
      'keyword_conversion': 'KEYWORD',
      'competitor_analysis': 'COMPET'
    };
    return labels[source] || source?.toUpperCase()?.slice(0, 6);
  };

  const getSourceColor = (source) => {
    const colors = {
      'ai_testing': 'bg-blue-50 text-blue-600',
      'reddit_mining': 'bg-orange-50 text-orange-600',
      'customer_surveys': 'bg-purple-50 text-purple-600',
      'keyword_conversion': 'bg-green-50 text-green-600',
      'competitor_analysis': 'bg-red-50 text-red-600'
    };
    return colors[source] || 'bg-gray-50 text-gray-600';
  };

  const getJourneyStage = (intent) => {
    const stages = {
      'recommendation_seeking': { label: 'Consideration', icon: <ShoppingCart size={14} /> },
      'problem_solving': { label: 'Awareness', icon: <Lightbulb size={14} /> },
      'instructions': { label: 'Decision', icon: <CheckCircle2 size={14} /> },
      'information_seeking': { label: 'Awareness', icon: <HelpCircle size={14} /> },
      'research': { label: 'Evaluation', icon: <Microscope size={14} /> },
      'creative': { label: 'Inspiration', icon: <Lightbulb size={14} /> }
    };
    return stages[intent] || { label: 'Unknown', icon: <HelpCircle size={14} /> };
  };

  // Loading/Onboarding State
  if (!onboardingComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <Loader2 className="animate-spin text-blue-600" size={64} />
              <div className="absolute inset-0 flex items-center justify-center">
                <Search className="text-blue-600" size={28} />
              </div>
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Analyzing Your Website</h2>
          <p className="text-slate-600 mb-6">
            We're crawling your website and generating 25 optimized prompts from 5 different sources...
          </p>
          
          <div className="space-y-3 text-left">
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <CheckCircle2 className="text-blue-600 flex-shrink-0" size={20} />
              <span className="text-sm text-slate-700">Crawling website content</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <CheckCircle2 className="text-blue-600 flex-shrink-0" size={20} />
              <span className="text-sm text-slate-700">Mining Reddit discussions</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <CheckCircle2 className="text-blue-600 flex-shrink-0" size={20} />
              <span className="text-sm text-slate-700">Analyzing competitors</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <Loader2 className="animate-spin text-blue-600 flex-shrink-0" size={20} />
              <span className="text-sm text-slate-700">Generating AI prompts...</span>
            </div>
          </div>
          
          <p className="text-xs text-slate-500 mt-6">This usually takes 30-60 seconds</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <Loader2 className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  const filteredPrompts = getFilteredPrompts();

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
              <button onClick={() => navigate('/dashboard')} className="text-slate-600 hover:text-slate-900">Dashboard</button>
              <button onClick={() => navigate('/prompts')} className="text-blue-600 font-medium">Prompts</button>
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900">PROMPTS</h2>
          <p className="text-slate-600">Manage and monitor your AI prompt opportunities</p>
        </div>

        {/* Filters Card */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm mb-6">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={fetchPrompts}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw size={18} />
              Regenerate Prompts
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1 uppercase">Category</label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({...filters, category: e.target.value})}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
              >
                <option value="all">All Categories</option>
                <option value="information_seeking">Information Seeking</option>
                <option value="recommendation_seeking">Recommendation</option>
                <option value="instructions">Instructions</option>
                <option value="problem_solving">Problem Solving</option>
                <option value="creative">Creative</option>
                <option value="research">Research</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1 uppercase">Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({...filters, source: e.target.value})}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
              >
                <option value="all">All Sources</option>
                <option value="ai_testing">AI Testing</option>
                <option value="reddit_mining">Reddit Mining</option>
                <option value="customer_surveys">Customer Surveys</option>
                <option value="keyword_conversion">Keyword Conversion</option>
                <option value="competitor_analysis">Competitor Analysis</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1 uppercase">Sort by</label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
              >
                <option value="overall_score">Composite Score</option>
                <option value="business_value">Business Value</option>
                <option value="volume">Volume</option>
                <option value="feasibility">Feasibility</option>
                <option value="intent_score">Intent Score</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1 uppercase">Order</label>
              <select
                value={filters.order}
                onChange={(e) => setFilters({...filters, order: e.target.value})}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.showMonitoredOnly}
              onChange={(e) => setFilters({...filters, showMonitoredOnly: e.target.checked})}
              className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            Show monitored only
          </label>
        </div>

        {/* Prompts Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="w-12 px-4 py-3 text-left">
                    <input type="checkbox" className="w-4 h-4 rounded border-slate-300" />
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Prompt</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Category</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Source</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Score</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredPrompts.map((prompt, index) => (
                  <tr key={prompt.id || index} className="hover:bg-slate-50 group">
                    <td className="px-4 py-4">
                      <input 
                        type="checkbox" 
                        checked={monitoredPrompts.has(prompt.id)}
                        onChange={() => toggleMonitor(prompt.id)}
                        className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" 
                      />
                    </td>
                    <td className="px-4 py-4">
                      <div className="max-w-md">
                        <p className="text-sm text-slate-900 mb-2 line-clamp-2">{prompt.prompt}</p>
                        {/* Mini Metrics */}
                        <div className="flex items-center gap-4 text-xs">
                          <div className="flex items-center gap-1">
                            <span className="text-slate-500">Business:</span>
                            <div className="w-16 bg-slate-100 rounded-full h-1.5">
                              <div className="bg-blue-500 h-1.5 rounded-full" style={{width: `${prompt.business_value}%`}} />
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-slate-500">Volume:</span>
                            <div className="w-16 bg-slate-100 rounded-full h-1.5">
                              <div className="bg-green-500 h-1.5 rounded-full" style={{width: `${prompt.volume}%`}} />
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="text-slate-500">Intent:</span>
                            <div className="w-16 bg-slate-100 rounded-full h-1.5">
                              <div className="bg-yellow-500 h-1.5 rounded-full" style={{width: `${prompt.intent_score || 50}%`}} />
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(prompt.intent)}`}>
                        {getCategoryIcon(prompt.intent)}
                        {getCategoryLabel(prompt.intent)}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getSourceColor(prompt.source)}`}>
                        {getSourceLabel(prompt.source)}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-lg font-bold text-slate-900">{Math.round(prompt.overall_score)}</span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-1">
                        <button 
                          onClick={() => setSelectedPrompt(prompt)}
                          className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                          title="View Details"
                        >
                          <Eye size={16} />
                        </button>
                        <button 
                          className="p-1.5 text-slate-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
                          title="View Analytics"
                        >
                          <BarChart3 size={16} />
                        </button>
                        <button 
                          className="p-1.5 text-slate-400 hover:text-yellow-600 hover:bg-yellow-50 rounded transition-colors"
                          title="Edit"
                        >
                          <Edit3 size={16} />
                        </button>
                        <button 
                          className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                        {monitoredPrompts.has(prompt.id) && (
                          <span className="ml-2 px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full font-medium">
                            ● MON
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between">
            <p className="text-sm text-slate-600">
              Showing 1-{filteredPrompts.length} of {filteredPrompts.length} prompts
            </p>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded flex items-center gap-1" disabled>
                <ChevronLeft size={16} /> Previous
              </button>
              <button className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded">1</button>
              <button className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded flex items-center gap-1" disabled>
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>

        {filteredPrompts.length === 0 && (
          <div className="bg-white rounded-xl p-12 border border-slate-200 text-center mt-6">
            <Filter className="mx-auto text-slate-400 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">No prompts match your filters</h3>
            <p className="text-slate-600">Try adjusting your filter criteria</p>
          </div>
        )}
      </div>

      {/* Prompt Detail Modal */}
      {selectedPrompt && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-white">
              <h3 className="text-lg font-semibold text-slate-900">PROMPT DETAILS</h3>
              <button 
                onClick={() => setSelectedPrompt(null)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <X size={20} className="text-slate-500" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {/* Prompt Text */}
              <p className="text-lg text-slate-900 mb-6 leading-relaxed">
                "{selectedPrompt.prompt}"
              </p>

              {/* Badges Row */}
              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-slate-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500 mb-1">Category</p>
                  <span className={`inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded-full ${getCategoryColor(selectedPrompt.intent)}`}>
                    {getCategoryIcon(selectedPrompt.intent)}
                    {selectedPrompt.intent?.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500 mb-1">Source</p>
                  <span className={`inline-flex items-center gap-1 px-3 py-1 text-sm font-medium rounded ${getSourceColor(selectedPrompt.source)}`}>
                    📱 {selectedPrompt.source?.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="bg-slate-50 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500 mb-1">Journey Stage</p>
                  <span className="inline-flex items-center gap-1 px-3 py-1 text-sm font-medium bg-indigo-100 text-indigo-700 rounded-full">
                    {getJourneyStage(selectedPrompt.intent).icon}
                    {getJourneyStage(selectedPrompt.intent).label}
                  </span>
                </div>
              </div>

              {/* Rankings Section */}
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-sm font-semibold text-slate-900 uppercase">Rankings</h4>
                  <div className="text-right">
                    <span className="text-xs text-slate-500">COMPOSITE:</span>
                    <span className="ml-2 text-2xl font-bold text-blue-600">{Math.round(selectedPrompt.overall_score)}</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  {/* Business Value */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Business Value</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.business_value}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{width: `${selectedPrompt.business_value}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">High conversion potential</span>
                    </div>
                  </div>

                  {/* Volume */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Volume</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.volume}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{width: `${selectedPrompt.volume}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">~{Math.round(selectedPrompt.volume * 52)} monthly</span>
                    </div>
                  </div>

                  {/* Competition */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Competition</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.competition}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-red-500 h-2 rounded-full" style={{width: `${selectedPrompt.competition}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">{selectedPrompt.competition > 60 ? 'High' : selectedPrompt.competition > 40 ? 'Moderate' : 'Low'} competition</span>
                    </div>
                  </div>

                  {/* Feasibility */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Feasibility</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.feasibility}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{width: `${selectedPrompt.feasibility}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">Good fit for brand</span>
                    </div>
                  </div>

                  {/* Intent */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Intent</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.intent_score || 50}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{width: `${selectedPrompt.intent_score || 50}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">{(selectedPrompt.intent_score || 50) > 70 ? 'Strong' : 'Moderate'} purchase intent</span>
                    </div>
                  </div>

                  {/* Citation Potential */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Citation Potential</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.citation_potential}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-orange-500 h-2 rounded-full" style={{width: `${selectedPrompt.citation_potential}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">Authority match</span>
                    </div>
                  </div>

                  {/* Brand Relevance */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-600">Brand Relevance</span>
                      <span className="text-sm font-medium text-slate-900">{selectedPrompt.brand_relevance}/100</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div className="bg-indigo-500 h-2 rounded-full" style={{width: `${selectedPrompt.brand_relevance}%`}} />
                      </div>
                      <span className="text-xs text-slate-500 w-32">Core product alignment</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Metadata Section */}
              <div className="mb-8 bg-slate-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-slate-900 uppercase mb-3">Metadata</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-500">Estimated Monthly Volume:</span>
                    <span className="ml-2 text-slate-900 font-medium">{Math.round(selectedPrompt.volume * 52)}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Difficulty Level:</span>
                    <span className="ml-2 text-slate-900 font-medium">
                      {selectedPrompt.competition > 60 ? 'Hard' : selectedPrompt.competition > 40 ? 'Medium' : 'Easy'}
                    </span>
                  </div>
                </div>
                
                <div className="mt-4">
                  <p className="text-slate-500 text-sm mb-2">Suggested Actions:</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    <li>• Create comparison content with competitors</li>
                    <li>• Optimize landing page for this query</li>
                    <li>• Build FAQ section addressing this question</li>
                  </ul>
                </div>
              </div>

              {/* Monitoring Section */}
              <div className="bg-slate-50 rounded-lg p-4 mb-6">
                <h4 className="text-sm font-semibold text-slate-900 uppercase mb-3">Monitoring</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-500">Status:</span>
                    <span className={`ml-2 ${monitoredPrompts.has(selectedPrompt.id) ? 'text-green-600' : 'text-slate-500'}`}>
                      {monitoredPrompts.has(selectedPrompt.id) ? '● Active' : '○ Inactive'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500">Frequency:</span>
                    <span className="ml-2 text-slate-900">Daily</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Last Checked:</span>
                    <span className="ml-2 text-slate-900">2 hours ago</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Brand Mentioned:</span>
                    <span className="ml-2 text-green-600">Yes (Position #2)</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => toggleMonitor(selectedPrompt.id)}
                  className={`flex-1 py-2.5 px-4 rounded-lg font-medium transition-colors ${
                    monitoredPrompts.has(selectedPrompt.id) 
                      ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  {monitoredPrompts.has(selectedPrompt.id) ? 'Stop Monitoring' : 'Start Monitor'}
                </button>
                <button className="flex-1 py-2.5 px-4 bg-slate-100 text-slate-700 rounded-lg font-medium hover:bg-slate-200 transition-colors">
                  Edit Rankings
                </button>
                <button className="flex-1 py-2.5 px-4 bg-red-100 text-red-700 rounded-lg font-medium hover:bg-red-200 transition-colors">
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PromptMonitoring;
