import { useNavigate } from 'react-router-dom';
import { Target, Users, Lightbulb, TrendingUp, Award, Globe, Heart, Zap } from 'lucide-react';
import MarketingNav from '@/components/MarketingNav';
import MarketingFooter from '@/components/MarketingFooter';
import { Helmet } from 'react-helmet';

const About = () => {
  const navigate = useNavigate();

  const values = [
    { icon: <Target size={32} />, title: 'Innovation First', description: 'We stay ahead of AI trends to provide cutting-edge GEO solutions.' },
    { icon: <Users size={32} />, title: 'Customer-Centric', description: 'Your success is our success. We build features that publishers actually need.' },
    { icon: <Lightbulb size={32} />, title: 'Data-Driven', description: 'Every recommendation is backed by real AI behavior analysis and data.' },
    { icon: <Heart size={32} />, title: 'Transparency', description: 'Clear pricing, honest metrics, and open communication always.' }
  ];

  const team = [
    { name: 'Sarah Mitchell', role: 'CEO & Co-Founder', bio: 'Former Head of SEO at TechCorp. 15+ years in digital marketing.' },
    { name: 'David Chen', role: 'CTO & Co-Founder', bio: 'Ex-Google AI researcher. PhD in Machine Learning from Stanford.' },
    { name: 'Maria Garcia', role: 'Head of Product', bio: 'Product leader with experience at Microsoft and Salesforce.' },
    { name: 'James Wilson', role: 'Head of Engineering', bio: 'Built scalable systems at Amazon Web Services for 10 years.' }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Helmet>
        <title>About CiteSight - Leading GEO Optimization Platform</title>
        <meta name="description" content="Learn about CiteSight's mission to help publishers optimize content for AI-generated summaries. Discover our story, values, and team." />
        <meta property="og:title" content="About CiteSight - GEO Optimization Experts" />
        <meta property="og:description" content="Pioneering the future of content visibility in AI search." />
      </Helmet>

      <MarketingNav />

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
            Building the Future of <span className="text-blue-600">Content Visibility</span>
          </h1>
          <p className="text-xl text-slate-600 leading-relaxed">
            We're on a mission to help publishers and content creators thrive in the AI-first era by providing the tools and insights needed to optimize for generative engine optimization.
          </p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-12 text-white">
              <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center mb-6">
                <Target size={32} />
              </div>
              <h2 className="text-3xl font-bold mb-4">Our Mission</h2>
              <p className="text-blue-100 text-lg leading-relaxed">
                To empower publishers and content creators with the insights and tools they need to maintain and grow their visibility in an AI-driven search landscape. We believe quality content deserves to be seen, regardless of how search evolves.
              </p>
            </div>

            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-12 text-white">
              <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center mb-6">
                <Globe size={32} />
              </div>
              <h2 className="text-3xl font-bold mb-4">Our Vision</h2>
              <p className="text-slate-300 text-lg leading-relaxed">
                A world where content creators can seamlessly adapt to AI-powered search, where quality and relevance drive visibility, and where the relationship between creators and AI systems is transparent and mutually beneficial.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Now */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">Why GEO Matters Now</h2>
            <p className="text-xl text-slate-600">The rise of AI search is transforming how content is discovered</p>
          </div>

          <div className="space-y-8">
            <div className="bg-white rounded-2xl p-8 border border-slate-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <TrendingUp size={24} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-3">AI Search is Exploding</h3>
                  <p className="text-slate-600 text-lg leading-relaxed">
                    Google's AI Overviews, ChatGPT Search, Perplexity, and Bing Copilot are fundamentally changing how people find information. Over 1 billion AI-generated answers are served daily, and traditional SEO strategies alone are no longer sufficient.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-8 border border-slate-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Zap size={24} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-3">Publishers Need New Tools</h3>
                  <p className="text-slate-600 text-lg leading-relaxed">
                    Traditional analytics can't track AI summary visibility. Publishers are losing traffic to AI-generated answers without understanding why or how to adapt. CiteSight fills this critical gap.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-8 border border-slate-200">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Award size={24} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 mb-3">GEO: The New SEO</h3>
                  <p className="text-slate-600 text-lg leading-relaxed">
                    Generative Engine Optimization (GEO) is emerging as the next evolution of SEO. Just as SEO transformed digital marketing 20 years ago, GEO will define content strategy for the next decade. We're pioneering this space.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Founding Story */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-8 text-center">Our Story</h2>
          <div className="prose prose-lg max-w-none">
            <p className="text-slate-600 text-lg leading-relaxed mb-6">
              CiteSight was born from a simple observation: publishers were losing visibility overnight as AI-generated summaries became mainstream, but they had no way to measure or respond to this shift.
            </p>
            <p className="text-slate-600 text-lg leading-relaxed mb-6">
              In early 2024, our founders—seasoned SEO experts and AI researchers—noticed that traffic patterns were changing dramatically. High-quality content was still being created, but AI systems were synthesizing it into summaries without attribution or visibility metrics.
            </p>
            <p className="text-slate-600 text-lg leading-relaxed mb-6">
              We realized that the same revolution that transformed search 20 years ago with Google was happening again with AI. But this time, content creators needed entirely new tools to understand and optimize for AI visibility.
            </p>
            <p className="text-slate-600 text-lg leading-relaxed">
              After months of research and development, CiteSight emerged as the first comprehensive GEO optimization platform—helping publishers not just survive, but thrive in the AI-first era.
            </p>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">Our Values</h2>
            <p className="text-xl text-slate-600">The principles that guide everything we do</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-slate-200 text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center mx-auto mb-6 text-white">
                  {value.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{value.title}</h3>
                <p className="text-slate-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">Meet Our Team</h2>
            <p className="text-xl text-slate-600">Industry experts passionate about the future of content</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-slate-200 text-center hover:border-blue-600 hover:shadow-xl transition-all">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full mx-auto mb-6 flex items-center justify-center text-white text-2xl font-bold">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{member.name}</h3>
                <p className="text-blue-600 font-semibold mb-3">{member.role}</p>
                <p className="text-slate-600 text-sm">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-gradient-to-br from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Join Us in Shaping the Future
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Be part of the GEO revolution and optimize your content for the AI era
          </p>
          <button
            onClick={() => navigate('/auth/register')}
            className="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-slate-50 transition-all"
          >
            Get Started Today
          </button>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
};

export default About;