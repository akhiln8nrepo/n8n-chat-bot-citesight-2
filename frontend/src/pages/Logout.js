import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Clear authentication data
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    
    // Show success message
    toast.success('You have been logged out successfully');
    
    // Redirect after 2 seconds
    const timer = setTimeout(() => {
      navigate('/home');
    }, 2000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={40} className="text-green-600" />
          </div>
          
          <h1 className="text-3xl font-bold text-slate-900 mb-4">
            Logged Out Successfully
          </h1>
          
          <p className="text-slate-600 mb-8">
            You have been securely logged out of your CiteSight account.
          </p>

          <div className="flex flex-col gap-3">
            <button
              onClick={() => navigate('/auth/login')}
              className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-3 rounded-xl font-bold hover:shadow-lg transition-all"
            >
              Sign In Again
            </button>
            
            <button
              onClick={() => navigate('/home')}
              className="text-slate-600 hover:text-slate-900 font-semibold"
            >
              Return to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Logout;
