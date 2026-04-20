import React, { useState } from 'react';
import { apiService } from '../api/services';
import { Lock, User, Shield, Briefcase, TrendingUp, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';

const DEMO_ROLES = [
  { id: 'admin', name: 'Admin', role: 'Security & Ops', icon: <Shield size={20} />, color: 'text-brand-400', bg: 'bg-brand-500/10' },
  { id: 'mark', name: 'Mark', role: 'Marketing Strategy', icon: <TrendingUp size={20} />, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { id: 'fin', name: 'Fin', role: 'Financial Analysis', icon: <Briefcase size={20} />, color: 'text-emerald-400', bg: 'bg-emerald-500/10' }
];

interface LoginProps {
  onLoginSuccess: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const data = await apiService.login(username, password);
      localStorage.setItem('access_token', data.access_token);
      onLoginSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSelect = (roleId: string) => {
    setUsername(roleId);
    setPassword(`${roleId}123`);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-600/10 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[120px] rounded-full" />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10"
      >
        {/* Left Side: Brand & Roles */}
        <div className="space-y-10">
          <div>
            <motion.div 
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              className="flex items-center space-x-3 mb-6"
            >
              <div className="w-12 h-12 bg-brand-600 rounded-2xl flex items-center justify-center shadow-lg shadow-brand-500/20">
                <Zap size={24} className="text-white" />
              </div>
              <h1 className="text-3xl font-bold tracking-tight">EnterpriseRAG</h1>
            </motion.div>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Access your <br />
              <span className="text-zinc-500 italic">Secure Knowledge.</span>
            </h2>
            <p className="text-zinc-400 text-lg">Select a demo persona or use your credentials.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-4">
            {DEMO_ROLES.map((role) => (
              <motion.button
                key={role.id}
                whileHover={{ x: 10, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleQuickSelect(role.id)}
                className={cn(
                  "flex items-center p-4 rounded-2xl border transition-all text-left group",
                  username === role.id 
                    ? "bg-zinc-900 border-brand-500 shadow-lg shadow-brand-500/10" 
                    : "bg-zinc-900/40 border-zinc-800 hover:border-zinc-700"
                )}
              >
                <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center mr-4 shrink-0 transition-colors", role.bg, role.color)}>
                  {role.icon}
                </div>
                <div>
                  <h3 className="font-bold text-white group-hover:text-brand-400 transition-colors">{role.name}</h3>
                  <p className="text-xs text-zinc-500 font-medium uppercase tracking-wider">{role.role}</p>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Right Side: Login Form */}
        <div className="bg-zinc-900/50 backdrop-blur-3xl border border-zinc-800 p-8 md:p-12 rounded-[32px] shadow-2xl relative">
          <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
            <Lock size={120} />
          </div>

          <div className="relative">
            <h3 className="text-2xl font-bold mb-8">Sign In</h3>

            <AnimatePresence mode="wait">
              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-4 rounded-xl mb-8 flex items-start space-x-3"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0" />
                  <p>{error}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-zinc-400 ml-1">Username</label>
                <div className="group relative">
                  <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-brand-500 transition-colors" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all outline-none"
                    placeholder="e.g. admin"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-zinc-400 ml-1">Password</label>
                <div className="group relative">
                  <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-brand-500 transition-colors" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all outline-none"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-brand-600/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed mt-4"
              >
                {loading ? (
                  <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto" />
                ) : (
                  'Continue to Dashboard'
                )}
              </button>
            </form>

            <div className="mt-10 pt-8 border-t border-zinc-800 flex justify-between items-center text-xs text-zinc-500 font-medium">
              <span>Secure Authentication</span>
              <span className="flex items-center space-x-1">
                <Shield size={12} className="text-brand-500" />
                <span>AES-256 Encryption</span>
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
