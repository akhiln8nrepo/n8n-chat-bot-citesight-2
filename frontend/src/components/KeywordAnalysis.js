import { useState } from 'react';
import axios from '@/utils/axios';
import { Search, Lightbulb, TrendingUp, ExternalLink, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const KeywordAnalysis = ({ keyword, contentId, onAnalysisComplete }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const handleAnalyze = async () => {
    if (!keyword) {
      toast.error('Please enter a keyword');
      return;
    }

    setAnalyzing(true);
    try {
      const response = await axios.post('/keyword-analysis', {
        keyword: keyword,
        content_id: contentId
      });
      
      setAnalysis(response.data);
      toast.success('Keyword analysis complete!');
      
      if (onAnalysisComplete) {
        onAnalysisComplete(response.data);
      }
    } catch (error) {
      console.error('Error analyzing keyword:', error);
      toast.error('Failed to analyze keyword');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Analysis Trigger */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-slate-900 mb-2">Keyword Analysis</h3>
            <p className="text-sm text-slate-600">Discover LLM questions and search trends for: <span className="font-semibold text-blue-600">{keyword}</span></p>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="btn-primary flex items-center gap-2"
          >
            {analyzing ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search size={20} />
                Analyze Keyword
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* LLM Questions */}
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb size={24} className="text-yellow-500" />
              <h3 className="text-lg font-bold text-slate-900">Previously Asked LLM Questions</h3>
            </div>
            <div className="space-y-3">
              {analysis.llm_questions?.map((item, index) => (
                <div key={index} className="flex items-start gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 text-blue-600 font-semibold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-900 font-medium mb-2">{item.question}</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        item.search_volume === 'high' ? 'bg-red-100 text-red-700' :
                        item.search_volume === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {item.search_volume} volume
                      </span>
                      {item.difficulty !== undefined && (
                        <>
                          <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                            item.difficulty >= 70 ? 'bg-red-100 text-red-700' :
                            item.difficulty >= 40 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                          }`}>
                            {item.difficulty}% difficulty
                          </span>
                          <span className="text-xs text-slate-500">
                            ({item.competing_pages || 0} competing pages)
                          </span>
                        </>
                      )}
                    </div>
                    {item.difficulty_analysis && (
                      <p className="text-xs text-slate-600 mt-2">{item.difficulty_analysis}</p>
                    )}
                  </div>
                  <div className={`px-3 py-1 rounded-lg text-xs font-bold ${
                    item.difficulty >= 70 ? 'bg-red-100 text-red-700' :
                    item.difficulty >= 40 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {item.difficulty_level || 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Most Searched Queries */}
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={24} className="text-green-500" />
              <h3 className="text-lg font-bold text-slate-900">Most Searched Queries</h3>
            </div>
            <div className="space-y-3">
              {analysis.search_queries?.map((item, index) => (
                <div key={index} className="p-4 bg-gradient-to-r from-slate-50 to-white rounded-lg border border-slate-200">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <p className="text-slate-900 font-medium mb-1">{item.query}</p>
                      <p className="text-sm text-slate-600 line-clamp-2">{item.snippet}</p>
                    </div>
                    <a
                      href={item.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 flex-shrink-0"
                    >
                      <ExternalLink size={18} />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Coverage Analysis (if content provided) */}
          {analysis.coverage_analysis && (
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-900">Content Coverage Analysis</h3>
                <div className="text-3xl font-bold text-blue-600">
                  {analysis.coverage_analysis.coverage_score}%
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 size={18} className="text-green-600" />
                    <span className="font-medium text-slate-900">Answered Questions</span>
                  </div>
                  <div className="text-sm text-slate-600">
                    {analysis.coverage_analysis.answered_questions?.length || 0} out of {analysis.llm_questions?.length || 0} questions
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle size={18} className="text-orange-600" />
                    <span className="font-medium text-slate-900">Missing Questions</span>
                  </div>
                  <div className="text-sm text-slate-600">
                    {analysis.coverage_analysis.missing_questions?.length || 0} questions not addressed
                  </div>
                </div>

                <div>
                  <div className="font-medium text-slate-900 mb-2">Recommendations:</div>
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.coverage_analysis.recommendations?.map((rec, index) => (
                      <li key={index} className="text-sm text-slate-600">{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KeywordAnalysis;