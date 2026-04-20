import { useState, useEffect } from 'react';
import { Login } from './components/Login';
import { Sidebar } from './components/Sidebar';
import { Chat } from './components/Chat';
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
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'guardrails' | 'settings'>('chat');
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
        <header className="md:hidden flex items-center justify-center h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
          <h1 className="text-xl font-bold bg-gradient-to-r from-brand-400 to-purple-500 bg-clip-text text-transparent uppercase tracking-wider">
            {activeTab === 'chat' ? 'Enterprise RAG' : activeTab}
          </h1>
        </header>
        
        <div className="flex-1 overflow-hidden relative">
          {activeTab === 'chat' && <Chat settings={ragSettings} />}
          {activeTab === 'guardrails' && (
            <div className="p-8 max-w-4xl mx-auto space-y-6">
              <h2 className="text-2xl font-bold">Guardrails Configuration</h2>
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
                <p className="text-zinc-400 mb-4">View and configure AI security policies.</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800">
                    <h3 className="font-medium mb-2">Input Scanning</h3>
                    <p className="text-xs text-zinc-500">Filters toxic, jailbreak, and off-topic questions.</p>
                    <div className="mt-3 flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                      <span className="text-xs font-medium text-green-400 uppercase">Active</span>
                    </div>
                  </div>
                  <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800">
                    <h3 className="font-medium mb-2">PII Scrubbing</h3>
                    <p className="text-xs text-zinc-500">Detects and hides personal identifiable information.</p>
                    <div className="mt-3 flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                      <span className="text-xs font-medium text-green-400 uppercase">Active</span>
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
