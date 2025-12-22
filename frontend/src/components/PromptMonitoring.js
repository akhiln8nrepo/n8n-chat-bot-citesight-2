import { useState, useEffect } from 'react';
import axios from '@/utils/axios';
import { toast } from 'sonner';
import { 
  Loader2, 
  Filter, 
  TrendingUp, 
  Target, 
  Award,
  BarChart3,
  CheckCircle2,
  Search,
  RefreshCw
} from 'lucide-react';

const PromptMonitoring = () => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [filters, setFilters] = useState({
    source: 'all',
    intent: 'all',
    minBusinessValue: 0
  });

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  useEffect(() => {
    if (onboardingComplete) {
      fetchPrompts();
    }
  }, [onboardingComplete]);

  const checkOnboardingStatus = async () => {
    try {
      const response = await axios.get('/onboarding/status');
      setOnboardingComplete(response.data.completed);
      
      if (!response.data.completed) {
        // Poll every 5 seconds until complete
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

  const getFilteredPrompts = () => {
    return prompts.filter(p => {
      if (filters.source !== 'all' && p.source !== filters.source) return false;
      if (filters.intent !== 'all' && p.intent !== filters.intent) return false;
      if (p.business_value < filters.minBusinessValue) return false;
      return true;
    });
  };

  const getSourceLabel = (source) => {
    const labels = {
      'ai_testing': 'AI Testing',
      'reddit_mining': 'Reddit Mining',
      'customer_surveys': 'Customer Surveys',
      'keyword_conversion': 'Keyword Conversion',
      'competitor_analysis': 'Competitor Analysis'
    };
    return labels[source] || source;
  };

  const getIntentLabel = (intent) => {
    const labels = {
      'information_seeking': 'Information Seeking',
      'recommendation_seeking': 'Recommendation',
      'instructions': 'Instructions',
      'problem_solving': 'Problem Solving',
      'creative': 'Creative',
      'research': 'Research'
    };
    return labels[intent] || intent;
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-600 bg-green-50';
    if (score >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getSourceColor = (source) => {
    const colors = {
      'ai_testing': 'bg-blue-100 text-blue-700',
      'reddit_mining': 'bg-orange-100 text-orange-700',
      'customer_surveys': 'bg-purple-100 text-purple-700',
      'keyword_conversion': 'bg-green-100 text-green-700',
      'competitor_analysis': 'bg-red-100 text-red-700'
    };
    return colors[source] || 'bg-gray-100 text-gray-700';
  };

  // Loading/Onboarding State
  if (!onboardingComplete) {
    return (
      <div className=\"min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4\">
        <div className=\"bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center\">
          <div className=\"flex justify-center mb-6\">
            <div className=\"relative\">
              <Loader2 className=\"animate-spin text-blue-600\" size={64} />
              <div className=\"absolute inset-0 flex items-center justify-center\">
                <Search className=\"text-blue-600\" size={28} />
              </div>
            </div>
          </div>
          
          <h2 className=\"text-2xl font-bold text-slate-900 mb-3\">Analyzing Your Website</h2>
          <p className=\"text-slate-600 mb-6\">
            We're crawling your website and generating 25 optimized prompts from 5 different sources...
          </p>
          
          <div className=\"space-y-3 text-left\">
            <div className=\"flex items-center gap-3 p-3 bg-blue-50 rounded-lg\">
              <CheckCircle2 className=\"text-blue-600 flex-shrink-0\" size={20} />
              <span className=\"text-sm text-slate-700\">Crawling website content</span>
            </div>
            <div className=\"flex items-center gap-3 p-3 bg-blue-50 rounded-lg\">
              <CheckCircle2 className=\"text-blue-600 flex-shrink-0\" size={20} />
              <span className=\"text-sm text-slate-700\">Mining Reddit discussions</span>
            </div>
            <div className=\"flex items-center gap-3 p-3 bg-blue-50 rounded-lg\">
              <CheckCircle2 className=\"text-blue-600 flex-shrink-0\" size={20} />
              <span className=\"text-sm text-slate-700\">Analyzing competitors</span>
            </div>
            <div className=\"flex items-center gap-3 p-3 bg-blue-50 rounded-lg\">
              <Loader2 className=\"animate-spin text-blue-600 flex-shrink-0\" size={20} />
              <span className=\"text-sm text-slate-700\">Generating AI prompts...</span>
            </div>
          </div>
          
          <p className=\"text-xs text-slate-500 mt-6\">This usually takes 30-60 seconds</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className=\"flex items-center justify-center h-96\">
        <Loader2 className=\"animate-spin text-blue-600\" size={48} />
      </div>
    );
  }

  const filteredPrompts = getFilteredPrompts();

  return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Prompt Monitoring</h1>
            <p className="text-slate-600 mt-1">25 AI-optimized prompts updated weekly</p>
          </div>
          <button
            onClick={fetchPrompts}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw size={18} />
            Refresh
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <Target className="text-blue-600" size={24} />
              <span className="text-sm text-slate-600">Total Prompts</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">{prompts.length}</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <Award className="text-green-600" size={24} />
              <span className="text-sm text-slate-600">Avg Business Value</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {prompts.length > 0 ? Math.round(prompts.reduce((sum, p) => sum + p.business_value, 0) / prompts.length) : 0}
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="text-purple-600" size={24} />
              <span className="text-sm text-slate-600">Avg Feasibility</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {prompts.length > 0 ? Math.round(prompts.reduce((sum, p) => sum + p.feasibility, 0) / prompts.length) : 0}
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="text-orange-600" size={24} />
              <span className="text-sm text-slate-600">Citation Potential</span>
            </div>
            <p className="text-3xl font-bold text-slate-900">
              {prompts.length > 0 ? Math.round(prompts.reduce((sum, p) => sum + p.citation_potential, 0) / prompts.length) : 0}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <Filter size={20} className="text-slate-600" />
            <h3 className="text-lg font-semibold text-slate-900">Filters</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({...filters, source: e.target.value})}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
              <label className="block text-sm font-medium text-slate-700 mb-2">Intent</label>
              <select
                value={filters.intent}
                onChange={(e) => setFilters({...filters, intent: e.target.value})}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Intents</option>
                <option value="information_seeking">Information Seeking</option>
                <option value="recommendation_seeking">Recommendation</option>
                <option value="instructions">Instructions</option>
                <option value="problem_solving">Problem Solving</option>
                <option value="creative">Creative</option>
                <option value="research">Research</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Min Business Value: {filters.minBusinessValue}
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.minBusinessValue}
                onChange={(e) => setFilters({...filters, minBusinessValue: parseInt(e.target.value)})}
                className="w-full"
              />
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-slate-600">
              Showing {filteredPrompts.length} of {prompts.length} prompts
            </p>
            {(filters.source !== 'all' || filters.intent !== 'all' || filters.minBusinessValue > 0) && (
              <button
                onClick={() => setFilters({ source: 'all', intent: 'all', minBusinessValue: 0 })}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Prompts List */}
        <div className="space-y-4">
          {filteredPrompts.map((prompt, index) => (
            <div key={prompt.id || index} className="bg-white rounded-xl p-6 border border-slate-200 hover:border-blue-300 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg text-blue-700 font-bold">
                    #{prompt.rank}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{prompt.prompt}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(prompt.source)}`}>
                        {getSourceLabel(prompt.source)}
                      </span>
                      <span className="px-2 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium">
                        {getIntentLabel(prompt.intent)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className={`px-3 py-1 rounded-lg font-bold ${getScoreColor(prompt.overall_score)}`}>
                  {Math.round(prompt.overall_score)}
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mt-4 pt-4 border-t border-slate-100">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Business Value</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{width: `${prompt.business_value}%`}}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{prompt.business_value}</span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-slate-500 mb-1">Volume</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{width: `${prompt.volume}%`}}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{prompt.volume}</span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-slate-500 mb-1">Competition</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-red-600 h-2 rounded-full" 
                        style={{width: `${prompt.competition}%`}}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{prompt.competition}</span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-slate-500 mb-1">Feasibility</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full" 
                        style={{width: `${prompt.feasibility}%`}}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{prompt.feasibility}</span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-slate-500 mb-1">Citation</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-orange-600 h-2 rounded-full" 
                        style={{width: `${prompt.citation_potential}%`}}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{prompt.citation_potential}</span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-slate-500 mb-1">Relevance</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full" 
                        style={{width: `${prompt.brand_relevance}%`}}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-900">{prompt.brand_relevance}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredPrompts.length === 0 && (
          <div className="bg-white rounded-xl p-12 border border-slate-200 text-center">
            <Filter className="mx-auto text-slate-400 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">No prompts match your filters</h3>
            <p className="text-slate-600">Try adjusting your filter criteria</p>
          </div>
        )}
      </div>
  );
};

export default PromptMonitoring;
