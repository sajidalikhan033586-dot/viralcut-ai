import React from 'react';
import { Sparkles, Cpu, Film, History, ExternalLink, TrendingUp } from 'lucide-react';
import type { SystemStatus } from '../types';

interface NavbarProps {
  status: SystemStatus | null;
  onOpenHistory: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ status, onOpenHistory }) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand identity: NextRise Digital */}
        <div className="flex items-center space-x-3.5">
          {/* NextRise Stylized Modern Emblem */}
          <div className="relative group">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/25 transition-transform duration-300 group-hover:scale-105">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center relative overflow-hidden">
                {/* Modern Geometric NR Monogram & Rising Arrow */}
                <svg className="w-6 h-6 text-cyan-400 transition-all duration-300 group-hover:text-cyan-300" viewBox="0 0 32 32" fill="none">
                  <path d="M7 25V7L15 19V7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M17 13L25 7M25 7H19M25 7V13" stroke="url(#rise-grad)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M17 25V17H21C23.2091 17 25 18.7909 25 21C25 23.2091 23.2091 25 21 25H17Z" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                  <defs>
                    <linearGradient id="rise-grad" x1="17" y1="13" x2="25" y2="7" gradientUnits="userSpaceOnUse">
                      <stop stopColor="#38bdf8" />
                      <stop offset="1" stopColor="#818cf8" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full border-2 border-slate-950 animate-pulse" />
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                NextRise <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 font-black">Clipper AI</span>
              </h1>
              <span className="hidden sm:inline-flex px-2 py-0.5 text-[10px] font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 rounded-full tracking-wider uppercase">
                Studio
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <span className="text-slate-300 font-medium">By NextRise Digital</span>
              <span className="text-slate-600">•</span>
              <span className="text-cyan-400/90 hidden md:inline">Learn. Earn. Rise.</span>
            </div>
          </div>
        </div>

        {/* System & Hardware Diagnostics */}
        <div className="hidden lg:flex items-center space-x-3 text-xs">
          {/* FFmpeg Indicator */}
          <div className="flex items-center space-x-1.5 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            <Film className="w-3.5 h-3.5 text-cyan-400" />
            <span>FFmpeg 9.0</span>
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>

          {/* GPU / Hardware Acceleration */}
          <div className="flex items-center space-x-1.5 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>{status?.gpu?.device || 'Hardware AI Engine'}</span>
            <span className="text-[10px] px-1 bg-cyan-500/20 text-cyan-300 rounded font-mono">NVENC</span>
          </div>

          {/* AI Model Stack */}
          <div className="flex items-center space-x-1.5 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            <span>Whisper Multilingual</span>
          </div>
        </div>

        {/* Action Controls & Official Link */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <a
            href="https://nextrisehq.com"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center space-x-1.5 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 hover:from-cyan-500/20 hover:to-blue-500/20 border border-cyan-500/30 text-cyan-300 hover:text-cyan-200 px-3 py-1.5 rounded-xl transition-all text-xs font-semibold"
          >
            <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
            <span>NextRiseHQ</span>
            <ExternalLink className="w-3 h-3 text-cyan-400/80" />
          </a>

          {/* History drawer toggle */}
          <button
            onClick={onOpenHistory}
            className="flex items-center space-x-2 bg-slate-900 hover:bg-slate-800 border border-slate-700/60 hover:border-slate-600 text-slate-200 px-3.5 py-1.5 rounded-xl transition-all text-xs font-medium cursor-pointer shadow-sm"
          >
            <History className="w-4 h-4 text-slate-400" />
            <span>Job History</span>
          </button>
        </div>

      </div>
    </header>
  );
};
