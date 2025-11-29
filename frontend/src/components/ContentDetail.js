import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { ArrowLeft, FileText, Calendar, ExternalLink, Loader2, Tag, Plus, X } from 'lucide-react';
import Navigation from './Navigation';
import KeywordAnalysis from './KeywordAnalysis';
import ContentRecommendations from './ContentRecommendations';
import { toast } from 'sonner';

const ContentDetail = () => {
  const { contentId } = useParams();
  const navigate = useNavigate();
  const [content, setContent] = useState(null);
  const [keyword, setKeyword] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAddKeyword, setShowAddKeyword] = useState(false);
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => {
    fetchContentDetail();
  }, [contentId]);

  const fetchContentDetail = async () => {
    try {
      const response = await axios.get(`/content/${contentId}`);
      setContent(response.data);
      
      // Get all associated keywords
      try {
        const keywordRes = await axios.get(`/keywords`);
        const contentKeywords = keywordRes.data.filter(k => k.content_id === contentId);
        setKeywords(contentKeywords);
        if (contentKeywords.length > 0) {
          setKeyword(contentKeywords[0].keyword);
        }
      } catch (error) {
        console.error('Error fetching keywords:', error);
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
      await axios.post('/keywords', {
        content_id: contentId,
        keyword: newKeyword.trim()
      });
      
      toast.success('Keyword added successfully!');
      setNewKeyword('');
      setShowAddKeyword(false);
      fetchContentDetail(); // Refresh to show new keyword
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

  const handleRecommendationsApplied = (data) => {
    toast.success('Content updated with recommendations!');
    fetchContentDetail(); // Refresh content
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
              {!keyword && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6">
                  <p className="text-yellow-800">
                    No keyword associated with this content. Please add a keyword first.
                  </p>
                  <input
                    type="text"
                    placeholder="Enter keyword (e.g., Treadmill)"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    className="form-input mt-3"
                  />
                </div>
              )}
              {keyword && (
                <KeywordAnalysis
                  keyword={keyword}
                  contentId={contentId}
                  onAnalysisComplete={handleAnalysisComplete}
                />
              )}
            </div>
          )}

          {activeTab === 'recommendations' && (
            <ContentRecommendations
              contentId={contentId}
              onApply={handleRecommendationsApplied}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ContentDetail;
