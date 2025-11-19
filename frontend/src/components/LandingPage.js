import { useNavigate } from 'react-router-dom';
import { TrendingUp, Search, Target, BarChart3, Zap, Shield } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Search size={28} />,
      title: 'AI Summary Visibility Tracker',
      description: 'Monitor your content presence across Google AI Overview, Bing Copilot, Perplexity, and ChatGPT in real-time.'
    },
    {
      icon: <Target size={28} />,
      title: 'Keyword Monitoring',
      description: 'Track specific keywords and their performance across all major AI platforms with detailed position tracking.'
    },
    {
      icon: <TrendingUp size={28} />,
      title: 'GEO Recommendations',
      description: 'Get AI-powered actionable recommendations for semantic chunking, schema markup, and FAQ injection.'
    },
    {
      icon: <BarChart3 size={28} />,
      title: 'Visibility Score Dashboard',
      description: 'Comprehensive analytics dashboard with visibility scores, trend analysis, and performance metrics.'
    },
    {
      icon: <Zap size={28} />,
      title: 'Real-Time Alerts',
      description: 'Receive instant notifications when your content visibility changes across AI platforms.'
    },
    {
      icon: <Shield size={28} />,
      title: 'Competitive Intelligence',
      description: 'Benchmark your performance against competitors with GEO Health Score analysis.'
    }
  ];

  return (
    <div className="landing-hero">
      {/* Navigation */}
      <nav className="relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-lg flex items-center justify-center">
              <TrendingUp size={24} className="text-white" />
            </div>
            <span className="text-2xl font-bold text-slate-900">GEO Monitor</span>
          </div>
          <button
            data-testid="get-started-nav-btn"
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 leading-tight mb-6">
              Master Your AI Visibility
            </h1>
            <p className="text-base sm:text-lg text-slate-600 mb-8 leading-relaxed">
              Monitor your content presence in AI-generated summaries across major platforms.
              Get actionable GEO recommendations to improve visibility and drive traffic.
            </p>
            <div className="flex flex-wrap gap-4">
              <button
                data-testid="start-monitoring-btn"
                onClick={() => navigate('/dashboard')}
                className="btn-primary"
              >
                Start Monitoring
              </button>
              <button
                data-testid="learn-more-btn"
                onClick={() => window.scrollTo({ top: window.innerHeight, behavior: 'smooth' })}
                className="btn-secondary"
              >
                Learn More
              </button>
            </div>
          </div>
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1551288049-bebda4e38f71"
              alt="Analytics Dashboard"
              className="rounded-2xl shadow-2xl w-full"
            />
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 bg-white py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Comprehensive AI Visibility Platform
            </h2>
            <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto">
              Everything you need to optimize your content for AI-generated summaries and improve your digital presence.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="feature-card" data-testid={`feature-card-${index}`}>
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Platforms Section */}
      <div className="relative z-10 py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
              Track Across All Major AI Platforms
            </h2>
            <p className="text-base sm:text-lg text-slate-600">
              Comprehensive monitoring of your content visibility
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {['Google AI Overview', 'Bing Copilot', 'Perplexity', 'ChatGPT'].map((platform, index) => (
              <div key={index} className="bg-white rounded-xl p-6 text-center border border-slate-200 hover:border-sky-500 transition-colors" data-testid={`platform-card-${index}`}>
                <div className="w-12 h-12 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <Search size={24} className="text-white" />
                </div>
                <h3 className="font-bold text-slate-900">{platform}</h3>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 bg-gradient-to-r from-sky-500 to-cyan-500 py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Optimize Your AI Visibility?
          </h2>
          <p className="text-lg text-sky-50 mb-8">
            Join publishers and content marketers who are staying ahead in the AI-first era.
          </p>
          <button
            data-testid="cta-get-started-btn"
            onClick={() => navigate('/dashboard')}
            className="bg-white text-sky-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-slate-50 transition-colors shadow-lg"
          >
            Get Started Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;