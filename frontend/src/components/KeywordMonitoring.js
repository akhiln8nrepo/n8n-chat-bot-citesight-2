import { useState, useEffect } from 'react';
import axios from 'axios';
import { Target, Plus, X } from 'lucide-react';
import Navigation from './Navigation';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const KeywordMonitoring = () => {
  const [content, setContent] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedContentId, setSelectedContentId] = useState('');

  const [newKeyword, setNewKeyword] = useState({
    content_id: '',
    keyword: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const contentRes = await axios.get(`${API}/content`);
      setContent(contentRes.data);
      
      if (contentRes.data.length > 0) {
        const allKeywords = [];
        for (const item of contentRes.data) {
          try {
            const keywordsRes = await axios.get(`${API}/keywords/${item.id}`);
            allKeywords.push(...keywordsRes.data);
          } catch (error) {
            console.error(`Error fetching keywords for content ${item.id}:`, error);
          }
        }
        setKeywords(allKeywords);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
      toast.error('Failed to load data');
    }
  };

  const handleAddKeyword = async () => {
    if (!newKeyword.content_id || !newKeyword.keyword) {
      toast.error('Please select content and enter a keyword');
      return;
    }

    try {
      await axios.post(`${API}/keywords`, newKeyword);
      toast.success('Keyword added and tracking started!');
      setShowAddModal(false);
      setNewKeyword({ content_id: '', keyword: '' });
      fetchData();
    } catch (error) {
      console.error('Error adding keyword:', error);
      toast.error('Failed to add keyword');
    }
  };

  const filterKeywordsByContent = (contentId) => {
    if (!contentId) return keywords;
    return keywords.filter(k => k.content_id === contentId);
  };

  const filteredKeywords = filterKeywordsByContent(selectedContentId);

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
    <div className="dashboard-container" data-testid="keyword-monitoring-page">
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">Keyword Monitoring</h1>
            <p className="text-base text-slate-600">Track keyword performance across AI platforms</p>
          </div>
          <button
            data-testid="add-keyword-btn"
            onClick={() => setShowAddModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            Add Keyword
          </button>
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

        {filteredKeywords.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <Target size={64} className="mx-auto mb-4 text-slate-300" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No Keywords Tracked</h3>
            <p className="text-slate-600 mb-6">Start monitoring keywords to see how they perform across AI platforms.</p>
            <button
              data-testid="add-first-keyword-btn"
              onClick={() => setShowAddModal(true)}
              className="btn-primary"
            >
              Add Your First Keyword
            </button>
          </div>
        ) : (
          <div className="space-y-4" data-testid="keywords-list">
            {filteredKeywords.map((keyword, index) => {
              const contentItem = content.find(c => c.id === keyword.content_id);
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl p-6 border border-slate-200 hover:border-sky-500 transition-colors"
                  data-testid={`keyword-card-${index}`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 mb-2">{keyword.keyword}</h3>
                      <p className="text-sm text-slate-600">Content: {contentItem?.title || 'Unknown'}</p>
                    </div>
                    {keyword.avg_position && (
                      <div className="text-right">
                        <div className="text-2xl font-bold text-sky-600">#{keyword.avg_position}</div>
                        <div className="text-xs text-slate-500">Avg Position</div>
                      </div>
                    )}
                  </div>

                  <div>
                    <p className="text-sm font-medium text-slate-700 mb-2">Found on platforms:</p>
                    <div className="flex flex-wrap gap-2">
                      {keyword.platforms_found && keyword.platforms_found.length > 0 ? (
                        keyword.platforms_found.map((platform, idx) => (
                          <span key={idx} className="platform-chip">
                            {platform}
                          </span>
                        ))
                      ) : (
                        <span className="text-sm text-slate-500">Not found on any platform yet</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Keyword Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="add-keyword-modal">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Add Keyword</h2>
              <button
                data-testid="close-keyword-modal"
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={24} />
              </button>
            </div>

            {content.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-slate-600 mb-4">Please add content first before tracking keywords.</p>
                <button
                  data-testid="go-to-content-btn"
                  onClick={() => window.location.href = '/content'}
                  className="btn-primary"
                >
                  Add Content
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="form-label">Select Content</label>
                  <select
                    data-testid="keyword-content-select"
                    className="form-input"
                    value={newKeyword.content_id}
                    onChange={(e) => setNewKeyword({...newKeyword, content_id: e.target.value})}
                  >
                    <option value="">Select content to track</option>
                    {content.map((item) => (
                      <option key={item.id} value={item.id}>{item.title}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="form-label">Keyword</label>
                  <input
                    data-testid="keyword-input"
                    type="text"
                    className="form-input"
                    placeholder="AI content marketing"
                    value={newKeyword.keyword}
                    onChange={(e) => setNewKeyword({...newKeyword, keyword: e.target.value})}
                  />
                  <p className="text-xs text-slate-500 mt-2">Enter a keyword or phrase to monitor across AI platforms</p>
                </div>

                <button
                  data-testid="submit-keyword-btn"
                  onClick={handleAddKeyword}
                  className="btn-primary w-full"
                >
                  Start Tracking Keyword
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default KeywordMonitoring;