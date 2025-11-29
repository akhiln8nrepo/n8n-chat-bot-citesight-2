import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/utils/axios';
import { Lightbulb, Sparkles, CheckCircle2, FileText, ExternalLink } from 'lucide-react';
import Navigation from './Navigation';
import { toast } from 'sonner';

const Recommendations = () => {
  const navigate = useNavigate();
  const [content, setContent] = useState([]);
  const [optimizedContent, setOptimizedContent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const contentRes = await axios.get('/content');
      const allContent = contentRes.data;
      
      // Separate optimized vs unoptimized content
      const optimized = allContent.filter(c => c.optimized === true);
      const unoptimized = allContent.filter(c => c.optimized !== true);
      
      setOptimizedContent(optimized);
      setContent(unoptimized);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
      toast.error('Failed to load data');
    }
  };

  const handleOptimize = (contentId) => {
    navigate(`/content/${contentId}?tab=recommendations`);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <Navigation />
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading recommendations...</p>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">AI Content Recommendations</h1>
          <p className="text-slate-600">Optimize your content for better AI visibility with expert recommendations</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-600">Total Content</div>
              <FileText size={20} className="text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-slate-900">{content.length + optimizedContent.length}</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-600">Optimized</div>
              <CheckCircle2 size={20} className="text-green-600" />
            </div>
            <div className="text-3xl font-bold text-slate-900">{optimizedContent.length}</div>
          </div>
          
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-600">Needs Optimization</div>
              <Sparkles size={20} className="text-orange-600" />
            </div>
            <div className="text-3xl font-bold text-slate-900">{content.length}</div>
          </div>
        </div>

        {/* Needs Optimization Section */}
        {content.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Content Needing Optimization</h2>
            <div className="space-y-4">
              {content.map((item) => (
                <div key={item.id} className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-bold text-slate-900">{item.title}</h3>
                        <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                          Not Optimized
                        </span>
                      </div>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 mb-2"
                      >
                        <ExternalLink size={14} />
                        {item.url}
                      </a>
                      <p className="text-sm text-slate-600 line-clamp-2">{item.content_text}</p>
                    </div>
                    <button
                      onClick={() => handleOptimize(item.id)}
                      className="ml-4 flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all"
                    >
                      <Sparkles size={18} />
                      Get Recommendations
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Optimized Content Section */}
        {optimizedContent.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-4">Optimized Content</h2>
            <div className="space-y-4">
              {optimizedContent.map((item) => (
                <div key={item.id} className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 size={20} className="text-green-600" />
                        <h3 className="text-lg font-bold text-slate-900">{item.title}</h3>
                        <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
                          Optimized
                        </span>
                      </div>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1 mb-2"
                      >
                        <ExternalLink size={14} />
                        {item.url}
                      </a>
                      {item.optimization_date && (
                        <div className="text-sm text-slate-600">
                          Optimized on {new Date(item.optimization_date).toLocaleDateString()}
                        </div>
                      )}
                      {item.changes_applied && item.changes_applied.length > 0 && (
                        <div className="mt-2">
                          <div className="text-xs text-slate-600 mb-1">Changes Applied:</div>
                          <div className="flex flex-wrap gap-1">
                            {item.changes_applied.slice(0, 3).map((change, idx) => (
                              <span key={idx} className="text-xs bg-white text-slate-700 px-2 py-1 rounded">
                                {change}
                              </span>
                            ))}
                            {item.changes_applied.length > 3 && (
                              <span className="text-xs text-slate-500">+{item.changes_applied.length - 3} more</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => navigate(`/content/${item.id}`)}
                      className="ml-4 flex items-center gap-2 bg-white text-slate-700 px-4 py-2 rounded-lg hover:bg-slate-50 border border-slate-200 transition-all"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {content.length === 0 && optimizedContent.length === 0 && (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <Lightbulb size={48} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-xl font-bold text-slate-900 mb-2">No Content Yet</h3>
            <p className="text-slate-600 mb-6">Add content to start getting AI-powered optimization recommendations</p>
            <button
              onClick={() => navigate('/content')}
              className="btn-primary"
            >
              Add Your First Content
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;