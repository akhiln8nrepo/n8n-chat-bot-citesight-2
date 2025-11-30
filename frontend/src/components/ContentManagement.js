import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { FileText, Plus, Eye, TrendingUp, X, Sparkles } from 'lucide-react';
import Navigation from './Navigation';
import { toast } from 'sonner';

const ContentManagement = () => {
  const navigate = useNavigate();
  const [content, setContent] = useState([]);
  const [publishers, setPublishers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showPublisherModal, setShowPublisherModal] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const [visibilityData, setVisibilityData] = useState(null);

  const [newContent, setNewContent] = useState({
    publisher_id: '',
    title: '',
    url: '',
    content_text: ''
  });

  const [newPublisher, setNewPublisher] = useState({
    name: '',
    email: '',
    website: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Get or create publisher for logged-in user
      const publisherRes = await axios.get('/publishers/me');
      setPublishers([publisherRes.data]);
      
      // Get content
      const contentRes = await axios.get('/content');
      setContent(contentRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
      
      // Don't show error toast for 401 - the axios interceptor will handle redirect
      if (error.response?.status !== 401) {
        toast.error('Failed to load data');
      }
    }
  };

  const handleAddPublisher = async () => {
    if (!newPublisher.name || !newPublisher.email || !newPublisher.website) {
      toast.error('Please fill all publisher fields');
      return;
    }

    try {
      await axios.post('/publishers', newPublisher);
      toast.success('Publisher added successfully!');
      setShowPublisherModal(false);
      setNewPublisher({ name: '', email: '', website: '' });
      fetchData();
    } catch (error) {
      console.error('Error adding publisher:', error);
      toast.error('Failed to add publisher');
    }
  };

  const handleAddContent = async () => {
    if (!newContent.publisher_id || !newContent.title || !newContent.url || !newContent.content_text) {
      toast.error('Please fill all fields');
      return;
    }

    try {
      await axios.post('/content', newContent);
      toast.success('Content added and visibility tracking started!');
      setShowAddModal(false);
      setNewContent({ publisher_id: '', title: '', url: '', content_text: '' });
      fetchData();
    } catch (error) {
      console.error('Error adding content:', error);
      toast.error('Failed to add content');
    }
  };

  const viewVisibility = async (contentId) => {
    try {
      const response = await axios.get(`/visibility/${contentId}`);
      setVisibilityData(response.data);
      const content_item = content.find(c => c.id === contentId);
      setSelectedContent(content_item);
    } catch (error) {
      console.error('Error fetching visibility:', error);
      toast.error('Failed to load visibility data');
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
    <div className="dashboard-container" data-testid="content-management-page">
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-2">Content Management</h1>
            <p className="text-base text-slate-600">Track and monitor your content across AI platforms</p>
          </div>
          <div className="flex gap-3">
            <button
              data-testid="add-publisher-btn"
              onClick={() => setShowPublisherModal(true)}
              className="btn-secondary flex items-center gap-2"
            >
              <Plus size={20} />
              Publisher
            </button>
            <button
              data-testid="add-content-btn"
              onClick={() => setShowAddModal(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Plus size={20} />
              Add Content
            </button>
          </div>
        </div>

        {content.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <FileText size={64} className="mx-auto mb-4 text-slate-300" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No Content Yet</h3>
            <p className="text-slate-600 mb-6">Start by adding a publisher and then your first content to track.</p>
            <button
              data-testid="add-first-content-btn"
              onClick={() => {
                if (publishers.length === 0) {
                  setShowPublisherModal(true);
                } else {
                  setShowAddModal(true);
                }
              }}
              className="btn-primary"
            >
              {publishers.length === 0 ? 'Add Publisher First' : 'Add Your First Content'}
            </button>
          </div>
        ) : (
          <div className="data-table" data-testid="content-table">
            <table className="w-full">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>URL</th>
                  <th>Publisher</th>
                  <th>Added</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {content.map((item) => (
                  <tr key={item.id} data-testid={`content-row-${item.id}`}>
                    <td className="font-medium">{item.title}</td>
                    <td>
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline text-sm">
                        {item.url.substring(0, 40)}...
                      </a>
                    </td>
                    <td>
                      {publishers.find(p => p.id === item.publisher_id)?.name || 'Unknown'}
                    </td>
                    <td className="text-sm text-slate-600">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <button
                          data-testid={`view-visibility-${item.id}`}
                          onClick={() => viewVisibility(item.id)}
                          className="flex items-center gap-2 text-sky-600 hover:text-sky-700 font-medium text-sm"
                        >
                          <Eye size={16} />
                          Visibility
                        </button>
                        <button
                          onClick={() => navigate(`/content/${item.id}`)}
                          className="flex items-center gap-2 text-purple-600 hover:text-purple-700 font-medium text-sm"
                        >
                          <Sparkles size={16} />
                          Optimize
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Publisher Modal */}
      {showPublisherModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="add-publisher-modal">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Add Publisher</h2>
              <button
                data-testid="close-publisher-modal"
                onClick={() => setShowPublisherModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="form-label">Publisher Name</label>
                <input
                  data-testid="publisher-name-input"
                  type="text"
                  className="form-input"
                  placeholder="Tech News Daily"
                  value={newPublisher.name}
                  onChange={(e) => setNewPublisher({...newPublisher, name: e.target.value})}
                />
              </div>

              <div>
                <label className="form-label">Email</label>
                <input
                  data-testid="publisher-email-input"
                  type="email"
                  className="form-input"
                  placeholder="contact@technews.com"
                  value={newPublisher.email}
                  onChange={(e) => setNewPublisher({...newPublisher, email: e.target.value})}
                />
              </div>

              <div>
                <label className="form-label">Website</label>
                <input
                  data-testid="publisher-website-input"
                  type="url"
                  className="form-input"
                  placeholder="https://technews.com"
                  value={newPublisher.website}
                  onChange={(e) => setNewPublisher({...newPublisher, website: e.target.value})}
                />
              </div>

              <button
                data-testid="submit-publisher-btn"
                onClick={handleAddPublisher}
                className="btn-primary w-full"
              >
                Add Publisher
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Content Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="add-content-modal">
          <div className="bg-white rounded-xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Add New Content</h2>
              <button
                data-testid="close-content-modal"
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={24} />
              </button>
            </div>

            {publishers.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-slate-600 mb-4">Please add a publisher first before adding content.</p>
                <button
                  data-testid="go-to-publisher-btn"
                  onClick={() => {
                    setShowAddModal(false);
                    setShowPublisherModal(true);
                  }}
                  className="btn-primary"
                >
                  Add Publisher
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="form-label">Publisher</label>
                  <select
                    data-testid="publisher-select"
                    className="form-input"
                    value={newContent.publisher_id}
                    onChange={(e) => setNewContent({...newContent, publisher_id: e.target.value})}
                  >
                    <option value="">Select a publisher</option>
                    {publishers.map((pub) => (
                      <option key={pub.id} value={pub.id}>{pub.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="form-label">Content Title</label>
                  <input
                    data-testid="content-title-input"
                    type="text"
                    className="form-input"
                    placeholder="How AI is Transforming Content Marketing"
                    value={newContent.title}
                    onChange={(e) => setNewContent({...newContent, title: e.target.value})}
                  />
                </div>

                <div>
                  <label className="form-label">URL</label>
                  <input
                    data-testid="content-url-input"
                    type="url"
                    className="form-input"
                    placeholder="https://example.com/article"
                    value={newContent.url}
                    onChange={(e) => setNewContent({...newContent, url: e.target.value})}
                  />
                </div>

                <div>
                  <label className="form-label">Content Text (for analysis)</label>
                  <textarea
                    data-testid="content-text-input"
                    className="form-input"
                    rows="6"
                    placeholder="Paste your article content here for GEO analysis..."
                    value={newContent.content_text}
                    onChange={(e) => setNewContent({...newContent, content_text: e.target.value})}
                  />
                </div>

                <button
                  data-testid="submit-content-btn"
                  onClick={handleAddContent}
                  className="btn-primary w-full"
                >
                  Add Content & Start Tracking
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Visibility Modal */}
      {visibilityData && selectedContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="visibility-modal">
          <div className="bg-white rounded-xl p-8 max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Visibility Report</h2>
                <p className="text-sm text-slate-600 mt-1">{selectedContent.title}</p>
              </div>
              <button
                data-testid="close-visibility-modal"
                onClick={() => {
                  setVisibilityData(null);
                  setSelectedContent(null);
                }}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4">
              {visibilityData.map((record, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    record.is_present ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}
                  data-testid={`visibility-record-${index}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-3">
                      <TrendingUp size={20} className={record.is_present ? 'text-green-600' : 'text-red-600'} />
                      <h3 className="font-bold text-slate-900">{record.platform}</h3>
                    </div>
                    <span className={`visibility-badge ${
                      record.visibility_score >= 70 ? '' :
                      record.visibility_score >= 50 ? 'medium' : 'low'
                    }`}>
                      {record.visibility_score}% Visibility
                    </span>
                  </div>
                  
                  {record.is_present ? (
                    <div>
                      <p className="text-sm text-slate-700 mb-2">{record.summary_snippet}</p>
                      <p className="text-xs text-slate-500">Position: #{record.position}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-600">Content not currently visible in AI summaries</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentManagement;