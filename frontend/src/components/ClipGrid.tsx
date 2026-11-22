import React, { useState } from 'react';
import { Download, FolderOpen, Sparkles } from 'lucide-react';
import type { Clip, Job } from '../types';
import { ClipCard } from './ClipCard';

interface ClipGridProps {
  job: Job;
  onOpenScoreModal: (clip: Clip) => void;
}

export const ClipGrid: React.FC<ClipGridProps> = ({ job, onOpenScoreModal }) => {
  const clips = job.clips || [];
  const [openingFolder, setOpeningFolder] = useState(false);
  const [folderNotice, setFolderNotice] = useState<string | null>(null);

  if (clips.length === 0) {
    return null;
  }

  // Calculate average viral score
  const avgScore = (clips.reduce((acc, c) => acc + c.viral_score, 0) / clips.length).toFixed(1);

  const handleOpenFolder = async () => {
    try {
      setOpeningFolder(true);
      const res = await fetch(`/api/jobs/${job.id}/open-folder`, { method: 'POST' });
      if (res.ok) {
        setFolderNotice('Opened in Windows Explorer');
        setTimeout(() => setFolderNotice(null), 3000);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setOpeningFolder(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Studio Header & Batch Actions */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-purple-400 uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4 text-yellow-300" />
            <span>Ready-to-Publish AI Clips</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {job.video_title || 'Exported Short-Form Clips'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Generated <span className="text-white font-semibold">{clips.length} clips</span> • Average Viral Potential:{' '}
            <span className="text-purple-300 font-bold">{avgScore}/100</span>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          
          {/* Open Folder Button */}
          <button
            onClick={handleOpenFolder}
            disabled={openingFolder}
            className="flex-1 sm:flex-none py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-slate-200 text-xs font-semibold flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-sm"
          >
            <FolderOpen className="w-4 h-4 text-indigo-400" />
            <span>{folderNotice || 'Open Output Folder'}</span>
          </button>

          {/* Download All as ZIP */}
          <a
            href={`/api/jobs/${job.id}/download-all`}
            className="flex-1 sm:flex-none py-2.5 px-5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-xs font-bold flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-lg shadow-purple-600/25 active:scale-[0.98]"
          >
            <Download className="w-4 h-4" />
            <span>Download All (ZIP)</span>
          </a>

        </div>
      </div>

      {/* Grid of Clip Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {clips.map((clip) => (
          <ClipCard
            key={clip.id}
            clip={clip}
            onOpenScoreModal={onOpenScoreModal}
          />
        ))}
      </div>

    </div>
  );
};
