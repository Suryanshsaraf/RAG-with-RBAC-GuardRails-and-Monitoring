import { useState, useEffect } from 'react';
import { Login } from './components/Login';
import { Sidebar } from './components/Sidebar';
import { Chat } from './components/Chat';
import { jwtDecode } from 'jwt-decode';

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
        onLogout={handleLogout} 
        isMobileOpen={isMobileSidebarOpen}
        setIsMobileOpen={setIsMobileSidebarOpen}
      />
      
      <main className="flex-1 md:ml-72 flex flex-col h-screen">
        <header className="md:hidden flex items-center justify-center h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
          <h1 className="text-xl font-bold bg-gradient-to-r from-brand-400 to-purple-500 bg-clip-text text-transparent">
            Enterprise RAG
          </h1>
        </header>
        
        <div className="flex-1 overflow-hidden relative">
          <Chat />
        </div>
      </main>
    </div>
  );
}

export default App;
