import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import axios from '../utils/axios';
import {
  BarChart3, TrendingUp, TrendingDown, Eye, Target, Users, Award,
  Filter, Calendar, RefreshCw, ChevronRight, AlertTriangle, CheckCircle2,
  Zap, Globe, MessageSquare, ThumbsUp, ThumbsDown, Minus, ExternalLink,
  Layers, PieChart, Activity, ArrowUpRight, ArrowDownRight, Info, Search
} from 'lucide-react';

const Analytics = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [period, setPeriod] = useState('30d');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/auth/login');
      return;
    }
    fetchAnalytics();
  }, [period, platformFilter, categoryFilter]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ period });
      if (platformFilter !== 'all') params.append('platform', platformFilter);
      if (categoryFilter !== 'all') params.append('category', categoryFilter);
      
      const response = await axios.get(`/api/analytics/dashboard?${params}`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/auth/login');
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      'chatgpt': '🤖',
      'claude': '🧠',
      'gemini': '✨',
      'perplexity': '🔍'
    };
    return icons[platform] || '💬';
  };

  const getPlatformColor = (platform) => {
    const colors = {
      'chatgpt': 'bg-green-500',
      'claude': 'bg-orange-500',
      'gemini': 'bg-blue-500',
      'perplexity': 'bg-purple-500'
    };
    return colors[platform] || 'bg-gray-500';
  };

  const getSentimentIcon = (sentiment) => {
    if (sentiment > 0.2) return <ThumbsUp className="text-green-500" size={16} />;
    if (sentiment < -0.2) return <ThumbsDown className="text-red-500" size={16} />;
    return <Minus className="text-gray-400" size={16} />;
  };

  const formatSentiment = (score) => {
    if (score === null || score === undefined) return 'N/A';
    if (score > 0.2) return 'Positive';
    if (score < -0.2) return 'Negative';
    return 'Neutral';
  };

  const getVisibilityColor = (rate) => {
    if (rate >= 70) return 'text-green-600';
    if (rate >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPositionBadge = (position) => {
    if (!position) return <span className="text-gray-400">-</span>;
    if (position === 1) return <span className="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full text-xs font-medium">🥇 #1</span>;
    if (position === 2) return <span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded-full text-xs font-medium">🥈 #2</span>;
    if (position === 3) return <span className="bg-orange-100 text-orange-800 px-2 py-0.5 rounded-full text-xs font-medium">🥉 #3</span>;
    return <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-xs">#{position}</span>;
  };

  if (loading || !data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin text-blue-600 mx-auto mb-4" size={40} />
          <p className="text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <h1 className="text-xl font-bold text-slate-900">GEO Monitor</h1>
              <div className="hidden md:flex items-center gap-1">
                <button onClick={() => navigate('/dashboard')} className="px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg">
                  Dashboard
                </button>
                <button onClick={() => navigate('/prompts')} className="px-3 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg">
                  Prompts
                </button>
                <button className="px-3 py-2 text-sm text-blue-600 bg-blue-50 rounded-lg font-medium">
                  Analytics
                </button>
              </div>
            </div>
            <button onClick={handleLogout} className="text-sm text-slate-600 hover:text-slate-900">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header with Filters */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Analytics Dashboard</h2>
            <p className="text-slate-500 text-sm mt-1">AI Visibility Monitoring & Competitive Intelligence</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            {/* Period Filter */}
            <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-lg p-1">
              {['7d', '30d', '90d'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    period === p ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {p === '7d' ? '7 Days' : p === '30d' ? '30 Days' : '90 Days'}
                </button>
              ))}
            </div>

            {/* Platform Filter */}
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Platforms</option>
              <option value="chatgpt">🤖 ChatGPT</option>
              <option value="claude">🧠 Claude</option>
              <option value="gemini">✨ Gemini</option>
              <option value="perplexity">🔍 Perplexity</option>
            </select>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {data?.available_categories?.map(cat => (
                <option key={cat} value={cat}>{cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>
              ))}
            </select>

            <button
              onClick={fetchAnalytics}
              className="p-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white p-1 rounded-lg border border-slate-200 w-fit">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'platforms', label: 'AI Platforms', icon: Globe },
            { id: 'competitors', label: 'Competitors', icon: Users },
            { id: 'opportunities', label: 'Opportunities', icon: Target }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md transition-colors ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <Eye className="text-blue-500" size={24} />
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                (data?.kpis?.visibility_rate || 0) >= 50 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {data?.kpis?.visibility_rate >= 50 ? '↑ Good' : '↓ Needs Work'}
              </span>
            </div>
            <p className="text-sm text-slate-500 mb-1">AI Visibility Rate</p>
            <p className={`text-3xl font-bold ${getVisibilityColor(data?.kpis?.visibility_rate || 0)}`}>
              {data?.kpis?.visibility_rate || 0}%
            </p>
            <p className="text-xs text-slate-400 mt-2">{data?.kpis?.total_mentions || 0} mentions in {data?.kpis?.total_checks || 0} checks</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <Award className="text-yellow-500" size={24} />
              <span className="text-xs font-medium px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
                🥇 {data?.kpis?.first_position_count || 0}
              </span>
            </div>
            <p className="text-sm text-slate-500 mb-1">Average Position</p>
            <p className="text-3xl font-bold text-slate-900">
              {data?.kpis?.avg_position ? `#${data.kpis.avg_position}` : 'N/A'}
            </p>
            <p className="text-xs text-slate-400 mt-2">Top 3: {data?.kpis?.top_3_count || 0} times</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <PieChart className="text-purple-500" size={24} />
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                (data?.kpis?.share_of_voice || 0) >= 30 ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
              }`}>
                {(data?.kpis?.share_of_voice || 0) >= 30 ? 'Leading' : 'Growing'}
              </span>
            </div>
            <p className="text-sm text-slate-500 mb-1">Share of Voice</p>
            <p className="text-3xl font-bold text-slate-900">
              {data?.kpis?.share_of_voice || 0}%
            </p>
            <p className="text-xs text-slate-400 mt-2">vs {data?.competitors?.length || 0} competitors</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              {getSentimentIcon(data?.kpis?.avg_sentiment || 0)}
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                (data?.kpis?.avg_sentiment || 0) > 0.2 ? 'bg-green-100 text-green-700' : 
                (data?.kpis?.avg_sentiment || 0) < -0.2 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
              }`}>
                {formatSentiment(data?.kpis?.avg_sentiment)}
              </span>
            </div>
            <p className="text-sm text-slate-500 mb-1">Brand Sentiment</p>
            <p className="text-3xl font-bold text-slate-900">
              {data?.kpis?.avg_sentiment !== null ? (data.kpis.avg_sentiment >= 0 ? '+' : '') + data.kpis.avg_sentiment.toFixed(2) : 'N/A'}
            </p>
            <p className="text-xs text-slate-400 mt-2">
              👍 {data?.sentiment_breakdown?.positive || 0} | 
              👎 {data?.sentiment_breakdown?.negative || 0}
            </p>
          </div>
        </div>

        {/* Main Content Based on Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Platform Performance */}
            <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Globe size={18} />
                  AI Platform Performance
                </h3>
              </div>
              <div className="p-5">
                <div className="space-y-4">
                  {data?.platform_breakdown?.map((platform) => (
                    <div 
                      key={platform.platform} 
                      className={`p-4 rounded-lg border-2 transition-all ${
                        platformFilter === platform.platform ? 'border-blue-500 bg-blue-50' : 'border-slate-100 hover:border-slate-200'
                      }`}
                      onClick={() => setPlatformFilter(platformFilter === platform.platform ? 'all' : platform.platform)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{getPlatformIcon(platform.platform)}</span>
                          <div>
                            <p className="font-medium text-slate-900">{platform.display_name}</p>
                            <p className="text-xs text-slate-500">{platform.total_checks} checks performed</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`text-2xl font-bold ${getVisibilityColor(platform.mention_rate)}`}>
                            {platform.mention_rate}%
                          </p>
                          <p className="text-xs text-slate-500">visibility</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6 text-sm">
                        <div>
                          <span className="text-slate-500">Avg Position:</span>
                          <span className="ml-2 font-medium">{platform.avg_position ? `#${platform.avg_position}` : 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">🥇 First:</span>
                          <span className="ml-2 font-medium">{platform.first_positions || 0}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">👍:</span>
                          <span className="ml-1 font-medium text-green-600">{platform.positive_sentiment || 0}</span>
                          <span className="mx-1">/</span>
                          <span className="text-slate-500">👎:</span>
                          <span className="ml-1 font-medium text-red-600">{platform.negative_sentiment || 0}</span>
                        </div>
                      </div>
                      <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getPlatformColor(platform.platform)} rounded-full transition-all`}
                          style={{ width: `${platform.mention_rate}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Share of Voice */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <PieChart size={18} />
                  Share of Voice
                </h3>
              </div>
              <div className="p-5">
                <div className="space-y-3">
                  {data?.share_of_voice_breakdown?.map((entity, idx) => (
                    <div key={entity.entity} className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold"
                        style={{ backgroundColor: entity.is_brand ? '#3B82F6' : `hsl(${idx * 60}, 70%, 50%)` }}
                      >
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className={`text-sm ${entity.is_brand ? 'font-bold text-blue-600' : 'text-slate-700'}`}>
                            {entity.entity} {entity.is_brand && '⭐'}
                          </span>
                          <span className="text-sm font-medium">{entity.share}%</span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${entity.is_brand ? 'bg-blue-500' : 'bg-slate-400'}`}
                            style={{ width: `${entity.share}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {data?.competitors?.length === 0 && (
                  <div className="text-center py-8 text-slate-500">
                    <Users className="mx-auto mb-2 opacity-50" size={32} />
                    <p className="text-sm">No competitor data yet</p>
                    <p className="text-xs">Start monitoring to track competitors</p>
                  </div>
                )}
              </div>
            </div>

            {/* Trend Chart */}
            <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Activity size={18} />
                  Visibility Trend
                </h3>
              </div>
              <div className="p-5">
                {data?.trend_data?.length > 0 ? (
                  <div className="h-48 flex items-end gap-1">
                    {data.trend_data.slice(-14).map((day, idx) => {
                      const maxMentions = Math.max(...data.trend_data.map(d => d.brand_mentions + d.competitor_mentions), 1);
                      const brandHeight = (day.brand_mentions / maxMentions) * 100;
                      const compHeight = (day.competitor_mentions / maxMentions) * 100;
                      
                      return (
                        <div key={day.date} className="flex-1 flex flex-col items-center gap-1" title={`${day.date}: ${day.brand_mentions} brand, ${day.competitor_mentions} competitor mentions`}>
                          <div className="w-full flex flex-col gap-0.5" style={{ height: '160px' }}>
                            <div 
                              className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                              style={{ height: `${brandHeight}%`, minHeight: day.brand_mentions > 0 ? '4px' : '0' }}
                            />
                            <div 
                              className="w-full bg-slate-300 rounded-b transition-all hover:bg-slate-400"
                              style={{ height: `${compHeight}%`, minHeight: day.competitor_mentions > 0 ? '4px' : '0' }}
                            />
                          </div>
                          <span className="text-xs text-slate-400 transform -rotate-45 origin-left">
                            {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="h-48 flex items-center justify-center text-slate-400">
                    <div className="text-center">
                      <Activity className="mx-auto mb-2 opacity-50" size={32} />
                      <p className="text-sm">No trend data available</p>
                    </div>
                  </div>
                )}
                <div className="flex items-center justify-center gap-6 mt-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded" />
                    <span className="text-slate-600">Your Brand</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-slate-300 rounded" />
                    <span className="text-slate-600">Competitors</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Position Distribution */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Award size={18} />
                  Position Distribution
                </h3>
              </div>
              <div className="p-5">
                <div className="space-y-4">
                  {[1, 2, 3].map(pos => {
                    const count = data?.position_distribution?.[pos] || 0;
                    const total = Object.values(data?.position_distribution || {}).reduce((a, b) => a + b, 0) || 1;
                    const percent = ((count / total) * 100).toFixed(1);
                    
                    return (
                      <div key={pos}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm flex items-center gap-2">
                            {pos === 1 && '🥇'}
                            {pos === 2 && '🥈'}
                            {pos === 3 && '🥉'}
                            Position #{pos}
                          </span>
                          <span className="text-sm font-medium">{count} ({percent}%)</span>
                        </div>
                        <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${
                              pos === 1 ? 'bg-yellow-400' : pos === 2 ? 'bg-gray-400' : 'bg-orange-400'
                            }`}
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm">Position #4+</span>
                      <span className="text-sm font-medium">{data?.position_distribution?.other || 0}</span>
                    </div>
                    <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-slate-400 rounded-full"
                        style={{ width: `${((data?.position_distribution?.other || 0) / (Object.values(data?.position_distribution || {}).reduce((a, b) => a + b, 0) || 1)) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'platforms' && (
          <div className="space-y-6">
            {/* Platform Comparison Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900">AI Platform Comparison</h3>
                <p className="text-sm text-slate-500 mt-1">Click a platform to filter all analytics</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Platform</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Visibility Rate</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Avg Position</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">First Positions</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Total Checks</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Sentiment</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {data?.platform_breakdown?.map((platform) => (
                      <tr 
                        key={platform.platform} 
                        className={`hover:bg-slate-50 cursor-pointer ${platformFilter === platform.platform ? 'bg-blue-50' : ''}`}
                        onClick={() => setPlatformFilter(platformFilter === platform.platform ? 'all' : platform.platform)}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <span className="text-2xl">{getPlatformIcon(platform.platform)}</span>
                            <div>
                              <p className="font-medium text-slate-900">{platform.display_name}</p>
                              <p className="text-xs text-slate-500">{platform.mentions} mentions</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`text-lg font-bold ${getVisibilityColor(platform.mention_rate)}`}>
                            {platform.mention_rate}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          {getPositionBadge(platform.avg_position)}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="font-medium">{platform.first_positions || 0}</span>
                        </td>
                        <td className="px-6 py-4 text-center text-slate-600">
                          {platform.total_checks}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <span className="text-green-600 text-sm">+{platform.positive_sentiment || 0}</span>
                            <span className="text-slate-300">/</span>
                            <span className="text-red-600 text-sm">-{platform.negative_sentiment || 0}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <button 
                            className={`px-3 py-1 text-xs rounded-full transition-colors ${
                              platformFilter === platform.platform 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            }`}
                          >
                            {platformFilter === platform.platform ? 'Selected' : 'Filter'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Platform-specific insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data?.platform_breakdown?.map((platform) => (
                <div key={platform.platform} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-3xl">{getPlatformIcon(platform.platform)}</span>
                    <div>
                      <h4 className="font-semibold text-slate-900">{platform.display_name}</h4>
                      <p className="text-sm text-slate-500">Performance Breakdown</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className={`text-2xl font-bold ${getVisibilityColor(platform.mention_rate)}`}>
                        {platform.mention_rate}%
                      </p>
                      <p className="text-xs text-slate-500">Visibility</p>
                    </div>
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-slate-900">
                        {platform.avg_position ? `#${platform.avg_position}` : '-'}
                      </p>
                      <p className="text-xs text-slate-500">Avg Position</p>
                    </div>
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-yellow-600">
                        {platform.first_positions || 0}
                      </p>
                      <p className="text-xs text-slate-500">🥇 First Place</p>
                    </div>
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold">
                        <span className="text-green-600">{platform.positive_sentiment || 0}</span>
                        <span className="text-slate-300 mx-1">/</span>
                        <span className="text-red-600">{platform.negative_sentiment || 0}</span>
                      </p>
                      <p className="text-xs text-slate-500">👍 / 👎</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'competitors' && (
          <div className="space-y-6">
            {/* Competitor Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900">Competitor Intelligence</h3>
                <p className="text-sm text-slate-500 mt-1">Track how competitors appear in AI responses</p>
              </div>
              
              {data?.competitors?.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Competitor</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Mentions</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Share of Voice</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Avg Position</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Above Your Brand</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Comparisons</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Your Win Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {data.competitors.map((competitor, idx) => (
                        <tr key={competitor.name} className="hover:bg-slate-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm`}
                                style={{ backgroundColor: `hsl(${idx * 60}, 70%, 50%)` }}
                              >
                                {idx + 1}
                              </div>
                              <span className="font-medium text-slate-900">{competitor.name}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center font-medium">{competitor.mentions}</td>
                          <td className="px-6 py-4 text-center">
                            <span className={`font-medium ${competitor.share_of_voice > data.kpis.share_of_voice ? 'text-red-600' : 'text-green-600'}`}>
                              {competitor.share_of_voice}%
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            {getPositionBadge(competitor.avg_position)}
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className={`font-medium ${competitor.above_brand_count > 0 ? 'text-red-600' : 'text-green-600'}`}>
                              {competitor.above_brand_count}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">{competitor.direct_comparisons}</td>
                          <td className="px-6 py-4 text-center">
                            <span className={`font-medium ${competitor.win_rate >= 50 ? 'text-green-600' : 'text-red-600'}`}>
                              {competitor.win_rate}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-12 text-center">
                  <Users className="mx-auto mb-4 text-slate-300" size={48} />
                  <h4 className="text-lg font-medium text-slate-700 mb-2">No Competitor Data Yet</h4>
                  <p className="text-slate-500 mb-4">Start monitoring prompts to track competitor mentions</p>
                  <button 
                    onClick={() => navigate('/prompts')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Go to Prompts
                  </button>
                </div>
              )}
            </div>

            {/* Competitor Platform Breakdown */}
            {data?.competitors?.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {data.competitors.slice(0, 4).map((competitor, idx) => (
                  <div key={competitor.name} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold`}
                          style={{ backgroundColor: `hsl(${idx * 60}, 70%, 50%)` }}
                        >
                          {idx + 1}
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-900">{competitor.name}</h4>
                          <p className="text-sm text-slate-500">{competitor.mentions} total mentions</p>
                        </div>
                      </div>
                      <span className={`text-lg font-bold ${competitor.share_of_voice > data.kpis.share_of_voice ? 'text-red-600' : 'text-green-600'}`}>
                        {competitor.share_of_voice}%
                      </span>
                    </div>
                    
                    <p className="text-xs text-slate-500 mb-2">Mentions by Platform:</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      {Object.entries(competitor.platform_breakdown || {}).map(([platform, count]) => (
                        <span key={platform} className="px-2 py-1 bg-slate-100 rounded-full text-xs flex items-center gap-1">
                          {getPlatformIcon(platform)} {count}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'opportunities' && (
          <div className="space-y-6">
            {/* Opportunities List */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Target size={18} />
                  Visibility Opportunities
                </h3>
                <p className="text-sm text-slate-500 mt-1">Prompts where you can improve AI visibility</p>
              </div>
              
              {data?.opportunities?.length > 0 ? (
                <div className="divide-y divide-slate-100">
                  {data.opportunities.map((opp, idx) => (
                    <div key={opp.prompt_id} className="p-5 hover:bg-slate-50">
                      <div className="flex items-start gap-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                          opp.opportunity_type === 'no_visibility' ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'
                        }`}>
                          {opp.opportunity_type === 'no_visibility' ? <AlertTriangle size={20} /> : <TrendingUp size={20} />}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <p className="font-medium text-slate-900 mb-1">{opp.prompt_text}</p>
                              <div className="flex items-center gap-4 text-sm text-slate-500">
                                <span>Current: {opp.current_mention_rate}% visibility</span>
                                <span>Score: {opp.priority_score}</span>
                                <span>Volume: {opp.estimated_volume}</span>
                              </div>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              opp.opportunity_type === 'no_visibility' 
                                ? 'bg-red-100 text-red-700' 
                                : 'bg-yellow-100 text-yellow-700'
                            }`}>
                              {opp.opportunity_type === 'no_visibility' ? 'Not Visible' : 'Low Visibility'}
                            </span>
                          </div>
                          
                          {opp.competitors_present?.length > 0 && (
                            <div className="mt-3 p-3 bg-orange-50 rounded-lg">
                              <p className="text-xs text-orange-700 font-medium mb-1">
                                ⚠️ Competitors appearing in this query:
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {opp.competitors_present.map(comp => (
                                  <span key={comp} className="px-2 py-0.5 bg-orange-100 text-orange-800 rounded text-xs">
                                    {comp}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          <div className="mt-3 flex items-center gap-2">
                            <span className="text-xs text-slate-500">Recommended:</span>
                            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                              {opp.recommended_action}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center">
                  <CheckCircle2 className="mx-auto mb-4 text-green-400" size={48} />
                  <h4 className="text-lg font-medium text-slate-700 mb-2">Great Job!</h4>
                  <p className="text-slate-500">All monitored prompts have good visibility</p>
                </div>
              )}
            </div>

            {/* Prompt Performance Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-5 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900">Monitored Prompt Performance</h3>
              </div>
              
              {data?.prompt_performance?.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Prompt</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Visibility</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Avg Position</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Checks</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-slate-500 uppercase">Platforms</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {data.prompt_performance.map((prompt) => (
                        <tr key={prompt.prompt_id} className="hover:bg-slate-50">
                          <td className="px-6 py-4">
                            <p className="text-sm text-slate-900 font-medium line-clamp-2">{prompt.prompt_text}</p>
                            <p className="text-xs text-slate-500 mt-1">{prompt.category}</p>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className={`text-lg font-bold ${getVisibilityColor(prompt.mention_rate)}`}>
                              {prompt.mention_rate}%
                            </span>
                          </td>
                          <td className="px-6 py-4 text-center">
                            {getPositionBadge(prompt.avg_position)}
                          </td>
                          <td className="px-6 py-4 text-center text-slate-600">
                            {prompt.check_count}
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="flex items-center justify-center gap-1">
                              {Object.entries(prompt.platform_breakdown || {}).map(([platform, count]) => (
                                <span key={platform} title={`${platform}: ${count}`} className="text-lg">
                                  {getPlatformIcon(platform)}
                                </span>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-12 text-center">
                  <Search className="mx-auto mb-4 text-slate-300" size={48} />
                  <h4 className="text-lg font-medium text-slate-700 mb-2">No Monitored Prompts</h4>
                  <p className="text-slate-500 mb-4">Start monitoring prompts to see performance data</p>
                  <button 
                    onClick={() => navigate('/prompts')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Go to Prompts
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Info Footer */}
        <div className="mt-8 p-4 bg-blue-50 rounded-xl border border-blue-100">
          <div className="flex items-start gap-3">
            <Info className="text-blue-500 flex-shrink-0 mt-0.5" size={18} />
            <div>
              <p className="text-sm text-blue-800 font-medium">About This Dashboard</p>
              <p className="text-sm text-blue-700 mt-1">
                This analytics dashboard tracks your brand's visibility across AI platforms (ChatGPT, Claude, Gemini, Perplexity). 
                Start monitoring prompts from the Prompts page to see detailed analytics. 
                Use the platform and category filters to drill down into specific data.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
