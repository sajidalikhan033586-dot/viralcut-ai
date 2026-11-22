import React from 'react';
import { Sparkles, Cpu, Film, History, Zap } from 'lucide-react';
import type { SystemStatus } from '../types';

interface NavbarProps {
  status: SystemStatus | null;
  onOpenHistory: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ status, onOpenHistory }) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand identity */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-pink-500 p-0.5 flex items-center justify-center shadow-lg shadow-purple-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Zap className="w-5 h-5 text-purple-400 fill-purple-400/20" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                VIRALCUT <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 font-black">AI</span>
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20 rounded-full tracking-wider uppercase">
                Studio
              </span>
            </div>
            <p className="text-xs text-slate-400">Intelligent Autonomous Short-Form Video Engine</p>
          </div>
        </div>

        {/* System & Hardware Diagnostics */}
        <div className="hidden md:flex items-center space-x-3 text-xs">
          
          {/* FFmpeg Indicator */}
          <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            <Film className="w-3.5 h-3.5 text-indigo-400" />
            <span>FFmpeg 9.0</span>
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>

          {/* GPU / Hardware Acceleration */}
          <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            <span>{status?.gpu?.device || 'RTX 3060 12GB'}</span>
            <span className="text-[10px] px-1 bg-purple-500/20 text-purple-300 rounded font-mono">NVENC</span>
          </div>

          {/* AI Model Stack */}
          <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-pink-400" />
            <span>Whisper Multilingual</span>
          </div>
        </div>

        {/* History drawer toggle */}
        <button
          onClick={onOpenHistory}
          className="flex items-center space-x-2 bg-slate-900 hover:bg-slate-800 border border-slate-700/60 hover:border-slate-600 text-slate-200 px-3.5 py-1.5 rounded-xl transition-all text-xs font-medium cursor-pointer shadow-sm"
        >
          <History className="w-4 h-4 text-slate-400" />
          <span>Job History</span>
        </button>

      </div>
    </header>
  );
};
