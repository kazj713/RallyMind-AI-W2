import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class PoseFrame:
    frame_idx: int
    landmarks: np.ndarray
    timestamp: float


@dataclass
class MotionMetrics:
    shoulder_rotation: List[float]
    hip_rotation: List[float]
    knee_flexion: List[float]
    elbow_angle: List[float]
    wrist_position: List[Tuple[float, float]]
    center_of_gravity: List[Tuple[float, float]]
    velocity: List[float]


class AdvancedPoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract_landmarks_array(self, landmarks) -> np.ndarray:
        lm_list = []
        for lm in landmarks.landmark:
            lm_list.extend([lm.x, lm.y, lm.z, lm.visibility])
        return np.array(lm_list)

    def calculate_angle_3d(self, point1: np.ndarray, point2: np.ndarray, point3: np.ndarray) -> float:
        v1 = point1 - point2
        v2 = point3 - point2
        cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
        return angle

    def analyze_pose_sequence(self, video_path: str, sample_rate: int = 2) -> Tuple[List[PoseFrame], MotionMetrics, List[np.ndarray]]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        pose_frames = []
        annotated_frames = []
        shoulder_rotation = []
        hip_rotation = []
        knee_flexion = []
        elbow_angle = []
        wrist_position = []
        center_of_gravity = []
        velocity = []

        prev_landmarks = None
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks
                    lm_array = self.extract_landmarks_array(landmarks)
                    
                    pose_frame = PoseFrame(
                        frame_idx=frame_idx,
                        landmarks=lm_array,
                        timestamp=frame_idx / fps
                    )
                    pose_frames.append(pose_frame)

                    lm_coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
                    
                    left_shoulder = lm_coords[11]
                    right_shoulder = lm_coords[12]
                    left_hip = lm_coords[23]
                    right_hip = lm_coords[24]
                    left_knee = lm_coords[25]
                    right_knee = lm_coords[26]
                    left_elbow = lm_coords[13]
                    right_elbow = lm_coords[14]
                    left_wrist = lm_coords[15]
                    right_wrist = lm_coords[16]

                    shoulder_dist = np.linalg.norm(left_shoulder - right_shoulder)
                    shoulder_rotation.append(shoulder_dist)

                    hip_dist = np.linalg.norm(left_hip - right_hip)
                    hip_rotation.append(hip_dist)

                    left_knee_angle = self.calculate_angle_3d(left_hip, left_knee, lm_coords[27])
                    right_knee_angle = self.calculate_angle_3d(right_hip, right_knee, lm_coords[28])
                    knee_flexion.append((left_knee_angle + right_knee_angle) / 2)

                    left_elbow_angle = self.calculate_angle_3d(left_shoulder, left_elbow, left_wrist)
                    right_elbow_angle = self.calculate_angle_3d(right_shoulder, right_elbow, right_wrist)
                    elbow_angle.append((left_elbow_angle + right_elbow_angle) / 2)

                    avg_wrist = ((left_wrist + right_wrist) / 2)[:2]
                    wrist_position.append(tuple(avg_wrist))

                    cog = np.mean(lm_coords[[11, 12, 23, 24]], axis=0)[:2]
                    center_of_gravity.append(tuple(cog))

                    if prev_landmarks is not None:
                        displacement = np.linalg.norm(lm_coords - prev_landmarks)
                        velocity.append(displacement * fps / sample_rate)
                    else:
                        velocity.append(0.0)

                    prev_landmarks = lm_coords

                    annotated_frame = frame.copy()
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    annotated_frames.append(annotated_frame)

            frame_idx += 1

        cap.release()

        metrics = MotionMetrics(
            shoulder_rotation=shoulder_rotation,
            hip_rotation=hip_rotation,
            knee_flexion=knee_flexion,
            elbow_angle=elbow_angle,
            wrist_position=wrist_position,
            center_of_gravity=center_of_gravity,
            velocity=velocity
        )

        return pose_frames, metrics, annotated_frames

    def get_temporal_features(self, metrics: MotionMetrics, sequence_length: int = 60) -> np.ndarray:
        features = []
        
        def pad_or_truncate(arr: List[float], target_len: int) -> List[float]:
            if len(arr) >= target_len:
                return arr[-target_len:]
            else:
                return [0.0] * (target_len - len(arr)) + list(arr)
        
        for attr in ['shoulder_rotation', 'hip_rotation', 'knee_flexion', 'elbow_angle', 'velocity']:
            arr = getattr(metrics, attr)
            features.extend(pad_or_truncate(arr, sequence_length))
        
        return np.array(features)
