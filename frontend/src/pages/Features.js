import { useNavigate } from 'react-router-dom';
import { TrendingUp, Target, Lightbulb, BarChart3, Bell, DollarSign, Radio, Award, Zap, CheckCircle } from 'lucide-react';
import MarketingNav from '@/components/MarketingNav';
import MarketingFooter from '@/components/MarketingFooter';
import { Helmet } from 'react-helmet';

const Features = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <TrendingUp size={40} />,
      title: 'AI Summary Visibility Tracker',
      description: 'Track where and when your content appears in AI-generated answers across all major platforms.',
      benefits: [
        'Real-time monitoring across Google AI Overview, Bing Copilot, Perplexity, and ChatGPT',
        'Visibility score (0-100) for each platform',
        'Position tracking in AI summaries',
        'Historical trend analysis',
        'Content snippet preview'
      ]
    },
    {
      icon: <Target size={40} />,
      title: 'Keyword Monitoring',
      description: 'Monitor specific keywords and track their performance across AI engines with detailed position tracking.',
      benefits: [
        'Track unlimited keywords across all platforms',
        'Average position metrics',
        'Keyword visibility trends over time',
        'Competitor keyword analysis',
        'Search intent mapping'
      ]
    },
    {
      icon: <Lightbulb size={40} />,
      title: 'GEO Optimization Recommendations',
      description: 'Get AI-powered, actionable recommendations to improve your content visibility in AI summaries.',
      benefits: [
        'Semantic chunking strategies',
        'Schema markup optimization',
        'FAQ injection recommendations',
        'Content structure improvements',
        'Keyword optimization suggestions',
        'Priority-based action items'
      ]
    },
    {
      icon: <Users size={40} />,
      title: 'Competitor Benchmarking',
      description: 'Compare your AI visibility against top competitors and identify content gaps.',
      benefits: [
        'Side-by-side visibility comparison',
        'GEO Health Score benchmarking',
        'Platform presence analysis',
        'Content strategy insights',
        'Competitive intelligence reports'
      ]
    },
    {
      icon: <BarChart3 size={40} />,
      title: 'Predictive GEO Scoring',
      description: 'Forecast future visibility and ROI impact with advanced predictive analytics.',
      benefits: [
        'ML-powered visibility predictions',
        'ROI impact forecasting',
        'Traffic trend projections',
        'Content performance predictions',
        'Optimization impact estimates'
      ]
    },
    {
      icon: <Bell size={40} />,
      title: 'Real-Time AI Summary Alerts',
      description: 'Get notified instantly when your content visibility changes across AI platforms.',
      benefits: [
        'Instant email and SMS notifications',
        'Visibility spike/drop alerts',
        'New platform detection',
        'Competitor activity alerts',
        'Custom alert thresholds'
      ]
    },
    {
      icon: <DollarSign size={40} />,
      title: 'Attribution & Micro-Payment API',
      description: 'Track and monetize usage of your content in AI-generated responses.',
      benefits: [
        'Content usage tracking',
        'Attribution analytics',
        'Micro-payment integration',
        'Revenue tracking dashboard',
        'API for custom integrations'
      ]
    },
    {
      icon: <Radio size={40} />,
      title: 'AI Content Syndication',
      description: 'Push optimized content directly to AI bots and voice assistants.',
      benefits: [
        'Direct content syndication to AI platforms',
        'Voice assistant optimization',
        'Chatbot integration',
        'Automated content distribution',
        'Performance tracking'
      ]
    },
    {
      icon: <Award size={40} />,
      title: 'GEO Health Score',
      description: 'Holistic score measuring your content strength across all AI search systems.',
      benefits: [
        'Comprehensive 0-100 health score',
        'Category-wise breakdowns',
        'Improvement recommendations',
        'Historical score tracking',
        'Industry benchmarking'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Helmet>
        <title>Features - CiteSight GEO Optimization Platform</title>
        <meta name="description" content="Explore CiteSight's comprehensive features: AI visibility tracking, keyword monitoring, GEO recommendations, predictive scoring, and more." />
        <meta property="og:title" content="CiteSight Features - Complete GEO Toolkit" />
        <meta property="og:description" content="Everything you need to optimize content for AI-generated summaries." />
      </Helmet>

      <MarketingNav />

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
            Powerful Features for <span className="text-blue-600">GEO Success</span>
          </h1>
          <p className="text-xl text-slate-600 leading-relaxed">
            Everything you need to track, analyze, and optimize your content visibility across AI-generated summaries
          </p>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto space-y-20">
          {features.map((feature, index) => (
            <div key={index} className={`flex flex-col ${index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'} gap-12 items-center`}>
              <div className="flex-1">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center text-white mb-6">
                  {feature.icon}
                </div>
                <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">{feature.title}</h2>
                <p className="text-xl text-slate-600 mb-6 leading-relaxed">{feature.description}</p>
                <ul className="space-y-3">
                  {feature.benefits.map((benefit, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle size={24} className="text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700 text-lg">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex-1">
                <div className="bg-gradient-to-br from-slate-100 to-blue-100 rounded-2xl p-12 aspect-video flex items-center justify-center">
                  <div className="text-slate-400 text-center">
                    <div className="w-32 h-32 bg-white/50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      {feature.icon}
                    </div>
                    <p className="text-sm">Feature Preview</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Integration */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">Platform Integrations</h2>
            <p className="text-xl text-slate-600">Track your content across all major AI platforms</p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {['Google AI Overview', 'Bing Copilot', 'Perplexity', 'ChatGPT'].map((platform, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-slate-200 text-center hover:border-blue-600 hover:shadow-xl transition-all">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Zap size={32} className="text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">{platform}</h3>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-gradient-to-br from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Start optimizing your content for AI visibility today
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={() => navigate('/auth/register')}
              className="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-slate-50 transition-all"
            >
              Start Free Trial
            </button>
            <button
              onClick={() => navigate('/pricing')}
              className="border-2 border-white text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/10 transition-all"
            >
              View Pricing
            </button>
          </div>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
};

export default Features;