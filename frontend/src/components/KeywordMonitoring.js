import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { Target, Plus, Sparkles, Search, TrendingUp, ExternalLink } from 'lucide-react';
import Navigation from './Navigation';
import { toast } from 'sonner';

const KeywordMonitoring = () => {
  const navigate = useNavigate();
  const [content, setContent] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [contentKeywordMap, setContentKeywordMap] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const contentRes = await axios.get('/content');
      setContent(contentRes.data);
      
      const keywordsRes = await axios.get('/keywords');
      setKeywords(keywordsRes.data);
      
      // Create a map of content_id to keywords
      const kwMap = {};
      keywordsRes.data.forEach(kw => {
        if (!kwMap[kw.content_id]) {
          kwMap[kw.content_id] = [];
        }
        kwMap[kw.content_id].push(kw);
      });
      setContentKeywordMap(kwMap);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
      toast.error('Failed to load data');
    }
  };

  const handleAnalyzeKeyword = (contentId) => {
    navigate(`/content/${contentId}?tab=keyword-analysis`);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <Navigation />
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading keywords...</p>
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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Keyword Monitoring</h1>
            <p className="text-slate-600">Track and analyze keywords across your content with AI-powered insights</p>
          </div>
          <button
            onClick={() => navigate('/content')}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            Add Content & Keywords
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-600">Total Keywords</div>
              <Target size={20} className="text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-slate-900">{keywords.length}</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-600">Content Pieces</div>
              <TrendingUp size={20} className="text-green-600" />
            </div>
            <div className="text-3xl font-bold text-slate-900">{content.length}</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-600">Avg Keywords/Content</div>
              <Search size={20} className="text-purple-600" />
            </div>
            <div className="text-3xl font-bold text-slate-900">
              {content.length > 0 ? Math.round((keywords.length / content.length) * 10) / 10 : 0}
            </div>
          </div>
        </div>

        {/* Content & Keywords List */}
        {content.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <Target size={48} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No Content Yet</h3>
            <p className="text-slate-600 mb-6">Start by adding content and keywords to monitor</p>
            <button
              onClick={() => navigate('/content')}
              className="btn-primary"
            >
              Add Your First Content
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {content.map((item) => {
              const itemKeywords = contentKeywordMap[item.id] || [];
              return (
                <div key={item.id} className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-slate-900 mb-2">{item.title}</h3>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                      >
                        <ExternalLink size={14} />
                        {item.url}
                      </a>
                    </div>
                    <button
                      onClick={() => handleAnalyzeKeyword(item.id)}
                      className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      <Sparkles size={18} />
                      Analyze Keywords
                    </button>
                  </div>
                  
                  {itemKeywords.length > 0 ? (
                    <div>
                      <div className="text-sm text-slate-600 mb-2">Keywords:</div>
                      <div className="flex flex-wrap gap-2">
                        {itemKeywords.map((kw) => (
                          <div
                            key={kw.id}
                            className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium"
                          >
                            {kw.keyword}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-slate-400 italic">
                      No keywords added yet. Click "Analyze Keywords" to add and analyze.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default KeywordMonitoring;