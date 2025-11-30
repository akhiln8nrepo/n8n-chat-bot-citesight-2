import { useState } from 'react';
import axios from '@/utils/axios';
import { Sparkles, CheckCircle2, Loader2, Layout, FileText, X, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const ContentRecommendations = ({ contentId, onApply, onViewUpdated }) => {
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('base');
  const [showOptimizedModal, setShowOptimizedModal] = useState(false);
  const [optimizedContent, setOptimizedContent] = useState(null);

  const generateRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `/content/${contentId}/recommendations?template_id=${selectedTemplate}`
      );
      
      setRecommendations(response.data);
      toast.success('Recommendations generated!');
    } catch (error) {
      console.error('Error generating recommendations:', error);
      toast.error('Failed to generate recommendations');
    } finally {
      setLoading(false);
    }
  };

  const applyRecommendations = async () => {
    if (!recommendations) return;

    setApplying(true);
    try {
      const response = await axios.post(
        `/content/${contentId}/apply-recommendations`,
        { content_id: contentId, recommendations }
      );
      
      setOptimizedContent(response.data);
      setShowOptimizedModal(true);
      toast.success('Recommendations applied successfully!');
      
      if (onApply) {
        onApply(response.data);
      }
    } catch (error) {
      console.error('Error applying recommendations:', error);
      toast.error('Failed to apply recommendations');
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <h3 className="text-lg font-bold text-slate-900 mb-4">Content Optimization</h3>
        
        <div className="space-y-4">
          <div>
            <label className="form-label">Select Optimization Template</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="form-input"
            >
              <option value="base">Universal Template (All Models)</option>
              <option value="chatgpt">ChatGPT Specific</option>
              <option value="perplexity">Perplexity AI Specific</option>
              <option value="claude">Claude AI Specific</option>
              <option value="llama">LLaMA Specific</option>
              <option value="deepseek">DeepSeek Specific</option>
            </select>
          </div>

          <button
            onClick={generateRecommendations}
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Generate Recommendations
              </>
            )}
          </button>
        </div>
      </div>

      {recommendations && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <Layout size={20} className="text-blue-600" />
              <h4 className="font-bold text-slate-900">Optimized Header</h4>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-slate-900 font-medium">{recommendations.optimized_header}</p>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <FileText size={20} className="text-green-600" />
              <h4 className="font-bold text-slate-900">Subject Line</h4>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-slate-900 font-medium">{recommendations.subject_line}</p>
            </div>
          </div>

          {recommendations.faqs && recommendations.faqs.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <h4 className="font-bold text-slate-900 mb-3">Recommended FAQs</h4>
              <div className="space-y-3">
                {recommendations.faqs.slice(0, 3).map((faq, index) => (
                  <div key={index} className="p-4 bg-indigo-50 rounded-lg">
                    <div className="font-medium text-slate-900 mb-2">Q: {faq.question}</div>
                    <div className="text-sm text-slate-600">A: {faq.answer}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-xl font-bold mb-2">Ready to Optimize?</h4>
                <p className="text-blue-100">Apply all recommendations automatically</p>
              </div>
              <button
                onClick={applyRecommendations}
                disabled={applying}
                className="bg-white text-blue-600 px-6 py-3 rounded-lg font-bold hover:bg-blue-50 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {applying ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Applying...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={20} />
                    Implement All
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Optimized Content Modal */}
      {showOptimizedModal && optimizedContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-slate-900">Optimized Content</h3>
                <p className="text-sm text-slate-600 mt-1">Your content has been updated with all recommendations</p>
              </div>
              <button
                onClick={() => setShowOptimizedModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              <div className="space-y-6">
                {/* Title Comparison */}
                <div>
                  <h4 className="font-bold text-slate-900 mb-3">Title Comparison</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-slate-600 uppercase">Original</span>
                      </div>
                      <div className="bg-slate-100 p-4 rounded-lg border-2 border-slate-300">
                        <p className="text-slate-700 font-medium">{optimizedContent.original_title}</p>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 size={16} className="text-green-600" />
                        <span className="text-xs font-semibold text-green-700 uppercase">Optimized</span>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300">
                        <p className="text-slate-900 font-medium">{optimizedContent.optimized_title}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Content Comparison */}
                <div>
                  <h4 className="font-bold text-slate-900 mb-3">Content Comparison</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-slate-600 uppercase">Original Content</span>
                      </div>
                      <div className="bg-slate-100 p-4 rounded-lg border-2 border-slate-300 max-h-96 overflow-y-auto">
                        <p className="text-slate-700 text-sm whitespace-pre-wrap leading-relaxed">{optimizedContent.original_content}</p>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 size={16} className="text-green-600" />
                        <span className="text-xs font-semibold text-green-700 uppercase">Optimized Content</span>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300 max-h-96 overflow-y-auto">
                        <p className="text-slate-900 text-sm whitespace-pre-wrap leading-relaxed font-medium">{optimizedContent.optimized_content}</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-slate-600">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-slate-100 border-2 border-slate-300 rounded"></div>
                      <span>Original</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-green-50 border-2 border-green-300 rounded"></div>
                      <span>Optimized with AI improvements</span>
                    </div>
                  </div>
                </div>

                {/* Changes Summary */}
                {optimizedContent.changes_summary && optimizedContent.changes_summary.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 size={20} className="text-blue-600" />
                      <h4 className="font-bold text-slate-900">Changes Applied</h4>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <ul className="list-disc list-inside space-y-1">
                        {optimizedContent.changes_summary.map((change, index) => (
                          <li key={index} className="text-sm text-slate-700">{change}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="p-6 border-t border-slate-200 flex gap-3">
              <button
                onClick={() => {
                  setShowOptimizedModal(false);
                  if (onViewUpdated) {
                    onViewUpdated();
                  }
                }}
                className="btn-primary flex-1"
              >
                <CheckCircle2 size={18} className="mr-2" />
                View Updated Content
              </button>
              <button
                onClick={() => setShowOptimizedModal(false)}
                className="px-6 py-2 border border-slate-300 rounded-lg hover:bg-slate-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentRecommendations;