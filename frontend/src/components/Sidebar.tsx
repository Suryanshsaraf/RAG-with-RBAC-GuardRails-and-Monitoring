import React, { useState } from 'react';
import { apiService } from '../api/services';
import { UploadCloud, FileText, Settings, Shield, Menu, X } from 'lucide-react';
import { cn } from '../lib/utils';
import type { UserInfo } from '../App';

interface SidebarProps {
  user: UserInfo | null;
  activeTab: 'chat' | 'guardrails' | 'settings';
  setActiveTab: (tab: 'chat' | 'guardrails' | 'settings') => void;
  onLogout: () => void;
  isMobileOpen: boolean;
  setIsMobileOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, activeTab, setActiveTab, onLogout, isMobileOpen, setIsMobileOpen }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error'; msg: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setUploadStatus(null);
    try {
      const res = await apiService.uploadDocument(file);
      setUploadStatus({ type: 'success', msg: res.status });
      setFile(null);
    } catch (err: any) {
      setUploadStatus({ type: 'error', msg: 'Upload failed. Please try again.' });
    } finally {
      setUploading(false);
    }
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-zinc-950/80 backdrop-blur-xl border-r border-zinc-800 text-zinc-300 w-72">
      <div className="p-6">
        <h2 className="text-xl font-bold bg-gradient-to-r from-brand-400 to-purple-500 bg-clip-text text-transparent mb-8">
          Enterprise RAG
        </h2>

        <div className="space-y-2 mb-8">
          <button 
            onClick={() => { setActiveTab('chat'); setIsMobileOpen(false); }}
            className={cn(
              "w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all",
              activeTab === 'chat' ? "bg-brand-600 text-white shadow-lg shadow-brand-500/20" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            )}
          >
            <FileText size={18} />
            <span>Chat Session</span>
          </button>
          <button 
            onClick={() => { setActiveTab('guardrails'); setIsMobileOpen(false); }}
            className={cn(
              "w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all",
              activeTab === 'guardrails' ? "bg-brand-600 text-white shadow-lg shadow-brand-500/20" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            )}
          >
            <Shield size={18} />
            <span>Guardrails</span>
          </button>
          <button 
            onClick={() => { setActiveTab('settings'); setIsMobileOpen(false); }}
            className={cn(
              "w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-all",
              activeTab === 'settings' ? "bg-brand-600 text-white shadow-lg shadow-brand-500/20" : "text-zinc-400 hover:text-white hover:bg-zinc-900"
            )}
          >
            <Settings size={18} />
            <span>Settings</span>
          </button>
        </div>

        <div>
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">
            Knowledge Base
          </h3>
          
          <div className="bg-zinc-900/50 border border-zinc-800/50 rounded-xl p-4">
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-zinc-700 rounded-lg p-6 mb-4 relative hover:bg-zinc-800/50 transition-colors cursor-pointer group">
              <input 
                type="file" 
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileChange}
              />
              <UploadCloud size={24} className="text-zinc-400 mb-2 group-hover:text-brand-400 transition-colors" />
              <p className="text-sm text-center text-zinc-400 group-hover:text-zinc-300 transition-colors">
                {file ? file.name : "Click or drag file to upload"}
              </p>
            </div>

            {file && (
              <button 
                onClick={handleUpload}
                disabled={uploading}
                className="w-full py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg transition-colors flex items-center justify-center disabled:opacity-50"
              >
                {uploading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  'Ingest Document'
                )}
              </button>
            )}

            {uploadStatus && (
              <div className={cn(
                "mt-3 text-xs p-2 rounded",
                uploadStatus.type === 'success' ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
              )}>
                {uploadStatus.msg}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-auto p-6 border-t border-zinc-800">
        <div className="mb-4 flex items-center space-x-3 px-2">
          <div className="w-10 h-10 rounded-full bg-brand-600 flex items-center justify-center font-bold text-white uppercase">
            {user?.username.charAt(0)}
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-medium text-white truncate">{user?.username}</p>
            <p className="text-xs text-zinc-500 uppercase tracking-tight truncate">{user?.role} Role</p>
          </div>
        </div>
        <button 
          onClick={onLogout}
          className="w-full py-2 px-4 rounded-lg border border-zinc-700 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors text-sm"
        >
          Sign Out
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Toggle */}
      <button 
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Desktop Sidebar */}
      <div className="hidden md:block h-screen fixed inset-y-0 left-0 z-40">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar overlay */}
      {isMobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-black/80" onClick={() => setIsMobileOpen(false)} />
          <div className="relative flex-1 flex max-w-xs w-full">
            <SidebarContent />
          </div>
        </div>
      )}
    </>
  );
};
