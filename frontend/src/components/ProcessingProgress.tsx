import React from 'react';
import { Loader2, CheckCircle2, Sparkles, Film, Mic, Brain, Trophy, Scissors, ShieldCheck } from 'lucide-react';

interface ProcessingProgressProps {
  progress: number;
  stageName: string;
  jobId: string;
  onCancel: () => void;
}

const STAGES = [
  { id: 1, label: 'Preparing Video & Metadata', icon: Film, threshold: 15 },
  { id: 2, label: 'Audio Signal & Dynamics', icon: Mic, threshold: 30 },
  { id: 3, label: 'Multilingual Speech Recognition', icon: Brain, threshold: 48 },
  { id: 4, label: 'Viral Discovery & Scoring', icon: Trophy, threshold: 68 },
  { id: 5, label: 'Face Tracking & Smart Reframing', icon: Scissors, threshold: 75 },
  { id: 6, label: 'Rendering Clips & Captions', icon: Sparkles, threshold: 94 },
  { id: 7, label: 'Final Quality Verification', icon: ShieldCheck, threshold: 100 },
];

export const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  progress,
  stageName,
  jobId,
  onCancel,
}) => {
  return (
    <div className="bg-slate-900/90 border border-purple-500/30 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl mb-8">
      {/* Glow pulse bar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
            <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Autonomous Video Pipeline in Progress
              <span className="text-xs px-2 py-0.5 font-mono bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
                {progress.toFixed(0)}%
              </span>
            </h3>
            <p className="text-xs text-purple-300 font-medium">
              [{jobId.substring(0, 8)}] {stageName || 'Processing video...'}
            </p>
          </div>
        </div>

        <button
          onClick={onCancel}
          className="text-xs font-medium text-slate-400 hover:text-red-400 border border-slate-800 hover:border-red-500/30 bg-slate-950 px-3 py-1.5 rounded-lg transition-all cursor-pointer"
        >
          Cancel Job
        </button>
      </div>

      {/* Progress Bar Container */}
      <div className="w-full bg-slate-950 rounded-full h-3 p-0.5 border border-slate-800 mb-6 overflow-hidden">
        <div
          className="bg-gradient-to-r from-purple-600 via-indigo-500 to-pink-500 h-full rounded-full transition-all duration-300 shadow-lg shadow-purple-500/50"
          style={{ width: `${Math.max(3, Math.min(100, progress))}%` }}
        />
      </div>

      {/* Stages Stepper */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {STAGES.map((s) => {
          const Icon = s.icon;
          const isDone = progress >= s.threshold;
          const isCurrent = progress < s.threshold && (progress >= (s.threshold - 18) || s.id === 1);

          return (
            <div
              key={s.id}
              className={`p-3 rounded-xl border text-left transition-all ${
                isDone
                  ? 'bg-slate-950/80 border-emerald-500/30 text-emerald-400'
                  : isCurrent
                  ? 'bg-purple-950/40 border-purple-500/50 text-purple-200 shadow-md shadow-purple-500/10'
                  : 'bg-slate-950/30 border-slate-800/60 text-slate-500'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <Icon className={`w-4 h-4 ${isDone ? 'text-emerald-400' : isCurrent ? 'text-purple-400' : 'text-slate-600'}`} />
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-3.5 h-3.5 text-purple-400 animate-spin" />
                ) : (
                  <span className="text-[10px] font-mono text-slate-600">0{s.id}</span>
                )}
              </div>
              <p className="text-[11px] font-medium leading-tight">{s.label}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
