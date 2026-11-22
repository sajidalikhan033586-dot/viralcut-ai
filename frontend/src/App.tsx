import { useState, useEffect, useRef } from 'react';
import { Sparkles, AlertCircle } from 'lucide-react';
import type { Job, Clip, SystemStatus } from './types';
import { Navbar } from './components/Navbar';
import { VideoInput } from './components/VideoInput';
import { ProcessingProgress } from './components/ProcessingProgress';
import { ClipGrid } from './components/ClipGrid';
import { ScoreModal } from './components/ScoreModal';
import { HistoryDrawer } from './components/HistoryDrawer';

export function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [scoreModalClip, setScoreModalClip] = useState<Clip | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  // 1. Fetch system status and latest job on load
  useEffect(() => {
    fetchSystemStatus();
    fetchLatestJob();
    setupWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchLatestJob = async () => {
    try {
      const res = await fetch('/api/jobs?limit=1');
      if (res.ok) {
        const jobs = await res.json();
        if (jobs && jobs.length > 0) {
          loadJobDetails(jobs[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to load latest job:', e);
    }
  };

  // Periodic polling fallback while a job is running or queued
  useEffect(() => {
    if (!activeJob) return;
    const isOngoing = activeJob.status === 'processing' || activeJob.status === 'queued' || isProcessing;
    if (!isOngoing) return;

    const interval = setInterval(() => {
      loadJobDetails(activeJob.id);
    }, 1000);
    return () => clearInterval(interval);
  }, [isProcessing, activeJob?.id, activeJob?.status]);

  const fetchSystemStatus = async () => {
    try {
      const res = await fetch('/api/system/status');
      if (res.ok) {
        const data = await res.json();
        setSystemStatus(data);
      }
    } catch (e) {
      console.warn('System status check offline:', e);
    }
  };

  // 2. Setup WebSocket for real-time progress updates
  const setupWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { type, data } = payload;

          if (type === 'job_progress') {
            setIsProcessing(true);
            setActiveJob((prev) => {
              if (prev && prev.id === data.job_id) {
                return {
                  ...prev,
                  progress: data.progress,
                  current_stage: data.stage,
                  status: 'processing',
                };
              } else if (!prev || prev.id !== data.job_id) {
                // If user refreshed or new job, initialize activeJob
                return {
                  id: data.job_id,
                  created_at: new Date().toISOString(),
                  status: 'processing',
                  progress: data.progress,
                  current_stage: data.stage,
                  source_type: 'youtube',
                  source_url: '',
                  clips: [],
                  settings: {},
                } as any;
              }
              return prev;
            });
          } else if (type === 'job_completed') {
            setIsProcessing(false);
            loadJobDetails(data.job_id);
          } else if (type === 'job_failed') {
            setIsProcessing(false);
            setErrorBanner(data.error || 'Video clipping pipeline failed.');
            loadJobDetails(data.job_id);
          } else if (type === 'job_cancelled') {
            setIsProcessing(false);
            loadJobDetails(data.job_id);
          }
        } catch (e) {
          console.error('Error handling WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setTimeout(setupWebSocket, 3000);
      };
    } catch (e) {
      console.error('WebSocket connection error:', e);
    }
  };

  const loadJobDetails = async (jobId: string) => {
    try {
      const res = await fetch(`/api/jobs/${jobId}`);
      if (res.ok) {
        const job = await res.json();
        setActiveJob(job);
        if (job.status === 'processing' || job.status === 'queued') {
          setIsProcessing(true);
        } else {
          setIsProcessing(false);
        }
      }
    } catch (e) {
      console.error('Failed to fetch job details:', e);
    }
  };

  // 3. Submit YouTube URL
  const handleSubmitYouTube = async (url: string, settings: any) => {
    setErrorBanner(null);
    setIsProcessing(true);

    // Provide immediate responsive feedback in UI
    setActiveJob({
      id: 'Starting...',
      created_at: new Date().toISOString(),
      status: 'processing',
      progress: 3.0,
      current_stage: 'Validating YouTube URL and initializing engine...',
      source_type: 'youtube',
      source_url: url,
      clips: [],
      settings: settings,
    } as any);

    try {
      const res = await fetch('/api/jobs/youtube', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, ...settings }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to submit YouTube video');
      }
      const data = await res.json();
      loadJobDetails(data.job_id);
    } catch (e: any) {
      setIsProcessing(false);
      setErrorBanner(e.message || 'Error submitting video');
    }
  };

  // 4. Submit Local File Upload
  const handleSubmitUpload = async (file: File, settings: any) => {
    setErrorBanner(null);
    setIsProcessing(true);

    setActiveJob({
      id: 'Starting...',
      created_at: new Date().toISOString(),
      status: 'processing',
      progress: 3.0,
      current_stage: `Uploading ${file.name} to local workspace...`,
      source_type: 'upload',
      source_filename: file.name,
      clips: [],
      settings: settings,
    } as any);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_duration', settings.target_duration);
      formData.append('aspect_ratio', settings.aspect_ratio);
      formData.append('max_clips', settings.max_clips);
      formData.append('enable_captions', String(settings.enable_captions));
      formData.append('caption_style', settings.caption_style);
      formData.append('language', settings.language);
      formData.append('model_size', settings.model_size || 'tiny');

      const res = await fetch('/api/jobs/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to upload video');
      }
      const data = await res.json();
      loadJobDetails(data.job_id);
    } catch (e: any) {
      setIsProcessing(false);
      setErrorBanner(e.message || 'Error uploading file');
    }
  };

  // 5. Cancel active job
  const handleCancelJob = async () => {
    if (!activeJob) return;
    try {
      await fetch(`/api/jobs/${activeJob.id}/cancel`, { method: 'POST' });
      setIsProcessing(false);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-purple-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        status={systemStatus}
        onOpenHistory={() => setIsHistoryOpen(true)}
      />

      {/* Main Studio Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-8">
        
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto space-y-3 pt-2">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold mb-1 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-yellow-300 animate-pulse" />
            <span>Autonomous Viral Moment Intelligence Engine</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight">
            Turn Any Long Video Into <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-amber-300">
              Viral Short-Form Clips
            </span>
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Automatic multimodal speech analysis, intelligent hook detection, dynamic 9:16 vertical reframing, and word-level animated captions. No manual scrubbing required.
          </p>
        </div>

        {/* Global Error Banner */}
        {errorBanner && (
          <div className="max-w-4xl mx-auto bg-red-950/80 border border-red-500/40 p-4 rounded-xl flex items-center justify-between text-red-200 text-xs">
            <div className="flex items-center space-x-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span>{errorBanner}</span>
            </div>
            <button
              onClick={() => setErrorBanner(null)}
              className="text-slate-400 hover:text-white px-2 py-1 rounded"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Studio Input Area */}
        <div className="max-w-4xl mx-auto">
          <VideoInput
            onSubmitYouTube={handleSubmitYouTube}
            onSubmitUpload={handleSubmitUpload}
            isProcessing={isProcessing}
          />
        </div>

        {/* Real-Time Processing Progress */}
        {(isProcessing || activeJob?.status === 'processing' || activeJob?.status === 'queued') && activeJob && (
          <div className="max-w-4xl mx-auto">
            <ProcessingProgress
              progress={activeJob.progress}
              stageName={activeJob.current_stage}
              jobId={activeJob.id}
              onCancel={handleCancelJob}
            />
          </div>
        )}

        {/* Results Studio Grid */}
        {activeJob && activeJob.clips && activeJob.clips.length > 0 && (
          <div className="pt-4">
            <ClipGrid
              job={activeJob}
              onOpenScoreModal={(clip) => setScoreModalClip(clip)}
            />
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/90 py-6 text-center text-xs text-slate-500">
        <p>VIRALCUT AI — Autonomous Multilingual Video Intelligence Studio • Windows-First Local Processing</p>
      </footer>

      {/* Score Breakdown Modal */}
      <ScoreModal
        clip={scoreModalClip}
        onClose={() => setScoreModalClip(null)}
      />

      {/* History Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectJob={(id) => loadJobDetails(id)}
      />
    </div>
  );
}

export default App;
