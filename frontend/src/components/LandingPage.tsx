import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Search, BarChart3, ArrowRight } from 'lucide-react';
import { cn } from '../lib/utils';

interface LandingPageProps {
  onGetStarted: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-zinc-950 text-white overflow-x-hidden">
      {/* Background Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-brand-600/10 blur-[120px] rounded-full -z-10" />
      
      {/* Navbar */}
      <nav className="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <Zap size={18} className="text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">EnterpriseRAG</span>
        </div>
        <button 
          onClick={onGetStarted}
          className="px-5 py-2 rounded-full border border-zinc-800 hover:bg-zinc-900 transition-colors text-sm font-medium"
        >
          Sign In
        </button>
      </nav>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-32 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-8">
            Your Knowledge.<br />
            <span className="bg-gradient-to-r from-brand-400 via-purple-400 to-brand-500 bg-clip-text text-transparent">
              Unlocked.
            </span>
          </h1>
          <p className="text-zinc-400 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed">
            Production-grade RAG with role-based security, AI guardrails, and real-time monitoring. 
            The intelligent layer for your enterprise data.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button 
              onClick={onGetStarted}
              className="px-8 py-4 bg-brand-600 hover:bg-brand-500 text-white rounded-full font-bold text-lg transition-all hover:scale-105 flex items-center group shadow-xl shadow-brand-600/20"
            >
              Get Started 
              <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-32"
        >
          <FeatureCard 
            icon={<Shield className="text-brand-400" />}
            title="RBAC Security"
            description="Fine-grained access control ensuring users only see what they are authorized for."
          />
          <FeatureCard 
            icon={<Search className="text-purple-400" />}
            title="Hybrid Retrieval"
            description="Combining semantic and keyword search for unmatched accuracy and relevance."
          />
          <FeatureCard 
            icon={<Zap className="text-yellow-400" />}
            title="AI Guardrails"
            description="Integrated NeMo rails to prevent jailbreaks, toxicity, and off-topic conversations."
          />
          <FeatureCard 
            icon={<BarChart3 className="text-emerald-400" />}
            title="Observability"
            description="Real-time performance tracking with Prometheus, Grafana, and LangSmith."
          />
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-12 border-t border-zinc-900 text-center">
        <p className="text-zinc-600 text-sm">
          Powered by Llama 3.1 + Qdrant • Enterprise-Ready RAG
        </p>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
  <div className="p-8 rounded-3xl bg-zinc-900/40 border border-zinc-800 hover:border-zinc-700 transition-colors text-left group">
    <div className="w-12 h-12 rounded-2xl bg-zinc-950 border border-zinc-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
      {icon}
    </div>
    <h3 className="text-xl font-bold mb-3 text-white">{title}</h3>
    <p className="text-zinc-500 leading-relaxed text-sm">
      {description}
    </p>
  </div>
);
