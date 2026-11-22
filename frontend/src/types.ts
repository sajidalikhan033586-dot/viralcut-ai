export interface ScoreBreakdown {
  hook_strength: number;
  retention_potential: number;
  semantic_value: number;
  emotional_intensity: number;
  narrative_completeness: number;
  shareability: number;
  visual_audio_quality: number;
}

export interface WordTiming {
  word: string;
  start: number;
  end: number;
  probability?: number;
}

export interface Clip {
  id: string;
  job_id: string;
  clip_index: number;
  title: string;
  hook_headline: string;
  rationale: string;
  start_time: number;
  end_time: number;
  duration: number;
  viral_score: number;
  score_breakdown: ScoreBreakdown;
  transcript_text: string;
  words?: WordTiming[];
  file_path: string;
  file_name: string;
  aspect_ratio: string;
  resolution: string;
  file_size?: number;
  created_at: string;
}

export interface Job {
  id: string;
  created_at: string;
  updated_at: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  current_stage: string;
  source_type: 'youtube' | 'local';
  source_url?: string;
  source_filename?: string;
  video_title?: string;
  video_duration?: number;
  video_metadata?: any;
  settings?: any;
  error_message?: string;
  clips?: Clip[];
  clip_count?: number;
}

export interface SystemStatus {
  status: string;
  ffmpeg: {
    installed: boolean;
    binary: string;
  };
  gpu: {
    cuda_available: boolean;
    device: string;
  };
  models: {
    whisper: string;
    face_tracking: string;
  };
  supported_formats: string[];
  default_target_duration: number;
}
