import { useState } from 'react';
import axios from '@/utils/axios';
import { Sparkles, CheckCircle2, Loader2, ArrowRight, Layout, FileText, Shield, HelpCircle, Code, Target, Zap } from 'lucide-react';
import { toast } from 'sonner';

const ContentRecommendations = ({ contentId, onApply }) => {
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('base');
  const [templates, setTemplates] = useState([]);

  const loadTemplates = async () => {
    try {
      const response = await axios.get('/templates');
      setTemplates(Object.values(response.data));
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

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

  useState(() => {
    loadTemplates();
  }, []);

  return (
    <div className="space-y-6">
      {/* Template Selection & Generate */}
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
                Generating Recommendations...
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

      {/* Recommendations Display */}
      {recommendations && (
        <div className="space-y-4">
          {/* Optimized Header */}
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <Layout size={20} className="text-blue-600" />
              <h4 className="font-bold text-slate-900">Optimized Header</h4>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-slate-900 font-medium">{recommendations.optimized_header}</p>
            </div>
          </div>

          {/* Subject Line */}
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-2 mb-3">
              <FileText size={20} className="text-green-600" />
              <h4 className="font-bold text-slate-900">Subject Line</h4>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-slate-900 font-medium">{recommendations.subject_line}</p>
            </div>
          </div>

          {/* Body Improvements */}
          {recommendations.body_improvements?.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center gap-2 mb-4">
                <FileText size={20} className="text-purple-600" />
                <h4 className="font-bold text-slate-900">Body Content Improvements</h4>
              </div>
              <div className="space-y-3">
                {recommendations.body_improvements.map((item, index) => (
                  <div key={index} className="p-4 bg-slate-50 rounded-lg">
                    <div className="font-medium text-slate-900 mb-2">{item.section}</div>
                    <div className="text-sm text-slate-600 mb-2">
                      <span className="font-medium">Current:</span> {item.current}
                    </div>
                    <div className="text-sm text-green-700 mb-2">
                      <span className="font-medium">Recommended:</span> {item.recommended}
                    </div>
                    <div className="text-xs text-blue-600">
                      <span className="font-medium">Why:</span> {item.reason}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Credibility Signals */}
          {recommendations.credibility_signals?.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center gap-2 mb-4">
                <Shield size={20} className="text-yellow-600" />
                <h4 className="font-bold text-slate-900">Credibility Signals</h4>
              </div>
              <div className="space-y-2">
                {recommendations.credibility_signals.map((signal, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
                    <CheckCircle2 size={18} className="text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-slate-900">{signal.type}</div>
                      <div className="text-sm text-slate-600">{signal.recommendation}</div>
                      <span className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${\n                        signal.priority === 'high' ? 'bg-red-100 text-red-700' :\n                        signal.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :\n                        'bg-green-100 text-green-700'\n                      }`}>\n                        {signal.priority} priority\n                      </span>\n                    </div>\n                  </div>\n                ))}\n              </div>\n            </div>\n          )}

          {/* FAQs */}
          {recommendations.faqs?.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center gap-2 mb-4">
                <HelpCircle size={20} className="text-indigo-600" />
                <h4 className="font-bold text-slate-900">Recommended FAQs</h4>
              </div>
              <div className="space-y-3">
                {recommendations.faqs.map((faq, index) => (
                  <div key={index} className="p-4 bg-indigo-50 rounded-lg">
                    <div className="font-medium text-slate-900 mb-2">Q: {faq.question}</div>
                    <div className="text-sm text-slate-600">A: {faq.answer}</div>
                  </div>
                ))}\n              </div>\n            </div>\n          )}\n\n          {/* Keyword Optimization */}\n          {recommendations.keyword_optimization && (\n            <div className=\"bg-white rounded-xl p-6 border border-slate-200\">\n              <div className=\"flex items-center gap-2 mb-4\">\n                <Target size={20} className=\"text-red-600\" />\n                <h4 className=\"font-bold text-slate-900\">Keyword Optimization</h4>\n              </div>\n              <div className=\"space-y-3\">\n                <div className=\"p-3 bg-red-50 rounded-lg\">\n                  <div className=\"text-sm text-slate-900 mb-2\">\n                    <span className=\"font-medium\">Usage:</span> {recommendations.keyword_optimization.primary_keyword_usage}\n                  </div>\n                  <div className=\"text-sm text-slate-900 mb-2\">\n                    <span className=\"font-medium\">LSI Keywords:</span> {recommendations.keyword_optimization.lsi_keywords?.join(', ')}\n                  </div>\n                  <div className=\"text-sm text-slate-900\">\n                    <span className=\"font-medium\">Improvements:</span>\n                    <ul className=\"list-disc list-inside mt-1\">\n                      {recommendations.keyword_optimization.placement_improvements?.map((imp, index) => (\n                        <li key={index}>{imp}</li>\n                      ))}\n                    </ul>\n                  </div>\n                </div>\n              </div>\n            </div>\n          )}\n\n          {/* Implementation Priority */}\n          {recommendations.implementation_priority?.length > 0 && (\n            <div className=\"bg-white rounded-xl p-6 border border-slate-200\">\n              <div className=\"flex items-center gap-2 mb-4\">\n                <Zap size={20} className=\"text-orange-600\" />\n                <h4 className=\"font-bold text-slate-900\">Implementation Priority</h4>\n              </div>\n              <div className=\"space-y-2\">\n                {recommendations.implementation_priority.map((item, index) => (\n                  <div key={index} className=\"flex items-center justify-between p-3 bg-slate-50 rounded-lg\">\n                    <div className=\"flex-1\">\n                      <div className=\"font-medium text-slate-900\">{item.item}</div>\n                      <div className=\"flex gap-2 mt-1\">\n                        <span className={`text-xs px-2 py-1 rounded-full ${\n                          item.impact === 'high' ? 'bg-red-100 text-red-700' :\n                          item.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :\n                          'bg-green-100 text-green-700'\n                        }`}>\n                          {item.impact} impact\n                        </span>\n                        <span className={`text-xs px-2 py-1 rounded-full ${\n                          item.effort === 'low' ? 'bg-green-100 text-green-700' :\n                          item.effort === 'medium' ? 'bg-yellow-100 text-yellow-700' :\n                          'bg-red-100 text-red-700'\n                        }`}>\n                          {item.effort} effort\n                        </span>\n                      </div>\n                    </div>\n                    <ArrowRight size={18} className=\"text-slate-400\" />\n                  </div>\n                ))}\n              </div>\n            </div>\n          )}\n\n          {/* Apply All Button */}\n          <div className=\"bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white\">\n            <div className=\"flex items-center justify-between\">\n              <div>\n                <h4 className=\"text-xl font-bold mb-2\">Ready to Optimize?</h4>\n                <p className=\"text-blue-100\">Apply all recommendations automatically to your content</p>\n              </div>\n              <button\n                onClick={applyRecommendations}\n                disabled={applying}\n                className=\"bg-white text-blue-600 px-6 py-3 rounded-lg font-bold hover:bg-blue-50 transition-all flex items-center gap-2 disabled:opacity-50\"\n              >\n                {applying ? (\n                  <>\n                    <Loader2 size={20} className=\"animate-spin\" />\n                    Applying...\n                  </>\n                ) : (\n                  <>\n                    <CheckCircle2 size={20} />\n                    Implement All\n                  </>\n                )}\n              </button>\n            </div>\n          </div>\n        </div>\n      )}\n    </div>\n  );\n};\n\nexport default ContentRecommendations;
