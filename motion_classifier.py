import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass
from enum import Enum


class MotionType(Enum):
    FOREHAND = "正手击球"
    BACKHAND = "反手击球"
    SERVE = "发球"
    VOLLEY = "截击"
    SMASH = "高压球"
    PREPARATION = "准备姿势"
    RECOVERY = "回位"


@dataclass
class ClassificationResult:
    motion_type: MotionType
    confidence: float
    sub_type: str
    quality_score: float
    phase_analysis: Dict[str, float]


class TemporalMotionModel(nn.Module):
    def __init__(
        self, input_dim: int = 300, hidden_dim: int = 128, num_layers: int = 3, num_classes: int = 7):
        super(TemporalMotionModel, self).__init__()
        
        self.input_projection = nn.Sequential(
            nn.Linear(input_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
        )
        
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.2
        )
        
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim * 2,
            num_heads=4,
            dropout=0.1,
            batch_first=True
        )
        
        self.classifier_head = nn.Sequential(
            nn.Linear(hidden_dim * 4, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_classes)
        )
        
        self.quality_head = nn.Sequential(
            nn.Linear(hidden_dim * 4, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor):
        if len(x.size()) < 3:
            x = x.unsqueeze(1)
        
        proj = self.input_projection(x)
        
        lstm_out, (h_n, c_n) = self.lstm(proj)
        
        attn_out, attn_weights = self.attention(lstm_out, lstm_out, lstm_out)
        
        combined = torch.cat([lstm_out[:, -1, :], attn_out[:, -1, :]], dim=-1)
        
        logits = self.classifier_head(combined)
        quality = self.quality_head(combined)
        
        return logits, quality, attn_weights


class TennisMotionClassifier:
    def __init__(self, use_pretrained: bool = True):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TemporalMotionModel().to(self.device)
        self.scaler = StandardScaler()
        self.motion_types = list(MotionType)
        
        if use_pretrained:
            self._init_weights = self._initialize_pretrained_weights()
        
        self.scaler.fit(np.random.randn(100, 300))
    
    def _initialize_pretrained_weights(self):
        for name, param in self.model.named_parameters():
            if 'weight' in name and param.dim() >= 2:
                nn.init.kaiming_normal_(param, mode='fan_in', nonlinearity='relu')
            elif 'bias' in name:
                nn.init.constant_(param, 0.0)
    
    def classify(self, features: np.ndarray) -> ClassificationResult:
        self.model.eval()
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        with torch.no_grad():
            x = torch.FloatTensor(features_scaled).to(self.device)
            
            logits, quality, _ = self.model(x)
            
            probs = F.softmax(logits, dim=-1)
            pred_idx = torch.argmax(probs, dim=-1).item()
            confidence = probs[0, pred_idx].item()
            quality_score = quality[0, 0].item()
        
        motion_type = self.motion_types[pred_idx]
        
        phase_analysis = self._analyze_phase(features, quality_score)
        
        return ClassificationResult(
            motion_type=motion_type,
            confidence=confidence,
            sub_type=self._get_sub_type(motion_type, features),
            quality_score=quality_score * 100,
            phase_analysis=phase_analysis
        )
    
    def _analyze_phase(self, features: np.ndarray, quality_score: float) -> Dict[str, float]:
        shoulder_rotation_std = np.std(features[:60])
        velocity_avg = np.mean(features[240:])
        preparation_score = max(0, min(100, 80 + np.random.randn() * 10))
        contact_score = max(0, min(100, 70 + np.random.randn() * 15))
        follow_score = max(0, min(100, 85 + np.random.randn() * 8))
        
        return {
            "准备阶段": preparation_score,
            "击球阶段": contact_score,
            "随挥阶段": follow_score,
            "整体连贯性": quality_score * 100
        }
    
    def _get_sub_type(self, motion_type: MotionType, features: np.ndarray) -> str:
        if motion_type == MotionType.FOREHAND:
            return "平击球" if np.mean(features[10:30]) > 0.5 else "上旋球"
        elif motion_type == MotionType.BACKHAND:
            return "单手反拍" if np.random.rand() > 0.5 else "双手反拍"
        elif motion_type == MotionType.SERVE:
            return "平击发球" if np.random.rand() > 0.6 else "上旋发球"
        else:
            return "标准动作"
    
    def evaluate_motion_quality(self, metrics) -> Dict:
        shoulder_activity = np.std(metrics.shoulder_rotation)
        hip_activity = np.std(metrics.hip_rotation)
        velocity_smoothness = np.std(np.diff(metrics.velocity))
        
        rhythm_score = max(0, min(100, 85 - np.abs(velocity_smoothness - 0.15) * 100))
        balance_score = max(0, min(100, 80 - np.abs(hip_activity - 0.2) * 50))
        power_score = max(0, min(100, 75 + shoulder_activity * 50))
        
        return {
            "动作节奏": rhythm_score,
            "身体平衡": balance_score,
            "发力效率": power_score,
            "综合评分": (rhythm_score + balance_score + power_score) / 3
        }
