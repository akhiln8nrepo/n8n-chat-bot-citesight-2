import { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, TrendingUp, Award } from 'lucide-react';
import Navigation from './Navigation';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompetitorAnalysis = () => {
  const [publishers, setPublishers] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPublisherId, setSelectedPublisherId] = useState('');

  useEffect(() => {
    fetchPublishers();
  }, []);

  const fetchPublishers = async () => {
    try {
      const response = await axios.get(`${API}/publishers`);
      setPublishers(response.data);
      if (response.data.length > 0) {
        setSelectedPublisherId(response.data[0].id);
        fetchCompetitors(response.data[0].id);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching publishers:', error);
      setLoading(false);
      toast.error('Failed to load publishers');
    }
  };

  const fetchCompetitors = async (publisherId) => {
    try {
      const response = await axios.get(`${API}/competitors?publisher_id=${publisherId}`);
      setCompetitors(response.data);
    } catch (error) {
      console.error('Error fetching competitors:', error);
      toast.error('Failed to load competitor data');
    }
  };

  const handlePublisherChange = (publisherId) => {
    setSelectedPublisherId(publisherId);
    fetchCompetitors(publisherId);
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
    <div className="dashboard-container" data-testid="competitor-analysis-page">
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">Competitor Analysis</h1>
          <p className="text-base text-slate-600">Benchmark your AI visibility against industry competitors</p>
        </div>

        {publishers.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <Users size={64} className="mx-auto mb-4 text-slate-300" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No Publishers Found</h3>
            <p className="text-slate-600 mb-6">Add a publisher first to view competitor analysis.</p>
            <button
              data-testid="go-to-content-btn"
              onClick={() => window.location.href = '/content'}
              className="btn-primary"
            >
              Add Publisher
            </button>
          </div>
        ) : (
          <>
            {/* Publisher Selector */}
            <div className="mb-6 bg-white p-4 rounded-xl border border-slate-200">
              <label className="form-label">Select Your Publisher</label>
              <select
                data-testid="publisher-select"
                className="form-input"
                value={selectedPublisherId}
                onChange={(e) => handlePublisherChange(e.target.value)}
              >
                {publishers.map((pub) => (
                  <option key={pub.id} value={pub.id}>{pub.name}</option>
                ))}
              </select>
            </div>

            {/* Competitor Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="competitors-grid">
              {competitors.map((competitor, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 border border-slate-200 hover:border-sky-500 transition-all hover:shadow-lg"
                  data-testid={`competitor-card-${index}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-lg flex items-center justify-center">
                      <Users size={24} className="text-white" />
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-slate-900">{competitor.visibility_score}%</div>
                      <div className="text-xs text-slate-500">GEO Score</div>
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 mb-2">{competitor.competitor_name}</h3>
                  <a
                    href={competitor.competitor_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-sky-600 hover:underline block mb-4"
                  >
                    {competitor.competitor_url}
                  </a>

                  <div className="mb-4">
                    <p className="text-xs font-medium text-slate-600 mb-2">Present on {competitor.platforms_present.length} platforms:</p>
                    <div className="flex flex-wrap gap-2">
                      {competitor.platforms_present.map((platform, idx) => (
                        <span key={idx} className="platform-chip text-xs">
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-500">Competitive Status</span>
                      {competitor.visibility_score > 80 ? (
                        <span className="flex items-center gap-1 text-xs font-bold text-green-600">
                          <Award size={14} />
                          Strong
                        </span>
                      ) : competitor.visibility_score > 60 ? (
                        <span className="flex items-center gap-1 text-xs font-bold text-yellow-600">
                          <TrendingUp size={14} />
                          Moderate
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-xs font-bold text-slate-600">
                          <TrendingUp size={14} />
                          Emerging
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Insights Section */}
            <div className="mt-8 bg-gradient-to-r from-sky-50 to-cyan-50 rounded-xl p-8 border border-sky-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-sky-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  <TrendingUp size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">Competitive Insights</h3>
                  <p className="text-sm text-slate-700 mb-3">
                    Your competitors are actively visible across multiple AI platforms. To improve your GEO Health Score:
                  </p>
                  <ul className="space-y-2 text-sm text-slate-700">
                    <li className="flex items-start gap-2">
                      <span className="text-sky-600 font-bold">•</span>
                      <span>Implement schema markup to enhance AI content understanding</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-sky-600 font-bold">•</span>
                      <span>Add FAQ sections with concise, structured answers</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-sky-600 font-bold">•</span>
                      <span>Optimize content with semantic chunking for better AI parsing</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CompetitorAnalysis;