import React from 'react';
import { X, Award, Info, Zap, Flame, Lightbulb, Heart, BookOpen, Share2, Eye } from 'lucide-react';
import type { Clip } from '../types';

interface ScoreModalProps {
  clip: Clip | null;
  onClose: () => void;
}

export const ScoreModal: React.FC<ScoreModalProps> = ({ clip, onClose }) => {
  if (!clip) return null;

  const b = clip.score_breakdown || {
    hook_strength: 85,
    retention_potential: 88,
    semantic_value: 80,
    emotional_intensity: 75,
    narrative_completeness: 82,
    shareability: 84,
    visual_audio_quality: 90,
  };

  const dimensions = [
    { label: 'Hook Strength', weight: '20%', score: b.hook_strength, icon: Zap, color: 'text-yellow-400', bar: 'bg-yellow-400' },
    { label: 'Retention Potential', weight: '20%', score: b.retention_potential, icon: Flame, color: 'text-orange-400', bar: 'bg-orange-400' },
    { label: 'Semantic Value', weight: '15%', score: b.semantic_value, icon: Lightbulb, color: 'text-amber-300', bar: 'bg-amber-300' },
    { label: 'Emotional Intensity', weight: '15%', score: b.emotional_intensity, icon: Heart, color: 'text-pink-400', bar: 'bg-pink-400' },
    { label: 'Narrative Completeness', weight: '15%', score: b.narrative_completeness, icon: BookOpen, color: 'text-indigo-400', bar: 'bg-indigo-400' },
    { label: 'Shareability', weight: '10%', score: b.shareability, icon: Share2, color: 'text-purple-400', bar: 'bg-purple-400' },
    { label: 'Audio / Visual Quality', weight: '5%', score: b.visual_audio_quality, icon: Eye, color: 'text-cyan-400', bar: 'bg-cyan-400' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Viral Potential Score Breakdown</h3>
              <p className="text-xs text-slate-400">Explainable Heuristic Evaluation Model</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Total Score Badge */}
        <div className="my-5 p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
              Viral Potential Score — Heuristic Estimate
            </span>
            <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-amber-300">
              {clip.viral_score} / 100
            </span>
          </div>
          <div className="text-right">
            <span className="px-2.5 py-1 text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">
              {clip.viral_score >= 88 ? 'Tier 1: Exceptional' : clip.viral_score >= 78 ? 'Tier 2: High' : 'Tier 3: Moderate'}
            </span>
          </div>
        </div>

        {/* 7 Dimensions List */}
        <div className="space-y-3 mb-5">
          {dimensions.map((d, idx) => {
            const Icon = d.icon;
            return (
              <div key={idx} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="flex items-center space-x-2 text-slate-200 font-medium">
                    <Icon className={`w-3.5 h-3.5 ${d.color}`} />
                    <span>{d.label}</span>
                    <span className="text-[10px] text-slate-500 font-mono">({d.weight})</span>
                  </span>
                  <span className="font-mono font-bold text-slate-200">{d.score} / 100</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`${d.bar} h-full rounded-full transition-all duration-300`}
                    style={{ width: `${Math.min(100, Math.max(5, d.score))}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Disclaimer Note */}
        <div className="flex items-start space-x-2 p-3 bg-purple-500/5 border border-purple-500/20 rounded-xl text-slate-400 text-[11px] leading-relaxed">
          <Info className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
          <span>
            These weights represent explainable content intelligence heuristics, calibrated for rank ordering rather than probabilistic certainty.
          </span>
        </div>

      </div>
    </div>
  );
};
