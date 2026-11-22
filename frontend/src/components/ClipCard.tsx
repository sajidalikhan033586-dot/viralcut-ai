import React, { useState } from 'react';
import { Download, Award, Clock, FileText, Sparkles, ChevronDown, ChevronUp, Check } from 'lucide-react';
import type { Clip } from '../types';

interface ClipCardProps {
  clip: Clip;
  onOpenScoreModal: (clip: Clip) => void;
}

export const ClipCard: React.FC<ClipCardProps> = ({ clip, onOpenScoreModal }) => {
  const [showTranscript, setShowTranscript] = useState(false);
  const [copied, setCopied] = useState(false);

  // Time format helper: MM:SS
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const videoUrl = `/media/clips/${clip.file_name}`;
  const downloadUrl = `/api/clips/${clip.id}/download`;

  const handleCopyRationale = () => {
    navigator.clipboard.writeText(clip.rationale);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-2xl overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300 flex flex-col group">
      
      {/* Video Container (9:16 portrait preview or source ratio) */}
      <div className="relative aspect-[9/16] bg-slate-950 overflow-hidden flex items-center justify-center">
        <video
          src={videoUrl}
          controls
          preload="metadata"
          className="w-full h-full object-cover"
        />

        {/* Floating Viral Score Badge */}
        <div className="absolute top-3 right-3 z-10">
          <button
            onClick={() => onOpenScoreModal(clip)}
            className="flex items-center space-x-1.5 bg-slate-950/90 backdrop-blur-md border border-purple-500/40 hover:border-purple-400 px-3 py-1.5 rounded-full shadow-lg transition-all cursor-pointer group/score"
          >
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
            <span className="text-xs font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-pink-300">
              {clip.viral_score}
            </span>
            <span className="text-[10px] text-slate-400 group-hover/score:text-white transition-colors">Score</span>
          </button>
        </div>

        {/* Duration badge */}
        <div className="absolute bottom-3 left-3 z-10 pointer-events-none">
          <span className="px-2 py-0.5 text-[11px] font-mono font-medium bg-black/80 backdrop-blur-sm text-slate-200 rounded border border-white/10">
            {clip.duration.toFixed(1)}s
          </span>
        </div>
      </div>

      {/* Card Content & Details */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-4">
        
        <div>
          {/* Timestamp range & Aspect */}
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2 font-mono">
            <span className="flex items-center space-x-1">
              <Clock className="w-3 h-3 text-slate-500" />
              <span>{formatTime(clip.start_time)} - {formatTime(clip.end_time)}</span>
            </span>
            <span className="px-1.5 py-0.5 bg-slate-800 text-[10px] rounded font-semibold text-slate-300">
              {clip.aspect_ratio}
            </span>
          </div>

          {/* Title & Hook Headline */}
          <h4 className="text-base font-bold text-white leading-snug tracking-tight mb-1">
            {clip.title}
          </h4>
          {clip.hook_headline && (
            <p className="text-xs font-medium text-purple-300 italic mb-3">
              "{clip.hook_headline}"
            </p>
          )}

          {/* One-Sentence Selection Rationale */}
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3 text-xs text-slate-300 leading-relaxed relative">
            <div className="flex items-start justify-between">
              <span className="font-semibold text-purple-400 text-[10px] uppercase tracking-wider block mb-1">
                AI Selection Rationale
              </span>
              <button
                onClick={handleCopyRationale}
                className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 cursor-pointer"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : 'Copy'}
              </button>
            </div>
            <p className="text-slate-300 text-xs">{clip.rationale}</p>
          </div>
        </div>

        {/* Transcript Collapsible */}
        <div className="border-t border-slate-800 pt-3">
          <button
            onClick={() => setShowTranscript(!showTranscript)}
            className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 transition-colors py-1 cursor-pointer"
          >
            <span className="flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5 text-slate-500" />
              <span>Spoken Transcript</span>
            </span>
            {showTranscript ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showTranscript && (
            <div className="mt-2.5 p-3 rounded-lg bg-slate-950/90 border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans max-h-36 overflow-y-auto">
              {clip.transcript_text}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2 pt-1">
          <a
            href={downloadUrl}
            download={clip.file_name}
            className="flex-1 py-2.5 px-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs tracking-wide flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-purple-600/20 active:scale-[0.98] cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download MP4</span>
          </a>

          <button
            onClick={() => onOpenScoreModal(clip)}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer border border-slate-700/60"
            title="View Virality Metrics"
          >
            <Award className="w-4 h-4 text-purple-400" />
          </button>
        </div>

      </div>
    </div>
  );
};
