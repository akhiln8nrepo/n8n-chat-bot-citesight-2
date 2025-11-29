import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import axios from '@/utils/axios';
import { ArrowLeft, FileText, Calendar, ExternalLink, Loader2, Tag, Plus, X } from 'lucide-react';
import Navigation from './Navigation';
import KeywordAnalysis from './KeywordAnalysis';
import ContentRecommendations from './ContentRecommendations';
import { toast } from 'sonner';

const ContentDetail = () => {
  const { contentId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [content, setContent] = useState(null);
  const [keyword, setKeyword] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'overview');
  const [showAddKeyword, setShowAddKeyword] = useState(false);
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => {
    fetchContentDetail();
  }, [contentId]);

  useEffect(() => {
    // Set tab from URL parameter
    const tabParam = searchParams.get('tab');
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  const fetchContentDetail = async () => {
    try {
      const response = await axios.get(`/content/${contentId}`);
      setContent(response.data);
      
      // Get keywords for this specific content
      try {
        // Try the specific endpoint first
        const keywordRes = await axios.get(`/keywords/${contentId}`);
        setKeywords(keywordRes.data);
        if (keywordRes.data.length > 0) {
          setKeyword(keywordRes.data[0].keyword);
        }
        console.log('Keywords fetched:', keywordRes.data.length);
      } catch (error) {
        console.error('Error fetching keywords:', error);
        // Try fallback to get all keywords
        try {
          const allKeywordsRes = await axios.get(`/keywords`);
          const contentKeywords = allKeywordsRes.data.filter(k => k.content_id === contentId);
          setKeywords(contentKeywords);
          if (contentKeywords.length > 0) {
            setKeyword(contentKeywords[0].keyword);
          }
          console.log('Keywords fetched (fallback):', contentKeywords.length);
        } catch (fallbackError) {
          console.error('Error fetching keywords (fallback):', fallbackError);
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching content:', error);
      toast.error('Failed to load content');
      setLoading(false);
    }
  };

  const handleAddKeyword = async () => {
    if (!newKeyword.trim()) {
      toast.error('Please enter a keyword');
      return;
    }

    try {
      const response = await axios.post('/keywords', {
        content_id: contentId,
        keyword: newKeyword.trim()
      });
      
      console.log('Keyword added:', response.data);
      toast.success('Keyword added successfully!');
      
      // Immediately add to local state
      const newKw = response.data;
      setKeywords([...keywords, newKw]);
      setKeyword(newKw.keyword); // Auto-select the newly added keyword
      
      setNewKeyword('');
      setShowAddKeyword(false);
      
      // Also refresh in background
      setTimeout(() => fetchContentDetail(), 500);
    } catch (error) {
      console.error('Error adding keyword:', error);
      toast.error('Failed to add keyword');
    }
  };

  const handleDeleteKeyword = async (keywordId) => {
    try {
      await axios.delete(`/keywords/${keywordId}`);
      toast.success('Keyword removed');
      fetchContentDetail(); // Refresh keywords list
    } catch (error) {
      console.error('Error deleting keyword:', error);
      toast.error('Failed to delete keyword');
    }
  };

  const handleAnalysisComplete = (analysisData) => {
    toast.success('Analysis complete! Check recommendations tab.');
  };

  const handleRecommendationsApplied = async (data) => {
    toast.success('Content updated with recommendations!');
    await fetchContentDetail(); // Refresh content
  };

  const handleViewUpdated = async () => {
    await fetchContentDetail(); // Refresh content
    setActiveTab('overview'); // Switch to overview to show updated content
    toast.success('View updated! Check the Overview tab.');
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <Navigation />
        <div className="flex items-center justify-center h-screen">
          <Loader2 size={48} className="animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="dashboard-container">
        <Navigation />
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-900 mb-4">Content Not Found</h2>
            <button onClick={() => navigate('/content')} className="btn-primary">
              Back to Content
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <Navigation />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/content')}
            className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-4"
          >
            <ArrowLeft size={20} />
            Back to Content
          </button>
          
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <FileText size={24} className="text-blue-600" />
              </div>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-slate-900 mb-2">{content.title}</h1>
                <div className="flex items-center gap-4 text-sm text-slate-600 mb-3">
                  <div className="flex items-center gap-1">
                    <Calendar size={16} />
                    {new Date(content.created_at).toLocaleDateString()}
                  </div>
                  <a
                    href={content.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-blue-600 hover:text-blue-700"
                  >
                    <ExternalLink size={16} />
                    View Live
                  </a>
                </div>
                
                {/* Keywords Section */}
                <div className="flex items-center gap-2 flex-wrap">
                  <div className="flex items-center gap-1 text-sm text-slate-600">
                    <Tag size={16} />
                    <span className="font-medium">Keywords:</span>
                  </div>
                  {keywords.length > 0 ? (
                    keywords.map((kw) => (
                      <div key={kw.id} className="flex items-center gap-1 bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">
                        <span>{kw.keyword}</span>
                        <button
                          onClick={() => handleDeleteKeyword(kw.id)}
                          className="hover:text-blue-900"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ))
                  ) : (
                    <span className="text-sm text-slate-400">No keywords added</span>
                  )}
                  <button
                    onClick={() => setShowAddKeyword(true)}
                    className="flex items-center gap-1 bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1 rounded-full text-sm"
                  >
                    <Plus size={14} />
                    Add Keyword
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl border border-slate-200 mb-6">
          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'overview'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('keyword-analysis')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'keyword-analysis'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Keyword Analysis
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'recommendations'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Recommendations
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && (
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Content Preview</h3>
              <div className="prose max-w-none">
                <p className="text-slate-700 whitespace-pre-wrap">{content.content_text}</p>
              </div>
            </div>
          )}

          {activeTab === 'keyword-analysis' && (
            <div>
              {keywords.length === 0 ? (
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
                  <p className="text-yellow-800 mb-4">
                    No keywords added yet. Please add a keyword first to analyze.
                  </p>
                  <button
                    onClick={() => setShowAddKeyword(true)}
                    className="btn-primary"
                  >
                    Add Your First Keyword
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Keyword Selector */}
                  <div className="bg-white rounded-xl p-6 border border-slate-200">
                    <div className="mb-4">
                      <div className="text-sm text-slate-600 mb-2">
                        You have {keywords.length} keyword(s) for this content
                      </div>
                      <label className="form-label">Select Keyword to Analyze</label>
                      <select
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                        className="form-input"
                      >
                        {keywords.map((kw) => (
                          <option key={kw.id} value={kw.keyword}>
                            {kw.keyword}
                          </option>
                        ))}
                      </select>
                    </div>
                    {!keyword && (
                      <div className="text-sm text-red-600">
                        Please select a keyword from the dropdown above
                      </div>
                    )}
                  </div>

                  {keyword ? (
                    <KeywordAnalysis
                      keyword={keyword}
                      contentId={contentId}
                      onAnalysisComplete={handleAnalysisComplete}
                    />
                  ) : (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
                      <p className="text-blue-800">
                        Select a keyword from the dropdown above to start analysis
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'recommendations' && (
            <ContentRecommendations
              contentId={contentId}
              onApply={handleRecommendationsApplied}
              onViewUpdated={handleViewUpdated}
            />
          )}
        </div>
      </div>

      {/* Add Keyword Modal */}
      {showAddKeyword && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-slate-900">Add New Keyword</h3>
              <button
                onClick={() => setShowAddKeyword(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="form-label">Keyword</label>
                <input
                  type="text"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  placeholder="e.g., Treadmill, Laptop, etc."
                  className="form-input"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={handleAddKeyword}
                  className="btn-primary flex-1"
                >
                  Add Keyword
                </button>
                <button
                  onClick={() => setShowAddKeyword(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentDetail;
