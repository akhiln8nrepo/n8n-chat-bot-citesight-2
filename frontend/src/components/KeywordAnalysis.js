import { useState } from 'react';
import axios from '@/utils/axios';
import { Search, Lightbulb, TrendingUp, ExternalLink, AlertCircle, CheckCircle2, Loader2, Info, ShoppingCart, Navigation2, FileText } from 'lucide-react';
import { toast } from 'sonner';

// Simple Sparkline Component - Enhanced Size
const Sparkline = ({ data, color = '#3b82f6' }) => {
  if (!data || data.length === 0) return null;
  
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 100;
    return `${x},${y}`;
  }).join(' ');
  
  return (
    <svg width="140" height="40" className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="3"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
};

const KeywordAnalysis = ({ keyword, contentId, onAnalysisComplete }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [filterVolume, setFilterVolume] = useState('all');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [filterIntent, setFilterIntent] = useState('all');

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

  // Filter questions based on selected filters
  const getFilteredQuestions = () => {
    if (!analysis || !analysis.llm_questions) return [];
    
    let filtered = analysis.llm_questions;

    // Filter by volume
    if (filterVolume !== 'all') {
      filtered = filtered.filter(q => q.search_volume === filterVolume);
    }

    // Filter by difficulty
    if (filterDifficulty !== 'all') {
      filtered = filtered.filter(q => {
        const diff = q.difficulty || 0;
        if (filterDifficulty === 'low') return diff < 40;
        if (filterDifficulty === 'medium') return diff >= 40 && diff < 70;
        if (filterDifficulty === 'high') return diff >= 70;
        return true;
      });
    }

    // Filter by intent
    if (filterIntent !== 'all') {
      filtered = filtered.filter(q => q.intent === filterIntent);
    }

    return filtered;
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
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Lightbulb size={24} className="text-yellow-500" />
                <h3 className="text-lg font-bold text-slate-900">Previously Asked LLM Questions</h3>
                <span className="text-sm text-slate-500">({getFilteredQuestions().length} questions)</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-600">
                <Info size={14} />
                <span>Intent: I=Info, C=Commercial, T=Transaction, N=Navigation</span>
              </div>
            </div>

            {/* Filter Controls */}
            <div className="mb-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-slate-700">Volume:</label>
                  <select
                    value={filterVolume}
                    onChange={(e) => setFilterVolume(e.target.value)}
                    className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">All</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-slate-700">Difficulty:</label>
                  <select
                    value={filterDifficulty}
                    onChange={(e) => setFilterDifficulty(e.target.value)}
                    className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">All</option>
                    <option value="low">Low (&lt;40%)</option>
                    <option value="medium">Medium (40-69%)</option>
                    <option value="high">High (≥70%)</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-slate-700">Intent:</label>
                  <select
                    value={filterIntent}
                    onChange={(e) => setFilterIntent(e.target.value)}
                    className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all">All</option>
                    <option value="I">Informational</option>
                    <option value="C">Commercial</option>
                    <option value="T">Transactional</option>
                    <option value="N">Navigational</option>
                  </select>
                </div>

                {(filterVolume !== 'all' || filterDifficulty !== 'all' || filterIntent !== 'all') && (
                  <button
                    onClick={() => {
                      setFilterVolume('all');
                      setFilterDifficulty('all');
                      setFilterIntent('all');
                    }}
                    className="px-3 py-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-3">
              {getFilteredQuestions().map((item, index) => (
                <div key={index} className="flex items-start gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 text-blue-600 font-semibold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-900 font-medium mb-2">{item.question}</p>
                    
                    {/* First Row: Volume, Difficulty, Intent */}
                    <div className="flex items-center gap-2 flex-wrap mb-2">
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
                            ({item.competing_pages || 0} pages)
                          </span>
                        </>
                      )}
                      {item.intent && (
                        <span className={`text-xs px-2 py-1 rounded-full font-semibold flex items-center gap-1 ${
                          item.intent === 'T' ? 'bg-purple-100 text-purple-700' :
                          item.intent === 'C' ? 'bg-blue-100 text-blue-700' :
                          item.intent === 'N' ? 'bg-orange-100 text-orange-700' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {item.intent === 'T' && <ShoppingCart size={12} />}
                          {item.intent === 'C' && <Search size={12} />}
                          {item.intent === 'N' && <Navigation2 size={12} />}
                          {item.intent === 'I' && <FileText size={12} />}
                          {item.intent === 'T' ? 'Transactional' :
                           item.intent === 'C' ? 'Commercial' :
                           item.intent === 'N' ? 'Navigational' :
                           'Informational'}
                        </span>
                      )}
                    </div>
                    
                    {/* Second Row: Trend and Analysis */}
                    <div className="flex items-center gap-3">
                      {item.trend_data && item.trend_data.length > 0 && (
                        <div className="flex items-center gap-2 bg-white px-2 py-1 rounded border border-slate-200">
                          <TrendingUp size={14} className="text-blue-600" />
                          <Sparkline 
                            data={item.trend_data} 
                            color={item.search_volume === 'high' ? '#dc2626' : item.search_volume === 'medium' ? '#f59e0b' : '#16a34a'}
                          />
                          <span className="text-xs text-slate-500">12mo trend</span>
                        </div>
                      )}
                      {item.difficulty_analysis && (
                        <p className="text-xs text-slate-600">{item.difficulty_analysis}</p>
                      )}
                    </div>
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