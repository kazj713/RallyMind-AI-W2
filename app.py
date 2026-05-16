import streamlit as st
import cv2
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from pose_analyzer import AdvancedPoseAnalyzer, MotionMetrics
from motion_classifier import TennisMotionClassifier
from feedback_generator import IntelligentFeedbackGenerator


st.set_page_config(
    page_title="🎾 RallyMind AI - 网球动作分析系统",
    page_icon="🎾",
    layout="wide"
)

st.title("🎾 RallyMind AI")
st.subheader("基于深度学习的智能网球动作分析系统")
st.markdown("---")


@st.cache_resource
def load_models():
    analyzer = AdvancedPoseAnalyzer()
    classifier = TennisMotionClassifier()
    feedback_gen = IntelligentFeedbackGenerator()
    return analyzer, classifier, feedback_gen


analyzer, classifier, feedback_gen = load_models()


col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 🎬 上传训练视频")
    uploaded_file = st.file_uploader(
        "上传你的网球训练视频",
        type=["mp4", "mov", "avi", "mkv"]
    )


with col2:
    st.markdown("### ⚙️ 分析设置")
    sample_rate = st.slider("采样率（越小越精确）", 1, 10, 2)


if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    
    st.success("✅ 视频上传成功！")
    st.video(tfile.name)
    st.markdown("---")
    
    with st.spinner("🤖 正在进行动作分析，请稍候..."):
        try:
            pose_frames, metrics, annotated_frames = analyzer.analyze_pose_sequence(
                tfile.name,
                sample_rate=sample_rate
            )
            
            features = analyzer.get_temporal_features(metrics)
            classification = classifier.classify(features)
            quality_eval = classifier.evaluate_motion_quality(metrics)
            feedback = feedback_gen.generate_feedback(
                classification,
                metrics, quality_eval
            )
            
        except Exception as e:
            st.error(f"分析出错: {str(e)}")
            st.stop()
        
        st.success("分析完成！")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 分析结果",
        "🎯 姿态可视化",
        "📈 动作指标",
        "📚 AI反馈报告"
    ])
    
    with tab1:
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric(
                "动作类型",
                classification.motion_type.value,
                f"{classification.sub_type}"
            )
            st.metric(
                "识别置信度",
                f"{classification.confidence:.1f}%"
            )
        
        with col_b:
            st.metric(
                "整体评分",
                f"{classification.quality_score:.1f}/100",
                f"{feedback.overall_score:.1f}"
            )
        
        with col_c:
            st.metric(
                "动作节奏",
                f"{quality_eval['动作节奏']:.1f}"
            )
            st.metric(
                "身体平衡",
                f"{quality_eval['身体平衡']:.1f}"
            )
        
        st.markdown("### 🎯 阶段分析")
        for phase, score in classification.phase_analysis.items():
            st.progress(score / 100)
            st.text(f"{phase}: {score:.1f}/100")
    
    with tab2:
        st.markdown("### 姿态检测预览")
        if len(annotated_frames) > 0:
            display_count = min(3 if len(annotated_frames) < 4 else 4)
            cols = st.columns(display_count)
            
            for i in range(display_count):
                idx = i * len(annotated_frames) // display_count
                frame = annotated_frames[idx]
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cols[i].image(frame_rgb, caption=f"第 {idx * sample_rate} 帧")
    
    with tab3:
        st.markdown("### 📈 动作指标曲线")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        axes[0, 0].plot(metrics.shoulder_rotation)
        axes[0, 0].set_title("肩部旋转变化")
        axes[0, 0].set_xlabel("帧索引")
        axes[0, 0].grid(True, alpha=0.3)
        
        axes[0, 1].plot(metrics.hip_rotation)
        axes[0, 1].set_title("髋部转动变化")
        axes[0, 1].set_xlabel("帧索引")
        axes[0, 1].grid(True, alpha=0.3)
        
        axes[1, 0].plot(metrics.knee_flexion)
        axes[1, 0].set_title("膝盖角度变化")
        axes[1, 0].set_xlabel("帧索引")
        axes[1, 0].grid(True, alpha=0.3)
        
        axes[1, 1].plot(metrics.velocity)
        axes[1, 1].set_title("动作速度变化")
        axes[1, 1].set_xlabel("帧索引")
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab4:
        st.markdown("### 📚 AI 智能反馈")
        
        st.success("### 📝 总结")
        st.write(feedback.summary)
        
        if feedback.strengths:
            st.markdown("### ✅ 优点")
            for strength in feedback.strengths:
                st.write(f"- {strength}")
        
        st.markdown("### 💡 改进建议")
        for item in feedback.improvements:
            priority_map = {
                "需要立即改进": "🔴",
                "重要改进项": "🟡",
                "建议优化": "🟢",
                "表现优秀": "✅"
            }
            emoji = priority_map.get(item.priority.value, "")
            with st.expander(f"{emoji} {item.category}: {item.message}"):
                st.write(f"**建议：** {item.improvement_tip}")
        
        st.markdown("### 🏋️ 训练建议")
        for exercise in feedback.exercise_suggestions:
            st.write(f"- {exercise}")


else:
    st.info("请上传网球训练视频以开始智能分析。")
    st.markdown("""
    ### 功能特点：
    - 🔹 基于深度学习的动作识别（LSTM+Attention架构）
    - 🔹 精准的人体姿态估计（MediaPipe）
    - 🔹 智能反馈系统（参考Hermes Agent设计理念）
    - 🔹 专业的技术评估和训练建议
    """)


st.markdown("---")
st.markdown("© 2024 RallyMind AI")
