import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, X, HelpCircle } from 'lucide-react';
import MarketingNav from '@/components/MarketingNav';
import MarketingFooter from '@/components/MarketingFooter';
import { Helmet } from 'react-helmet';

const Pricing = () => {
  const navigate = useNavigate();
  const [billingCycle, setBillingCycle] = useState('monthly'); // 'monthly' or 'annual'

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for small publishers and bloggers',
      monthlyPrice: 99,
      annualPrice: 990,
      features: [
        { name: 'Up to 50 pages tracked', included: true },
        { name: 'Basic GEO recommendations', included: true },
        { name: '4 AI platforms monitored', included: true },
        { name: 'Email support', included: true },
        { name: 'Weekly reports', included: true },
        { name: 'Advanced analytics', included: false },
        { name: 'Competitor analysis', included: false },
        { name: 'API access', included: false }
      ]
    },
    {
      name: 'Pro',
      description: 'For growing content teams and agencies',
      monthlyPrice: 299,
      annualPrice: 2990,
      popular: true,
      features: [
        { name: 'Up to 500 pages tracked', included: true },
        { name: 'Advanced GEO recommendations', included: true },
        { name: '4 AI platforms monitored', included: true },
        { name: 'Priority email & chat support', included: true },
        { name: 'Daily reports', included: true },
        { name: 'Advanced analytics & insights', included: true },
        { name: 'Competitor analysis (5 competitors)', included: true },
        { name: 'Real-time alerts', included: true },
        { name: 'API access', included: false },
        { name: 'White-label reports', included: false }
      ]
    },
    {
      name: 'Enterprise',
      description: 'For large organizations with custom needs',
      monthlyPrice: null,
      annualPrice: null,
      custom: true,
      features: [
        { name: 'Unlimited pages tracked', included: true },
        { name: 'Custom AI models & integrations', included: true },
        { name: 'All AI platforms + custom sources', included: true },
        { name: 'Dedicated account manager', included: true },
        { name: 'Real-time reports & custom dashboards', included: true },
        { name: 'Enterprise analytics suite', included: true },
        { name: 'Unlimited competitor tracking', included: true },
        { name: 'Advanced real-time alerts', included: true },
        { name: 'Full API access', included: true },
        { name: 'White-label & custom branding', included: true },
        { name: 'SLA & uptime guarantees', included: true },
        { name: 'On-premise deployment option', included: true }
      ]
    }
  ];

  const faqs = [
    {
      question: 'Can I change plans later?',
      answer: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect at the start of your next billing cycle.'
    },
    {
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and wire transfers for Enterprise customers.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes! All plans come with a 14-day free trial. No credit card required to start.'
    },
    {
      question: 'What happens if I exceed my page limit?',
      answer: 'We\'ll notify you when you approach your limit. You can either upgrade your plan or purchase additional page credits.'
    },
    {
      question: 'Do you offer discounts for non-profits?',
      answer: 'Yes! We offer 30% discounts for registered non-profit organizations and educational institutions. Contact our sales team for details.'
    },
    {
      question: 'Can I cancel anytime?',
      answer: 'Absolutely. There are no long-term contracts. You can cancel your subscription at any time from your account dashboard.'
    }
  ];

  const getPrice = (plan) => {
    if (plan.custom) return 'Custom';
    const price = billingCycle === 'monthly' ? plan.monthlyPrice : plan.annualPrice;
    return `$${price}`;
  };

  const getSavings = (plan) => {
    if (plan.custom || billingCycle === 'monthly') return null;
    const monthlyCost = plan.monthlyPrice * 12;
    const savings = monthlyCost - plan.annualPrice;
    return savings;
  };

  return (
    <div className="min-h-screen bg-white">
      <Helmet>
        <title>Pricing - CiteSight GEO Optimization Platform</title>
        <meta name="description" content="Choose the perfect CiteSight plan for your needs. Transparent pricing with 14-day free trial. Starter, Pro, and Enterprise options available." />
        <meta property="og:title" content="CiteSight Pricing - Simple & Transparent" />
        <meta property="og:description" content="Start optimizing your content for AI with flexible pricing plans." />
      </Helmet>

      <MarketingNav />

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
            Simple, <span className="text-blue-600">Transparent</span> Pricing
          </h1>
          <p className="text-xl text-slate-600 mb-8">
            Choose the plan that fits your needs. All plans include 14-day free trial.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center gap-4 bg-white rounded-full p-2 shadow-lg">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                billingCycle === 'annual'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Annual
              <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`rounded-2xl p-8 border-2 relative ${
                  plan.popular
                    ? 'border-blue-600 shadow-2xl scale-105'
                    : 'border-slate-200'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}

                <h3 className="text-2xl font-bold text-slate-900 mb-2">{plan.name}</h3>
                <p className="text-slate-600 mb-6">{plan.description}</p>

                <div className="mb-6">
                  <span className="text-5xl font-bold text-slate-900">{getPrice(plan)}</span>
                  {!plan.custom && (
                    <span className="text-slate-600 ml-2">/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>
                  )}
                  {getSavings(plan) && (
                    <div className="text-sm text-green-600 font-semibold mt-2">
                      Save ${getSavings(plan)} per year
                    </div>
                  )}
                </div>

                <button
                  onClick={() => plan.custom ? navigate('/contact') : navigate('/auth/register')}
                  className={`w-full py-3 rounded-xl font-bold mb-8 transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-xl'
                      : 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  {plan.custom ? 'Contact Sales' : 'Start Free Trial'}
                </button>

                <ul className="space-y-3">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      {feature.included ? (
                        <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X size={20} className="text-slate-300 flex-shrink-0 mt-0.5" />
                      )}
                      <span className={feature.included ? 'text-slate-700' : 'text-slate-400'}>
                        {feature.name}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">Frequently Asked Questions</h2>
            <p className="text-xl text-slate-600">Everything you need to know about our pricing</p>
          </div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-slate-200">
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <HelpCircle size={20} className="text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">{faq.question}</h3>
                    <p className="text-slate-600 leading-relaxed">{faq.answer}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-slate-600 mb-4">Still have questions?</p>
            <button
              onClick={() => navigate('/contact')}
              className="text-blue-600 font-semibold hover:text-blue-700"
            >
              Contact our sales team →
            </button>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-gradient-to-br from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Start Your Free Trial Today
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            No credit card required. Get full access to all features for 14 days.
          </p>
          <button
            onClick={() => navigate('/auth/register')}
            className="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-slate-50 transition-all"
          >
            Get Started Free
          </button>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
};

export default Pricing;