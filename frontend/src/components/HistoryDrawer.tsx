import React, { useEffect, useState } from 'react';
import { X, Clock, CheckCircle2, AlertCircle, Loader2, ArrowRight } from 'lucide-react';
import type { Job } from '../types';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectJob: (jobId: string) => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  onSelectJob,
}) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      fetchJobs();
    }
  }, [isOpen]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/jobs');
      if (res.ok) {
        const data = await res.json();
        setJobs(data);
      }
    } catch (e) {
      console.error('Failed to load jobs history:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full p-6 flex flex-col shadow-2xl">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">Clipping Job History</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content List */}
        <div className="flex-1 overflow-y-auto py-4 space-y-3">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-48 space-y-2 text-slate-400 text-xs">
              <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
              <span>Loading past jobs...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs">
              No previous clipping jobs recorded yet.
            </div>
          ) : (
            jobs.map((j) => (
              <div
                key={j.id}
                onClick={() => {
                  onSelectJob(j.id);
                  onClose();
                }}
                className="bg-slate-950/80 hover:bg-slate-800/60 border border-slate-800/80 hover:border-purple-500/50 p-4 rounded-xl cursor-pointer transition-all group"
              >
                <div className="flex items-start justify-between mb-1.5">
                  <h4 className="text-xs font-bold text-white group-hover:text-purple-300 transition-colors line-clamp-1">
                    {j.video_title || j.source_filename || j.id}
                  </h4>
                  {j.status === 'completed' ? (
                    <span className="flex items-center space-x-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Done</span>
                    </span>
                  ) : j.status === 'failed' ? (
                    <span className="flex items-center space-x-1 text-[10px] font-semibold text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20">
                      <AlertCircle className="w-3 h-3" />
                      <span>Failed</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-1 text-[10px] font-semibold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-full border border-purple-500/20">
                      <Loader2 className="w-3 h-3 animate-spin" />
                      <span>{j.progress.toFixed(0)}%</span>
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-2">
                  <span>{new Date(j.created_at).toLocaleDateString()}</span>
                  <span className="flex items-center space-x-1 text-slate-400">
                    <span>{j.clip_count ?? (j.clips?.length || 0)} clips</span>
                    <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
};
