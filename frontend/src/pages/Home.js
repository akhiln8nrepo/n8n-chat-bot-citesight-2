import { useNavigate } from 'react-router-dom';
import { TrendingUp, Target, BarChart3, Zap, Shield, Award, CheckCircle, Star, ArrowRight } from 'lucide-react';
import MarketingNav from '@/components/MarketingNav';
import MarketingFooter from '@/components/MarketingFooter';
import { Helmet } from 'react-helmet';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <TrendingUp size={32} />,
      title: 'AI Summary Visibility Tracker',
      description: 'Monitor your content presence across Google AI Overview, Bing Copilot, Perplexity, and ChatGPT in real-time.'
    },
    {
      icon: <Target size={32} />,
      title: 'Keyword Monitoring',
      description: 'Track specific keywords and their performance across all major AI platforms with detailed position tracking.'
    },
    {
      icon: <BarChart3 size={32} />,
      title: 'GEO Recommendations',
      description: 'Get AI-powered actionable recommendations for semantic chunking, schema markup, and FAQ injection.'
    },
    {
      icon: <Zap size={32} />,
      title: 'Real-Time Alerts',
      description: 'Receive instant notifications when your content visibility changes across AI platforms.'
    },
    {
      icon: <Shield size={32} />,
      title: 'Competitive Intelligence',
      description: 'Benchmark your performance against competitors with GEO Health Score analysis.'
    },
    {
      icon: <Award size={32} />,
      title: 'Predictive GEO Scoring',
      description: 'Forecast future visibility and ROI impact with advanced predictive analytics.'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Head of Content, TechFlow Media',
      content: 'CiteSight helped us increase our AI visibility by 340% in just 3 months. The GEO recommendations are game-changing.',
      rating: 5
    },
    {
      name: 'Michael Rodriguez',
      role: 'SEO Director, Digital Ventures',
      content: 'Finally, a tool that bridges the gap between traditional SEO and the AI-first future. The predictive scoring is incredibly accurate.',
      rating: 5
    },
    {
      name: 'Emily Watson',
      role: 'Publisher, ContentHub',
      content: 'The competitive intelligence features give us a clear edge. We can now see exactly how our content performs vs competitors in AI summaries.',
      rating: 5
    }
  ];

  const pricingPreview = [
    {
      name: 'Starter',
      price: '$99',
      description: 'Perfect for small publishers',
      features: ['Up to 50 pages tracked', 'Basic GEO recommendations', 'Email support']
    },
    {
      name: 'Pro',
      price: '$299',
      description: 'For growing content teams',
      features: ['Up to 500 pages tracked', 'Advanced GEO recommendations', 'Priority support', 'Competitive analysis'],
      featured: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      description: 'For large organizations',
      features: ['Unlimited pages', 'Custom AI models', 'Dedicated support', 'API access', 'White-label options']
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Helmet>
        <title>CiteSight - Optimize Your Content for the AI Era</title>
        <meta name="description" content="Monitor and optimize your content visibility across AI-generated summaries. Track performance on Google AI Overview, ChatGPT, Perplexity & more." />
        <meta property="og:title" content="CiteSight - GEO Optimization Platform" />
        <meta property="og:description" content="Optimize your content for the AI era. Track, analyze, and improve your visibility in AI-generated summaries." />
      </Helmet>

      <MarketingNav />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 bg-gradient-to-br from-slate-50 to-blue-50 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-blue-100/30 to-transparent"></div>
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-block bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold mb-6">
                🚀 Welcome to the AI-First Era
              </div>
              <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight">
                Optimize Your Content for the <span className="text-blue-600">AI Era</span>
              </h1>
              <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                Track, analyze, and improve your content visibility across AI-generated summaries. 
                Master GEO (Generative Engine Optimization) and stay ahead in AI search.
              </p>
              <div className="flex flex-wrap gap-4 mb-8">
                <button
                  onClick={() => navigate('/auth/register')}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-xl font-bold text-lg hover:shadow-2xl transition-all flex items-center gap-2"
                >
                  Get Started <ArrowRight size={20} />
                </button>
                <button
                  onClick={() => navigate('/contact')}
                  className="border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-blue-50 transition-all"
                >
                  Request Demo
                </button>
              </div>
              <div className="flex items-center gap-8 text-sm text-slate-600">
                <div className="flex items-center gap-2">
                  <CheckCircle size={20} className="text-green-600" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={20} className="text-green-600" />
                  <span>14-day free trial</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-6 border border-slate-200">
                <img 
                  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800" 
                  alt="CiteSight Dashboard" 
                  className="rounded-xl w-full"
                />
              </div>
              <div className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-xl p-4 border border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <TrendingUp size={24} className="text-green-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-slate-900">+340%</div>
                    <div className="text-sm text-slate-600">AI Visibility</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Overview */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Comprehensive GEO Optimization Platform
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Everything you need to track, analyze, and optimize your content for AI-generated summaries
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-slate-200 hover:border-blue-600 hover:shadow-xl transition-all group">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center mb-6 text-white group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <button
              onClick={() => navigate('/features')}
              className="text-blue-600 font-semibold text-lg hover:text-blue-700 flex items-center gap-2 mx-auto"
            >
              Explore All Features <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Trusted by Leading Publishers
            </h2>
            <p className="text-xl text-slate-600">
              See how CiteSight is helping content teams optimize for AI visibility
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} size={20} className="text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-slate-700 mb-6 leading-relaxed">"{testimonial.content}"</p>
                <div>
                  <div className="font-bold text-slate-900">{testimonial.name}</div>
                  <div className="text-sm text-slate-600">{testimonial.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-slate-600">
              Choose the plan that fits your needs. All plans include 14-day free trial.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {pricingPreview.map((plan, index) => (
              <div key={index} className={`rounded-2xl p-8 border-2 ${plan.featured ? 'border-blue-600 shadow-2xl scale-105' : 'border-slate-200'}`}>
                {plan.featured && (
                  <div className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold mb-4 inline-block">
                    Most Popular
                  </div>
                )}
                <h3 className="text-2xl font-bold text-slate-900 mb-2">{plan.name}</h3>
                <p className="text-slate-600 mb-6">{plan.description}</p>
                <div className="mb-6">
                  <span className="text-5xl font-bold text-slate-900">{plan.price}</span>
                  {plan.price !== 'Custom' && <span className="text-slate-600">/month</span>}
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => navigate('/auth/register')}
                  className={`w-full py-3 rounded-xl font-bold transition-all ${
                    plan.featured 
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-xl' 
                      : 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  Get Started
                </button>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <button
              onClick={() => navigate('/pricing')}
              className="text-blue-600 font-semibold text-lg hover:text-blue-700 flex items-center gap-2 mx-auto"
            >
              View Full Pricing Details <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-6 bg-gradient-to-br from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Optimize for the AI Era?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of publishers who are staying ahead with CiteSight
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={() => navigate('/auth/register')}
              className="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-slate-50 transition-all flex items-center gap-2"
            >
              Start Free Trial <ArrowRight size={20} />
            </button>
            <button
              onClick={() => navigate('/contact')}
              className="border-2 border-white text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/10 transition-all"
            >
              Talk to Sales
            </button>
          </div>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
};

export default Home;
