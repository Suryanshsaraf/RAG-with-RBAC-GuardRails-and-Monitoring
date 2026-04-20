import { useState, useEffect } from 'react';
import { Login } from './components/Login';
import { Sidebar } from './components/Sidebar';
import { Chat } from './components/Chat';
import { LandingPage } from './components/LandingPage';
import { jwtDecode } from 'jwt-decode';
import { cn } from './lib/utils';

interface DecodedToken {
  sub: string;
  role: string;
  exp: number;
}

export interface UserInfo {
  username: string;
  role: string;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLanding, setShowLanding] = useState(true);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'guardrails' | 'settings'>('chat');
  const [ragSettings, setRagSettings] = useState({
    topK: 5,
    useHyde: false,
    multiQuery: false
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded = jwtDecode<DecodedToken>(token);
        setUser({ username: decoded.sub, role: decoded.role });
        setIsAuthenticated(true);
      } catch (err) {
        localStorage.removeItem('access_token');
      }
    }
  }, []);

  const handleLoginSuccess = () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const decoded = jwtDecode<DecodedToken>(token);
      setUser({ username: decoded.sub, role: decoded.role });
      setIsAuthenticated(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    if (showLanding) {
      return <LandingPage onGetStarted={() => setShowLanding(false)} />;
    }
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex">
      <Sidebar 
        user={user}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={handleLogout} 
        isMobileOpen={isMobileSidebarOpen}
        setIsMobileOpen={setIsMobileSidebarOpen}
      />
      
      <main className="flex-1 md:ml-72 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-zinc-800/50 bg-zinc-950/50 backdrop-blur-md px-6 flex items-center justify-between z-20">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => setIsMobileSidebarOpen(true)}
              className="md:hidden p-2 hover:bg-zinc-800 rounded-lg transition-colors"
            >
              <Menu size={20} />
            </button>
            <h1 className="text-sm font-bold uppercase tracking-widest text-zinc-500">
              {activeTab}
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            {user && (
              <div className="flex items-center space-x-3 bg-zinc-900/50 border border-zinc-800 py-1.5 pl-1.5 pr-3 rounded-full">
                <div className={cn(
                  "w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold shadow-lg",
                  user.role === 'admin' ? "bg-brand-500 shadow-brand-500/20" : 
                  user.role === 'Marketing' ? "bg-purple-500 shadow-purple-500/20" : 
                  "bg-emerald-500 shadow-emerald-500/20"
                )}>
                  {user.role[0]}
                </div>
                <span className="text-xs font-bold tracking-tight text-zinc-300">{user.role} Context</span>
                <div className={cn(
                  "w-1.5 h-1.5 rounded-full animate-pulse",
                  user.role === 'admin' ? "bg-brand-500" : 
                  user.role === 'Marketing' ? "bg-purple-500" : 
                  "bg-emerald-500"
                )} />
              </div>
            )}
          </div>
        </header>
        
        <div className="flex-1 overflow-hidden relative">
          {activeTab === 'chat' && <Chat settings={ragSettings} />}
          {activeTab === 'documents' && (
            <div className="p-8 max-w-5xl mx-auto space-y-10">
              <div className="flex justify-between items-end">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Knowledge Base</h2>
                  <p className="text-zinc-500">Manage and index your enterprise documents.</p>
                </div>
                <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-widest text-brand-500 bg-brand-500/10 px-3 py-1 rounded-full">
                  <div className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
                  <span>System Online</span>
                </div>
              </div>

              {/* Upload Zone */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                  <div className="aspect-[21/9] border-2 border-dashed border-zinc-800 rounded-[32px] flex flex-col items-center justify-center bg-zinc-900/20 hover:bg-zinc-900/40 hover:border-brand-500/50 transition-all cursor-pointer group">
                    <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <UploadCloud size={32} className="text-zinc-500 group-hover:text-brand-500" />
                    </div>
                    <p className="font-bold text-zinc-300">Drop files here to index</p>
                    <p className="text-xs text-zinc-500 mt-1 uppercase tracking-widest">PDF, CSV, Markdown up to 50MB</p>
                  </div>

                  {/* Document Table Mockup */}
                  <div className="bg-zinc-900/50 border border-zinc-800 rounded-[32px] overflow-hidden">
                    <div className="p-6 border-b border-zinc-800 bg-zinc-900/50 flex justify-between items-center">
                      <h3 className="font-bold">Indexed Documents</h3>
                      <button className="text-xs font-bold text-brand-500 uppercase tracking-widest hover:text-brand-400">View All</button>
                    </div>
                    <div className="p-6">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 border-b border-zinc-800">
                            <th className="pb-4">Document</th>
                            <th className="pb-4">Status</th>
                            <th className="pb-4">Access Level</th>
                            <th className="pb-4 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="text-sm">
                          <tr className="border-b border-zinc-800/50 group">
                            <td className="py-4">
                              <div className="flex items-center space-x-3">
                                <FileText size={16} className="text-brand-500" />
                                <span className="font-medium">q1_financials.pdf</span>
                              </div>
                            </td>
                            <td className="py-4">
                              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider">Indexed</span>
                            </td>
                            <td className="py-4">
                              <div className="flex -space-x-2">
                                <div className="w-6 h-6 rounded-full bg-brand-500 border-2 border-zinc-900 flex items-center justify-center text-[8px] font-bold" title="Admin">A</div>
                                <div className="w-6 h-6 rounded-full bg-emerald-500 border-2 border-zinc-900 flex items-center justify-center text-[8px] font-bold" title="Finance">F</div>
                              </div>
                            </td>
                            <td className="py-4 text-right">
                              <button className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-white transition-colors">
                                <BarChart3 size={16} />
                              </button>
                            </td>
                          </tr>
                          <tr className="group">
                            <td className="py-4">
                              <div className="flex items-center space-x-3">
                                <FileText size={16} className="text-brand-500" />
                                <span className="font-medium">marketing_strategy_2024.md</span>
                              </div>
                            </td>
                            <td className="py-4">
                              <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded uppercase tracking-wider">Indexed</span>
                            </td>
                            <td className="py-4">
                              <div className="flex -space-x-2">
                                <div className="w-6 h-6 rounded-full bg-brand-500 border-2 border-zinc-900 flex items-center justify-center text-[8px] font-bold" title="Admin">A</div>
                                <div className="w-6 h-6 rounded-full bg-purple-500 border-2 border-zinc-900 flex items-center justify-center text-[8px] font-bold" title="Marketing">M</div>
                              </div>
                            </td>
                            <td className="py-4 text-right">
                              <button className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-500 hover:text-white transition-colors">
                                <BarChart3 size={16} />
                              </button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* Sidebar Stats */}
                <div className="space-y-6">
                  <div className="bg-gradient-to-br from-brand-600 to-purple-600 rounded-[32px] p-8 shadow-xl shadow-brand-500/10">
                    <h4 className="text-white/70 text-xs font-bold uppercase tracking-widest mb-1">Vector Storage</h4>
                    <div className="text-3xl font-bold text-white mb-4">2,482 <span className="text-lg font-medium opacity-60">Chunks</span></div>
                    <div className="w-full bg-white/20 h-2 rounded-full mb-2">
                      <div className="bg-white w-[65%] h-full rounded-full" />
                    </div>
                    <p className="text-[10px] text-white/60 font-bold uppercase">65% of Qdrant Capacity Used</p>
                  </div>

                  <div className="bg-zinc-900/50 border border-zinc-800 rounded-[32px] p-8 space-y-6">
                    <h4 className="text-zinc-500 text-xs font-bold uppercase tracking-widest">Ingestion Pipeline</h4>
                    <div className="space-y-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                          <div className="w-2 h-2 rounded-full bg-emerald-500" />
                        </div>
                        <div className="text-xs font-bold uppercase tracking-wider text-zinc-400">Parsing Engine</div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                          <div className="w-2 h-2 rounded-full bg-emerald-500" />
                        </div>
                        <div className="text-xs font-bold uppercase tracking-wider text-zinc-400">Embedding (all-MiniLM)</div>
                      </div>
                      <div className="flex items-center space-x-4 opacity-50">
                        <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center">
                          <div className="w-2 h-2 rounded-full bg-zinc-500" />
                        </div>
                        <div className="text-xs font-bold uppercase tracking-wider text-zinc-500">Metadata Tagging</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'guardrails' && (
            <div className="p-8 max-w-6xl mx-auto space-y-8">
              <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold">Observability & Security</h2>
                <div className="flex space-x-2">
                  <button className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-zinc-800 transition-colors">Live Logs</button>
                  <button className="px-4 py-2 bg-brand-600 rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-brand-500 transition-colors">Refresh Data</button>
                </div>
              </div>

              {/* Bento Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {/* Latency Metric */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-[32px] p-6 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <div className="p-3 bg-brand-500/10 rounded-2xl">
                      <Zap size={20} className="text-brand-500" />
                    </div>
                    <span className="text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full">-12%</span>
                  </div>
                  <div className="mt-4">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Avg Latency</p>
                    <h3 className="text-3xl font-bold tracking-tight">242ms</h3>
                  </div>
                </div>

                {/* Queries Metric */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-[32px] p-6 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <div className="p-3 bg-purple-500/10 rounded-2xl">
                      <FileText size={20} className="text-purple-500" />
                    </div>
                    <span className="text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full">+18%</span>
                  </div>
                  <div className="mt-4">
                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">Total Queries</p>
                    <h3 className="text-3xl font-bold tracking-tight">12,842</h3>
                  </div>
                </div>

                {/* Blocked Queries */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-[32px] p-6 flex flex-col justify-between lg:col-span-2">
                  <div className="flex justify-between items-start">
                    <div className="p-3 bg-amber-500/10 rounded-2xl">
                      <Shield size={20} className="text-amber-500" />
                    </div>
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Security Health: Good</span>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Jailbreak Attempts</p>
                      <h3 className="text-2xl font-bold text-red-500">12</h3>
                    </div>
                    <div>
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">PII Redactions</p>
                      <h3 className="text-2xl font-bold text-brand-400">421</h3>
                    </div>
                  </div>
                </div>

                {/* Security Log Table */}
                <div className="lg:col-span-3 bg-zinc-900/50 border border-zinc-800 rounded-[32px] overflow-hidden">
                  <div className="p-6 border-b border-zinc-800 flex justify-between items-center">
                    <h3 className="font-bold">Security & Guardrail Logs</h3>
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  </div>
                  <div className="p-6">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 border-b border-zinc-800">
                          <th className="pb-4">Timestamp</th>
                          <th className="pb-4">User</th>
                          <th className="pb-4">Action</th>
                          <th className="pb-4">Reason</th>
                        </tr>
                      </thead>
                      <tbody className="text-[11px] font-medium">
                        <tr className="border-b border-zinc-800/50">
                          <td className="py-4 text-zinc-500 italic">2 mins ago</td>
                          <td className="py-4 font-bold text-zinc-300">fin_user_01</td>
                          <td className="py-4"><span className="text-red-500 bg-red-500/10 px-2 py-0.5 rounded uppercase font-bold">Blocked</span></td>
                          <td className="py-4 text-zinc-400">Restricted Category Access</td>
                        </tr>
                        <tr className="border-b border-zinc-800/50">
                          <td className="py-4 text-zinc-500 italic">14 mins ago</td>
                          <td className="py-4 font-bold text-zinc-300">mark_user_02</td>
                          <td className="py-4"><span className="text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded uppercase font-bold">Scrubbed</span></td>
                          <td className="py-4 text-zinc-400">PII Detection (Email)</td>
                        </tr>
                        <tr>
                          <td className="py-4 text-zinc-500 italic">1 hour ago</td>
                          <td className="py-4 font-bold text-zinc-300">admin</td>
                          <td className="py-4"><span className="text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded uppercase font-bold">Allowed</span></td>
                          <td className="py-4 text-zinc-400">System Configuration Query</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* RBAC Matrix Card */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-[32px] p-6 overflow-hidden">
                  <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-6">RBAC Matrix</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-400">Finance Docs</span>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 rounded bg-brand-500" title="Admin" />
                        <div className="w-2 h-2 rounded bg-emerald-500" title="Finance" />
                        <div className="w-2 h-2 rounded bg-zinc-800" />
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-400">Marketing Docs</span>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 rounded bg-brand-500" />
                        <div className="w-2 h-2 rounded bg-zinc-800" />
                        <div className="w-2 h-2 rounded bg-purple-500" title="Marketing" />
                      </div>
                    </div>
                    <div className="flex items-center justify-between border-t border-zinc-800 pt-4 mt-4">
                      <span className="text-[9px] font-bold text-brand-500 uppercase tracking-widest">Configure Grid</span>
                      <ArrowRight size={12} className="text-brand-500" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'settings' && (
            <div className="p-8 max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold mb-6">RAG Configuration</h2>
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-8 space-y-8">
                {/* Top K */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <label className="font-medium">Top K Chunks</label>
                    <span className="px-3 py-1 bg-brand-600/20 text-brand-400 rounded-full font-bold">{ragSettings.topK}</span>
                  </div>
                  <input 
                    type="range" 
                    min="1" 
                    max="20" 
                    value={ragSettings.topK}
                    onChange={(e) => setRagSettings(prev => ({ ...prev, topK: parseInt(e.target.value) }))}
                    className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
                  />
                  <div className="flex justify-between text-[10px] text-zinc-500 mt-2 uppercase tracking-widest">
                    <span>Precision</span>
                    <span>Recall</span>
                  </div>
                </div>

                {/* HyDE */}
                <div className="flex justify-between items-center py-4 border-t border-zinc-800">
                  <div>
                    <p className="font-medium">HyDE Expansion</p>
                    <p className="text-xs text-zinc-500">Hypothetical Document Embeddings for better retrieval</p>
                  </div>
                  <button 
                    onClick={() => setRagSettings(prev => ({ ...prev, useHyde: !prev.useHyde }))}
                    className={cn(
                      "w-12 h-6 rounded-full transition-colors relative p-1",
                      ragSettings.useHyde ? "bg-brand-600" : "bg-zinc-800"
                    )}
                  >
                    <div className={cn(
                      "w-4 h-4 rounded-full bg-white transition-transform",
                      ragSettings.useHyde ? "translate-x-6" : "translate-x-0"
                    )} />
                  </button>
                </div>

                {/* Multi-Query */}
                <div className="flex justify-between items-center py-4 border-t border-zinc-800">
                  <div>
                    <p className="font-medium">Multi-Query Retrieval</p>
                    <p className="text-xs text-zinc-500">Generate multiple search queries for broader context</p>
                  </div>
                  <button 
                    onClick={() => setRagSettings(prev => ({ ...prev, multiQuery: !prev.multiQuery }))}
                    className={cn(
                      "w-12 h-6 rounded-full transition-colors relative p-1",
                      ragSettings.multiQuery ? "bg-brand-600" : "bg-zinc-800"
                    )}
                  >
                    <div className={cn(
                      "w-4 h-4 rounded-full bg-white transition-transform",
                      ragSettings.multiQuery ? "translate-x-6" : "translate-x-0"
                    )} />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

    </div>
  );
}

export default App;
