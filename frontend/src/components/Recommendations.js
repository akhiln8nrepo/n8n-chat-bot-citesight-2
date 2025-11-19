import { useState, useEffect } from 'react';
import axios from 'axios';
import { Lightbulb, AlertCircle } from 'lucide-react';
import Navigation from './Navigation';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Recommendations = () => {
  const [content, setContent] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContentId, setSelectedContentId] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const contentRes = await axios.get(`${API}/content`);
      setContent(contentRes.data);
      
      if (contentRes.data.length > 0) {
        const allRecommendations = [];
        for (const item of contentRes.data) {
          try {
            const recRes = await axios.get(`${API}/recommendations/${item.id}`);
            allRecommendations.push(...recRes.data);
          } catch (error) {
            console.error(`Error fetching recommendations for content ${item.id}:`, error);
          }
        }
        setRecommendations(allRecommendations);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
      toast.error('Failed to load data');
    }
  };

  const filterRecommendationsByContent = (contentId) => {
    if (!contentId) return recommendations;
    return recommendations.filter(r => r.content_id === contentId);
  };

  const filteredRecommendations = filterRecommendationsByContent(selectedContentId);

  const groupedByPriority = {
    high: filteredRecommendations.filter(r => r.priority === 'high'),
    medium: filteredRecommendations.filter(r => r.priority === 'medium'),
    low: filteredRecommendations.filter(r => r.priority === 'low')
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
    <div className="dashboard-container" data-testid="recommendations-page">
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">GEO Recommendations</h1>
          <p className="text-base text-slate-600">AI-powered optimization tips to improve your content visibility</p>
        </div>

        {/* Filter */}
        <div className="mb-6 bg-white p-4 rounded-xl border border-slate-200">
          <label className="form-label">Filter by Content</label>
          <select
            data-testid="content-filter"
            className="form-input"
            value={selectedContentId}
            onChange={(e) => setSelectedContentId(e.target.value)}
          >
            <option value="">All Content</option>
            {content.map((item) => (
              <option key={item.id} value={item.id}>{item.title}</option>
            ))}
          </select>
        </div>

        {filteredRecommendations.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <Lightbulb size={64} className="mx-auto mb-4 text-slate-300" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No Recommendations Yet</h3>
            <p className="text-slate-600 mb-6">
              Add content to receive AI-powered GEO recommendations for optimization.
            </p>
            <button
              data-testid="go-to-content-btn"
              onClick={() => window.location.href = '/content'}
              className="btn-primary"
            >
              Add Content
            </button>
          </div>
        ) : (
          <div className="space-y-8" data-testid="recommendations-list">
            {/* High Priority */}
            {groupedByPriority.high.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle size={24} className="text-red-600" />
                  <h2 className="text-2xl font-bold text-slate-900">High Priority</h2>
                </div>
                <div className="space-y-3">
                  {groupedByPriority.high.map((rec, index) => {
                    const contentItem = content.find(c => c.id === rec.content_id);
                    return (
                      <div
                        key={index}
                        className="recommendation-card priority-high"
                        data-testid={`recommendation-high-${index}`}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <span className="priority-badge high">HIGH PRIORITY</span>
                          <span className="text-xs text-slate-500">{contentItem?.title || 'Unknown'}</span>
                        </div>
                        <h3 className="font-bold text-slate-900 mb-2">{rec.recommendation_type}</h3>
                        <p className="text-sm text-slate-700 leading-relaxed">{rec.recommendation_text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Medium Priority */}
            {groupedByPriority.medium.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Lightbulb size={24} className="text-yellow-600" />
                  <h2 className="text-2xl font-bold text-slate-900">Medium Priority</h2>
                </div>
                <div className="space-y-3">
                  {groupedByPriority.medium.map((rec, index) => {
                    const contentItem = content.find(c => c.id === rec.content_id);
                    return (
                      <div
                        key={index}
                        className="recommendation-card priority-medium"
                        data-testid={`recommendation-medium-${index}`}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <span className="priority-badge medium">MEDIUM PRIORITY</span>
                          <span className="text-xs text-slate-500">{contentItem?.title || 'Unknown'}</span>
                        </div>
                        <h3 className="font-bold text-slate-900 mb-2">{rec.recommendation_type}</h3>
                        <p className="text-sm text-slate-700 leading-relaxed">{rec.recommendation_text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Low Priority */}
            {groupedByPriority.low.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Lightbulb size={24} className="text-green-600" />
                  <h2 className="text-2xl font-bold text-slate-900">Low Priority</h2>
                </div>
                <div className="space-y-3">
                  {groupedByPriority.low.map((rec, index) => {
                    const contentItem = content.find(c => c.id === rec.content_id);
                    return (
                      <div
                        key={index}
                        className="recommendation-card priority-low"
                        data-testid={`recommendation-low-${index}`}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <span className="priority-badge low">LOW PRIORITY</span>
                          <span className="text-xs text-slate-500">{contentItem?.title || 'Unknown'}</span>
                        </div>
                        <h3 className="font-bold text-slate-900 mb-2">{rec.recommendation_type}</h3>
                        <p className="text-sm text-slate-700 leading-relaxed">{rec.recommendation_text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;