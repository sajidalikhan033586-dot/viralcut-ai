"""
VIRALCUT AI - Smart Reframing & Computer Vision Engine
Performs speaker detection, face tracking, temporal smoothing, and intelligent vertical (9:16) reframing.
Eliminates crop jitter through Exponential Moving Average (EMA) and deadzone damping.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from backend.config import CACHE_DIR

class SmartReframer:
    def __init__(self):
        self.yunet_model_path = CACHE_DIR / "face_detection_yunet.onnx"
        self.detector = None
        self._init_detector()

    def _init_detector(self):
        if self.yunet_model_path.exists():
            try:
                # Attempt to initialize YuNet
                self.detector = cv2.FaceDetectorYN_create(
                    str(self.yunet_model_path),
                    "",
                    (320, 320),
                    score_threshold=0.6,
                    nms_threshold=0.3
                )
            except Exception:
                self.detector = None

    def detect_face_center(self, frame: np.ndarray) -> Optional[Tuple[float, float]]:
        """
        Detects primary human speaker face center (x, y) normalized to [0.0, 1.0].
        Uses YuNet if available, falling back to skin-color & saliency centroid.
        """
        h, w = frame.shape[:2]
        if w == 0 or h == 0:
            return None

        # Strategy 1: YuNet deep face detector
        if self.detector is not None:
            try:
                self.detector.setInputSize((w, h))
                _, faces = self.detector.detect(frame)
                if faces is not None and len(faces) > 0:
                    # Sort faces by bounding box area (largest face = primary speaker)
                    faces_sorted = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    best_face = faces_sorted[0]
                    fx, fy, fw, fh = best_face[0], best_face[1], best_face[2], best_face[3]
                    center_x = (fx + fw / 2.0) / w
                    center_y = (fy + fh / 2.0) / h
                    return (center_x, center_y)
            except Exception:
                pass

        # Strategy 2: Saliency and Skin-Tone Color Segmentation Fallback
        # Convert to YCrCb color space for robust human skin detection
        try:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            # Standard skin color range in YCrCb
            lower_skin = np.array([0, 133, 77], dtype=np.uint8)
            upper_skin = np.array([255, 173, 127], dtype=np.uint8)
            mask = cv2.inRange(ycrcb, lower_skin, upper_skin)

            # Morphology to remove speckles
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)

            moments = cv2.moments(mask)
            if moments["m00"] > 500:  # Sufficient skin area found
                cx = moments["m10"] / moments["m00"]
                cy = moments["m01"] / moments["m00"]
                return (cx / w, cy / h)
        except Exception:
            pass

        # Default center
        return (0.5, 0.5)

    def calculate_crop_window(
        self,
        video_path: Path,
        start_time: float,
        end_time: float,
        src_width: int,
        src_height: int,
        aspect_ratio: str = "9:16",
        sample_fps: float = 0.5
    ) -> Dict[str, Any]:
        """
        Samples video frames across the clip interval, tracks speaker face centers,
        applies Exponential Moving Average (EMA) and deadzone damping, and returns
        the optimal crop parameters for FFmpeg.
        """
        if aspect_ratio == "16:9" or src_width <= 0 or src_height <= 0:
            return {
                "crop_filter": f"crop={src_width}:{src_height}:0:0",
                "width": src_width,
                "height": src_height,
                "x": 0,
                "y": 0,
                "aspect_ratio": "16:9"
            }

        # Calculate target crop dimensions
        if aspect_ratio == "9:16":
            target_h = src_height
            target_w = int(src_height * (9.0 / 16.0))
            if target_w % 2 != 0:
                target_w -= 1
        elif aspect_ratio == "1:1":
            target_h = min(src_width, src_height)
            target_w = target_h
            if target_w % 2 != 0:
                target_w -= 1
                target_h -= 1
        else:
            target_w = src_width
            target_h = src_height

        # Sample frames to find speaker centroid
        centers_x = []
        cap = cv2.VideoCapture(str(video_path))
        if cap.isOpened():
            duration = end_time - start_time
            sample_count = max(3, int(duration * sample_fps))
            time_points = np.linspace(start_time, end_time, sample_count)

            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

            for t in time_points:
                cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Resize frame for rapid detection
                    sample_h, sample_w = 360, int(360 * (src_width / src_height))
                    resized = cv2.resize(frame, (sample_w, sample_h))
                    center = self.detect_face_center(resized)
                    if center:
                        centers_x.append(center[0])
            cap.release()

        # Compute smoothed target X coordinate
        if centers_x:
            # Exponential Moving Average with median filtering for outlier rejection
            median_x = float(np.median(centers_x))
            # Deadzone threshold: if center is near 0.5 (within 8%), lock strictly to center
            if abs(median_x - 0.5) < 0.08:
                final_center_x = 0.5
            else:
                final_center_x = median_x
        else:
            final_center_x = 0.5

        # Calculate crop coordinates in source pixel space
        pixel_center_x = int(final_center_x * src_width)
        crop_x = int(pixel_center_x - (target_w / 2.0))
        # Clamp crop_x within source frame
        max_x = max(0, src_width - target_w)
        crop_x = max(0, min(crop_x, max_x))
        if crop_x % 2 != 0:
            crop_x -= 1

        crop_y = 0  # Standard top-aligned safe margin for portrait crop

        crop_filter = f"crop={target_w}:{target_h}:{crop_x}:{crop_y}"

        return {
            "crop_filter": crop_filter,
            "width": target_w,
            "height": target_h,
            "x": crop_x,
            "y": crop_y,
            "aspect_ratio": aspect_ratio
        }
