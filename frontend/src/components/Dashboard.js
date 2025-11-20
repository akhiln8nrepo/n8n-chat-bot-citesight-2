import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { TrendingUp, FileText, Target, Award, AlertCircle, ArrowUpRight } from 'lucide-react';
import Navigation from './Navigation';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get('/dashboard/stats');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <Navigation />
        <div className="flex items-center justify-center h-screen">
          <div className="spinner" data-testid="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container" data-testid="dashboard-page">
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">
            Dashboard Overview
          </h1>
          <p className="text-base text-slate-600">
            Monitor your AI visibility performance across all platforms
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="metric-card" data-testid="total-content-metric">
            <div className="flex items-center justify-between mb-2">
              <FileText size={24} className="text-sky-500" />
              {stats?.total_content > 0 && (
                <span className="text-xs text-green-600 flex items-center gap-1">
                  <ArrowUpRight size={14} />
                  Active
                </span>
              )}
            </div>
            <div className="metric-value">{stats?.total_content || 0}</div>
            <div className="metric-label">Total Content Tracked</div>
          </div>

          <div className="metric-card" data-testid="avg-visibility-metric">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp size={24} className="text-sky-500" />
              <span className={`text-xs flex items-center gap-1 ${
                stats?.avg_visibility_score >= 70 ? 'text-green-600' : 
                stats?.avg_visibility_score >= 50 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {stats?.avg_visibility_score >= 70 ? '⬆' : stats?.avg_visibility_score >= 50 ? '→' : '⬇'}
              </span>
            </div>
            <div className="metric-value">{stats?.avg_visibility_score || 0}%</div>
            <div className="metric-label">Average Visibility Score</div>
          </div>

          <div className="metric-card" data-testid="keywords-metric">
            <div className="flex items-center justify-between mb-2">
              <Target size={24} className="text-sky-500" />
            </div>
            <div className="metric-value">{stats?.total_keywords || 0}</div>
            <div className="metric-label">Keywords Monitored</div>
          </div>

          <div className="metric-card" data-testid="platforms-metric">
            <div className="flex items-center justify-between mb-2">
              <Award size={24} className="text-sky-500" />
            </div>
            <div className="metric-value">
              {Object.keys(stats?.platforms_present || {}).length}
            </div>
            <div className="metric-label">Platforms Present</div>
          </div>
        </div>

        {/* Platform Presence */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Platform Presence</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="chart-container" data-testid="platform-presence-chart">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Content Visibility by Platform</h3>
              {stats?.platforms_present && Object.keys(stats.platforms_present).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(stats.platforms_present).map(([platform, count], index) => (
                    <div key={index}>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-slate-700">{platform}</span>
                        <span className="text-sm font-bold text-sky-600">{count} articles</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-sky-500 to-cyan-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${(count / stats.total_content) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <AlertCircle size={48} className="mx-auto mb-3 opacity-50" />
                  <p>No content tracked yet. Add your first content to see platform presence.</p>
                </div>
              )}
            </div>

            <div className="chart-container" data-testid="visibility-trend-chart">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Visibility Trend (Last 7 Days)</h3>
              {stats?.visibility_trend && stats.visibility_trend.length > 0 ? (
                <div className="space-y-3">
                  {stats.visibility_trend.map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-xs text-slate-600">{item.date}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-slate-200 rounded-full h-2">
                          <div
                            className="bg-sky-500 h-2 rounded-full"
                            style={{ width: `${item.score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-bold text-slate-900 w-12 text-right">{item.score}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <TrendingUp size={48} className="mx-auto mb-3 opacity-50" />
                  <p>Trend data will appear here once you have tracked content.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-2xl font-bold text-slate-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <button
              data-testid="add-content-btn"
              onClick={() => navigate('/content')}
              className="p-6 bg-white rounded-xl border border-slate-200 hover:border-sky-500 transition-all text-left group"
            >
              <FileText size={32} className="text-sky-500 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-slate-900 mb-2">Add New Content</h3>
              <p className="text-sm text-slate-600">Track a new article or page for AI visibility</p>
            </button>

            <button
              data-testid="monitor-keywords-btn"
              onClick={() => navigate('/keywords')}
              className="p-6 bg-white rounded-xl border border-slate-200 hover:border-sky-500 transition-all text-left group"
            >
              <Target size={32} className="text-sky-500 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-slate-900 mb-2">Monitor Keywords</h3>
              <p className="text-sm text-slate-600">Add keywords to track across AI platforms</p>
            </button>

            <button
              data-testid="view-recommendations-btn"
              onClick={() => navigate('/recommendations')}
              className="p-6 bg-white rounded-xl border border-slate-200 hover:border-sky-500 transition-all text-left group"
            >
              <Award size={32} className="text-sky-500 mb-3 group-hover:scale-110 transition-transform" />
              <h3 className="font-bold text-slate-900 mb-2">View Recommendations</h3>
              <p className="text-sm text-slate-600">Get AI-powered GEO optimization tips</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;