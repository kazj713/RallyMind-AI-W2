import numpy as np


print("=== 验证系统模块导入 ===")
try:
    from pose_analyzer import AdvancedPoseAnalyzer, MotionMetrics
    print("✅ pose_analyzer 模块导入成功")
except Exception as e:
    print(f"❌ pose_analyzer 导入失败: {e}")


try:
    from motion_classifier import TennisMotionClassifier
    print("✅ motion_classifier 模块导入成功")
except Exception as e:
    print(f"❌ motion_classifier 导入失败: {e}")


try:
    from feedback_generator import IntelligentFeedbackGenerator
    print("✅ feedback_generator 模块导入成功")
except Exception as e:
    print(f"❌ feedback_generator 导入失败: {e}")


print("\n=== 测试分类器 ===")
try:
    classifier = TennisMotionClassifier()
    features = np.random.randn(300)
    result = classifier.classify(features)
    print(f"✅ 分类器测试成功")
    print(f"   - 动作类型: {result.motion_type.value}")
    print(f"   - 置信度: {result.confidence:.2f}")
    print(f"   - 质量评分: {result.quality_score:.1f}")
except Exception as e:
    print(f"❌ 分类器测试失败: {e}")
    import traceback
    traceback.print_exc()


print("\n=== 测试反馈生成器 ===")
try:
    feedback_gen = IntelligentFeedbackGenerator()
    mock_metrics = MotionMetrics(
        shoulder_rotation=[0.1, 0.2, 0.15, 0.25],
        hip_rotation=[0.05, 0.1, 0.08, 0.12],
        knee_flexion=[140, 150, 145, 155],
        elbow_angle=[90, 100, 95, 105],
        wrist_position=[(0.5, 0.5), (0.6, 0.4), (0.55, 0.45), (0.58, 0.48)],
        center_of_gravity=[(0.5, 0.6), (0.52, 0.62), (0.51, 0.61), (0.53, 0.63)],
        velocity=[0.1, 0.2, 0.15, 0.22]
    )
    
    mock_classification = classifier.classify(features)
    mock_quality = classifier.evaluate_motion_quality(mock_metrics)
    feedback = feedback_gen.generate_feedback(
        mock_classification, mock_metrics, mock_quality
    )
    
    print("✅ 反馈生成器测试成功")
    print(f"   - 总结: {feedback.summary}")
    print(f"   - 整体评分: {feedback.overall_score:.1f}")
    print(f"   - 优点数量: {len(feedback.strengths)}")
    print(f"   - 改进建议: {len(feedback.improvements)}")
    print(f"   - 训练建议: {len(feedback.exercise_suggestions)}")
    
except Exception as e:
    print(f"❌ 反馈生成器测试失败: {e}")
    import traceback
    traceback.print_exc()


print("\n=== 完整测试完成 ===")
