import React, { useState } from 'react';
import { Upload, Sparkles, Clock, Smartphone, Subtitles, Globe, Layers, AlertCircle, Zap } from 'lucide-react';

interface VideoInputProps {
  onSubmitYouTube: (url: string, settings: any) => void;
  onSubmitUpload: (file: File, settings: any) => void;
  isProcessing: boolean;
}

export const VideoInput: React.FC<VideoInputProps> = ({
  onSubmitYouTube,
  onSubmitUpload,
  isProcessing,
}) => {
  const [activeTab, setActiveTab] = useState<'youtube' | 'upload'>('youtube');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Settings state
  const [targetDuration, setTargetDuration] = useState<number>(15);
  const [aspectRatio, setAspectRatio] = useState<string>('9:16');
  const [maxClips, setMaxClips] = useState<number>(5);
  const [enableCaptions, setEnableCaptions] = useState<boolean>(true);
  const [captionStyle, setCaptionStyle] = useState<string>('dynamic_highlight');
  const [language, setLanguage] = useState<string>('auto');
  const [modelSize, setModelSize] = useState<string>('tiny');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const settings = {
      target_duration: targetDuration,
      aspect_ratio: aspectRatio,
      max_clips: maxClips,
      enable_captions: enableCaptions,
      caption_style: captionStyle,
      language: language,
      model_size: modelSize,
    };

    if (activeTab === 'youtube') {
      if (!youtubeUrl.trim()) {
        setErrorMessage('Please enter a valid YouTube video URL.');
        return;
      }
      if (!youtubeUrl.includes('youtube.com') && !youtubeUrl.includes('youtu.be')) {
        setErrorMessage('Invalid YouTube URL. Please provide a standard link (e.g. youtube.com/watch?v=...)');
        return;
      }
      onSubmitYouTube(youtubeUrl.trim(), settings);
    } else {
      if (!selectedFile) {
        setErrorMessage('Please select or drag a video file to upload.');
        return;
      }
      onSubmitUpload(selectedFile, settings);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setErrorMessage(null);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl">
      {/* Decorative gradient glow background */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Tabs */}
      <div className="flex border-b border-slate-800 mb-6">
        <button
          type="button"
          onClick={() => { setActiveTab('youtube'); setErrorMessage(null); }}
          className={`flex items-center space-x-2 pb-3.5 px-4 text-sm font-semibold border-b-2 transition-all cursor-pointer ${
            activeTab === 'youtube'
              ? 'border-purple-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          {/* Custom YouTube SVG */}
          <svg className="w-4 h-4 text-red-500 fill-current" viewBox="0 0 24 24">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          <span>Paste YouTube Video</span>
        </button>

        <button
          type="button"
          onClick={() => { setActiveTab('upload'); setErrorMessage(null); }}
          className={`flex items-center space-x-2 pb-3.5 px-4 text-sm font-semibold border-b-2 transition-all cursor-pointer ${
            activeTab === 'upload'
              ? 'border-purple-500 text-white'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Upload className="w-4 h-4 text-indigo-400" />
          <span>Upload Local File (MP4, MOV, MKV)</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input Source Area */}
        {activeTab === 'youtube' ? (
          <div>
            <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
              YouTube Video or Podcast Link
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                disabled={isProcessing}
                className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 text-white placeholder-slate-500 rounded-xl px-4 py-3.5 text-sm transition-all outline-none"
              />
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Supports authorized interviews, podcasts, lectures, and long-form recordings in English, Urdu, Hindi, and code-switching.
            </p>
          </div>
        ) : (
          <div>
            <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-2">
              Choose or Drag Video File
            </label>
            <div className="border-2 border-dashed border-slate-700 hover:border-purple-500/80 rounded-xl p-8 text-center bg-slate-950/40 hover:bg-slate-950/70 transition-all cursor-pointer relative">
              <input
                type="file"
                accept="video/mp4,video/quicktime,video/x-matroska,video/webm"
                onChange={handleFileChange}
                disabled={isProcessing}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="flex flex-col items-center justify-center space-y-2">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-sm font-medium text-slate-200">
                  {selectedFile ? selectedFile.name : 'Click to select or drag video file here'}
                </p>
                <p className="text-xs text-slate-500">
                  {selectedFile ? `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB` : 'MP4, MOV, MKV, WEBM (No duration limit, streamed in chunks)'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Studio Controls Matrix */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
          
          {/* Target Clip Duration */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
            <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 mb-2">
              <Clock className="w-3.5 h-3.5 text-purple-400" />
              <span>Duration</span>
            </label>
            <select
              value={targetDuration}
              onChange={(e) => setTargetDuration(Number(e.target.value))}
              disabled={isProcessing}
              className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-2 outline-none focus:border-purple-500"
            >
              <option value={10}>~10 Seconds</option>
              <option value={15}>~15 Seconds (Optimal)</option>
              <option value={20}>~20 Seconds</option>
              <option value={30}>~30 Seconds</option>
            </select>
          </div>

          {/* Output Aspect Ratio */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
            <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 mb-2">
              <Smartphone className="w-3.5 h-3.5 text-pink-400" />
              <span>Output Ratio</span>
            </label>
            <select
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value)}
              disabled={isProcessing}
              className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-2 outline-none focus:border-purple-500"
            >
              <option value="9:16">9:16 (TikTok/Shorts)</option>
              <option value="16:9">16:9 Widescreen</option>
              <option value="1:1">1:1 Square</option>
            </select>
          </div>

          {/* Number of Clips */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
            <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 mb-2">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              <span>Clips</span>
            </label>
            <select
              value={maxClips}
              onChange={(e) => setMaxClips(Number(e.target.value))}
              disabled={isProcessing}
              className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-2 outline-none focus:border-purple-500"
            >
              <option value={3}>Top 3 Clips</option>
              <option value={5}>Top 5 Clips (Best)</option>
              <option value={10}>Top 10 Clips</option>
            </select>
          </div>

          {/* Subtitle / Caption Style */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
            <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 mb-2">
              <Subtitles className="w-3.5 h-3.5 text-yellow-400" />
              <span>Captions</span>
            </label>
            <select
              value={enableCaptions ? captionStyle : 'off'}
              onChange={(e) => {
                if (e.target.value === 'off') {
                  setEnableCaptions(false);
                } else {
                  setEnableCaptions(true);
                  setCaptionStyle(e.target.value);
                }
              }}
              disabled={isProcessing}
              className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-2 outline-none focus:border-purple-500"
            >
              <option value="dynamic_highlight">Dynamic Highlight</option>
              <option value="bold_podcast">Bold Podcast</option>
              <option value="minimal_clean">Minimal Clean</option>
              <option value="modern_creator">Modern Creator</option>
              <option value="off">Captions Off</option>
            </select>
          </div>

          {/* Language Intelligence */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
            <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 mb-2">
              <Globe className="w-3.5 h-3.5 text-emerald-400" />
              <span>Language</span>
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isProcessing}
              className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-2 outline-none focus:border-purple-500"
            >
              <option value="auto">Auto-Detect</option>
              <option value="en">English</option>
              <option value="ur">Urdu (اردو)</option>
              <option value="hi">Hindi</option>
            </select>
          </div>

          {/* AI Speed & Model Mode */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
            <label className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 mb-2">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>AI Speed</span>
            </label>
            <select
              value={modelSize}
              onChange={(e) => setModelSize(e.target.value)}
              disabled={isProcessing}
              className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-2 outline-none focus:border-purple-500 font-medium"
            >
              <option value="tiny">⚡ Ultra Fast (5x)</option>
              <option value="base">🎯 Accurate</option>
            </select>
          </div>

        </div>

        {/* Error notification banner */}
        {errorMessage && (
          <div className="flex items-center space-x-2 bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl px-4 py-3 text-xs">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Primary Action Button */}
        <div>
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-4 px-6 rounded-xl font-bold text-sm tracking-wide text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-pink-600 hover:from-purple-500 hover:via-indigo-500 hover:to-pink-500 active:scale-[0.99] transition-all duration-200 shadow-xl shadow-purple-500/25 flex items-center justify-center space-x-2.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Sparkles className="w-5 h-5 text-yellow-300 animate-spin-slow" />
            <span>{isProcessing ? 'ENGINE RUNNING AUTONOMOUS PIPELINE...' : 'ANALYZE & GENERATE VIRAL CLIPS'}</span>
          </button>
        </div>

      </form>
    </div>
  );
};
