import React, { useState, useRef, useEffect } from 'react';
import { apiService, type QueryResponse } from '../api/services';
import { Send, Bot, User, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const STARTER_PROMPTS = [
  "What are the data privacy policies?",
  "Tell me about the corporate structure.",
  "How does the RBAC system work in this project?"
];

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: QueryResponse['sources'];
  guardrail_triggered?: boolean;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([{
    id: 'welcome',
    role: 'assistant',
    content: 'Welcome to Enterprise RAG. How can I help you today?'
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await apiService.query(userMsg.content);
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        guardrail_triggered: res.guardrail_triggered
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 pb-32">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
        </AnimatePresence>

        {messages.length === 1 && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="max-w-3xl mx-auto mt-12"
          >
            <div className="flex items-center space-x-2 text-zinc-500 mb-4 px-2">
              <span className="text-xs font-bold uppercase tracking-widest text-brand-500">ASK:</span>
              <div className="h-[1px] flex-1 bg-zinc-800" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {STARTER_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setInput(prompt);
                    // We could trigger submit here if we want immediate execution
                  }}
                  className="text-left p-4 rounded-xl bg-zinc-900/50 border border-zinc-800 hover:border-brand-500/50 hover:bg-zinc-800/50 transition-all text-sm text-zinc-300 hover:text-white"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </motion.div>
        )}
        {loading && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start max-w-3xl"
          >
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-600/20 flex items-center justify-center border border-brand-500/30 mr-4">
              <Bot size={16} className="text-brand-400" />
            </div>
            <div className="flex items-center space-x-2 h-8">
              <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce"></div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-zinc-950 via-zinc-950 to-transparent">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="w-full bg-zinc-900/80 backdrop-blur-md border border-zinc-700/50 rounded-2xl py-4 pl-6 pr-14 text-white focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all shadow-xl"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-brand-600 hover:bg-brand-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white rounded-xl transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
        <p className="text-center text-xs text-zinc-500 mt-2">
          Enterprise RAG can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
};

const MessageBubble = ({ msg }: { msg: Message }) => {
  const isUser = msg.role === 'user';
  const [showSources, setShowSources] = useState(false);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex items-start max-w-4xl", isUser && "justify-end ml-auto")}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-brand-600/20 flex items-center justify-center border border-brand-500/30 mr-4 mt-1">
          <Bot size={16} className="text-brand-400" />
        </div>
      )}
      
      <div className={cn(
        "px-6 py-4 rounded-2xl max-w-[85%]",
        isUser 
          ? "bg-brand-600 text-white shadow-brand-500/20 shadow-lg rounded-tr-sm" 
          : "bg-zinc-900/80 border border-zinc-800 text-zinc-100 rounded-tl-sm shadow-xl"
      )}>
        {msg.guardrail_triggered && (
          <div className="flex items-center space-x-2 text-yellow-500 text-xs font-medium mb-2 bg-yellow-500/10 px-2 py-1 rounded w-fit">
            <ShieldAlert size={14} />
            <span>Guardrail Intervened</span>
          </div>
        )}
        
        <div className="prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>

        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-zinc-800/50">
            <button 
              onClick={() => setShowSources(!showSources)}
              className="flex items-center space-x-1 text-xs text-zinc-400 hover:text-zinc-300 transition-colors"
            >
              <span>{msg.sources.length} Sources Used</span>
              {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            
            <AnimatePresence>
              {showSources && (
                <motion.div 
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="mt-3 space-y-2">
                    {msg.sources.map((src, i) => (
                      <div key={i} className="bg-zinc-950 p-3 rounded-lg text-xs border border-zinc-800/50">
                        <div className="font-medium text-brand-400 mb-1">Source {i + 1}</div>
                        <p className="text-zinc-400 line-clamp-3">{src.content}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center border border-zinc-700 ml-4 mt-1">
          <User size={16} className="text-zinc-400" />
        </div>
      )}
    </motion.div>
  );
};
