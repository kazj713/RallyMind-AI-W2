import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pose_analyzer import MotionMetrics
from motion_classifier import ClassificationResult


class FeedbackPriority(Enum):
    CRITICAL = "需要立即改进"
    IMPORTANT = "重要改进项"
    SUGGESTION = "建议优化"
    POSITIVE = "表现优秀"


@dataclass
class FeedbackItem:
    category: str
    message: str
    priority: FeedbackPriority
    improvement_tip: str


@dataclass
class FeedbackReport:
    summary: str
    strengths: List[str]
    improvements: List[FeedbackItem]
    exercise_suggestions: List[str]
    overall_score: float


class IntelligentFeedbackGenerator:
    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict:
        return {
            "shoulder": {
                "low_activity": "肩膀活动范围不足，可能影响击球力量",
                "high_activity": "肩膀过度旋转，可能导致受伤风险",
                "tip": "增加肩部柔韧性训练，如肩部环绕和弹力带拉伸"
            },
            "hip": {
                "low_activity": "髋部转动不充分，影响全身发力",
                "high_activity": "髋部过度转动，可能失去平衡",
                "tip": "加强核心力量和髋部灵活性训练"
            },
            "knee": {
                "too_straight": "膝盖过于伸直，缓冲不足",
                "too_bent": "膝盖过度弯曲，影响移动速度",
                "tip": "练习半蹲姿势，保持膝盖微屈"
            },
            "balance": {
                "unstable": "重心不稳定，动作连贯性受影响",
                "tip": "进行单腿站立练习，增强平衡感"
            },
            "rhythm": {
                "irregular": "动作节奏不连贯，影响击球时机把握",
                "tip": "跟着节拍器练习挥拍，培养节奏感"
            }
        }
    
    def generate_feedback(self, classification: ClassificationResult, 
                         metrics: MotionMetrics, quality_eval: Dict) -> FeedbackReport:
        strengths = []
        improvements = []
        
        if quality_eval["身体平衡"] > 75:
            strengths.append("身体平衡控制出色，重心稳定")
        if quality_eval["动作节奏"] > 80:
            strengths.append("动作节奏良好，击球时机把握准确")
        if classification.confidence > 0.7:
            strengths.append(f"动作识别为 {classification.motion_type.value}，特征明显")
        
        shoulder_std = np.std(metrics.shoulder_rotation)
        hip_std = np.std(metrics.hip_rotation)
        knee_avg = np.mean(metrics.knee_flexion)
        velocity_smoothness = np.std(np.diff(metrics.velocity))
        
        if shoulder_std < 0.1:
            improvements.append(FeedbackItem(
                category="肩部动作",
                message="肩膀旋转幅度偏小，力量传递不充分",
                priority=FeedbackPriority.IMPORTANT,
                improvement_tip="尝试加大转肩幅度，像费德勒那样充分转肩准备"
            ))
        
        if hip_std < 0.08:
            improvements.append(FeedbackItem(
                category="髋部发力",
                message="髋部转动不足，未能充分利用下肢力量",
                priority=FeedbackPriority.IMPORTANT,
                improvement_tip="加强转髋练习，从下往上传递力量"
            ))
        
        if knee_avg < 120:
            improvements.append(FeedbackItem(
                category="膝盖姿势",
                message="膝盖弯曲度过大，影响移动效率",
                priority=FeedbackPriority.SUGGESTION,
                improvement_tip="保持膝盖微屈（约150度），既稳定又灵活"
            ))
        
        if velocity_smoothness > 0.3:
            improvements.append(FeedbackItem(
                category="动作连贯性",
                message="动作节奏不够流畅，忽快忽慢",
                priority=FeedbackPriority.SUGGESTION,
                improvement_tip="多做空拍练习，让动作更流畅自然"
            ))
        
        if len(improvements) == 0:
            improvements.append(FeedbackItem(
                category="整体表现",
                message="技术动作非常标准，继续保持！",
                priority=FeedbackPriority.POSITIVE,
                improvement_tip="可以尝试加快击球节奏，提高攻击性"
            ))
        
        summary = self._generate_summary(classification, quality_eval)
        exercises = self._generate_exercises(improvements, classification)
        
        return FeedbackReport(
            summary=summary,
            strengths=strengths,
            improvements=improvements,
            exercise_suggestions=exercises,
            overall_score=quality_eval["综合评分"]
        )
    
    def _generate_summary(self, classification: ClassificationResult, quality_eval: Dict) -> str:
        base_text = f"本次分析识别出动作类型为 {classification.motion_type.value}。"
        
        score = quality_eval["综合评分"]
        if score >= 90:
            return base_text + f"技术表现非常优秀（{score:.1f}/100），接近职业水平！"
        elif score >= 75:
            return base_text + f"技术表现良好（{score:.1f}/100），有几个细节可以优化。"
        elif score >= 60:
            return base_text + f"技术表现合格（{score:.1f}/100），需要加强基本动作练习。"
        else:
            return base_text + f"技术动作需要改进（{score:.1f}/100），建议从基础开始练习。"
    
    def _generate_exercises(self, improvements: List[FeedbackItem], 
                           classification: ClassificationResult) -> List[str]:
        exercises = []
        
        if classification.motion_type.value == "正手击球":
            exercises.append("正手多球训练：教练送球，连续20次正手击球")
            exercises.append("转肩练习：侧身站立，持拍做转肩动作")
        
        elif classification.motion_type.value == "反手击球":
            exercises.append("反手多球训练：连续20次反手击球")
            exercises.append("靠墙练习：背部靠墙，感受反手击球的身体转动")
        
        elif classification.motion_type.value == "发球":
            exercises.append("发球抛球练习：抛球100次，固定抛球位置")
            exercises.append("发球分解练习：分步骤练习发球动作")
        
        exercises.append("核心力量训练：平板支撑3组，每组60秒")
        exercises.append("柔韧性训练：肩部、髋部拉伸各5分钟")
        
        return exercises
