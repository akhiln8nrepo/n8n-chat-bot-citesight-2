import { useNavigate } from 'react-router-dom';
import { TrendingUp, Twitter, Linkedin, Github, Mail } from 'lucide-react';

const MarketingFooter = () => {
  const navigate = useNavigate();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-white py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center">
                <TrendingUp size={24} className="text-white" />
              </div>
              <span className="text-2xl font-bold">CiteSight</span>
            </div>
            <p className="text-slate-400 text-sm mb-4">Optimize your content for the AI era. Track, analyze, and improve your visibility in AI-generated summaries.</p>
            <div className="flex gap-4">
              <button className="text-slate-400 hover:text-white transition-colors"><Twitter size={20} /></button>
              <button className="text-slate-400 hover:text-white transition-colors"><Linkedin size={20} /></button>
              <button className="text-slate-400 hover:text-white transition-colors"><Github size={20} /></button>
              <button className="text-slate-400 hover:text-white transition-colors"><Mail size={20} /></button>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-bold text-lg mb-4">Product</h4>
            <ul className="space-y-2 text-slate-400">
              <li><button onClick={() => navigate('/features')} className="hover:text-white transition-colors">Features</button></li>
              <li><button onClick={() => navigate('/pricing')} className="hover:text-white transition-colors">Pricing</button></li>
              <li><button onClick={() => navigate('/product-tour')} className="hover:text-white transition-colors">Product Tour</button></li>
              <li><button onClick={() => navigate('/auth/register')} className="hover:text-white transition-colors">Get Started</button></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-bold text-lg mb-4">Company</h4>
            <ul className="space-y-2 text-slate-400">
              <li><button onClick={() => navigate('/about')} className="hover:text-white transition-colors">About Us</button></li>
              <li><button onClick={() => navigate('/blog')} className="hover:text-white transition-colors">Blog</button></li>
              <li><button onClick={() => navigate('/contact')} className="hover:text-white transition-colors">Contact</button></li>
              <li><button onClick={() => navigate('/faq')} className="hover:text-white transition-colors">FAQ</button></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-bold text-lg mb-4">Legal</h4>
            <ul className="space-y-2 text-slate-400">
              <li><button onClick={() => navigate('/legal/privacy')} className="hover:text-white transition-colors">Privacy Policy</button></li>
              <li><button onClick={() => navigate('/legal/terms')} className="hover:text-white transition-colors">Terms of Service</button></li>
              <li><button onClick={() => navigate('/legal/cookie')} className="hover:text-white transition-colors">Cookie Policy</button></li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-400 text-sm">&copy; {currentYear} CiteSight. All rights reserved.</p>
          <p className="text-slate-400 text-sm">Built for the AI-first era</p>
        </div>
      </div>
    </footer>
  );
};

export default MarketingFooter;