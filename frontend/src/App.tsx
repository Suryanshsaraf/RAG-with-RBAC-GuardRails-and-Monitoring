import { useState, useEffect } from 'react';
import { Login } from './components/Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8 pb-4 border-b border-zinc-800">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-500 to-purple-500 bg-clip-text text-transparent">
            Enterprise RAG
          </h1>
          <button 
            onClick={handleLogout}
            className="px-4 py-2 text-sm text-zinc-400 hover:text-white transition-colors"
          >
            Sign Out
          </button>
        </header>
        <div>
          Dashboard Placeholder
        </div>
      </div>
    </div>
  );
}

export default App;
