# RallyMind AI - 智能网球动作分析系统

## 项目说明

这是一个基于深度学习的智能网球动作分析系统，参考 NousResearch Hermes Agent 的设计理念实现。

## 核心功能

### 1. 高级姿态识别
* MediaPipe 人体33个关键点识别
* 精准的肩膀、髋部、膝盖、肘部角度计算
* 时序动作特征提取

### 2. 深度学习动作分类
* LSTM + Attention 架构
* 7种网球动作类型识别：正手、反手、发球、截击、高压球等
* 动作质量自动评分
* 阶段分析（准备、击球、随挥）

### 3. 智能 AI 反馈系统
* 优点分析与改进建议
* 分优先级反馈（🔴紧急、🟡重要、🟢建议）
* 个性化训练建议
* 基于运动生物力学的专业评估

### 4. Streamlit 可视化界面
* 视频上传与播放
* 姿态可视化预览
* 动作指标曲线图（肩部、髋部、膝盖、速度）
* 完整的 AI 分析报告

## 技术栈

| 模块 | 技术 |
| --- | --- |
| Web 框架 | Streamlit |
| 姿态识别 | MediaPipe Pose |
| 视觉处理 | OpenCV |
| 深度学习 | PyTorch |
| 机器学习 | scikit-learn, transformers |
| 数据分析 | NumPy, Pandas, Matplotlib |

## 安装与运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行应用
streamlit run app.py
```

## 项目结构

```
/workspace/
├── app.py                  # 主应用入口
├── pose_analyzer.py        # 高级姿态分析引擎
├── motion_classifier.py    # 深度学习动作分类器
├── feedback_generator.py   # 智能反馈系统
├── requirements.txt        # Python 依赖
├── test_system.py          # 系统测试脚本
└── README.md               # 项目文档
```

## 使用说明

1. 启动应用后，在浏览器中访问 `http://localhost:8501`
2. 上传你的网球训练视频（支持 mp4, mov, avi, mkv 格式）
3. 调整采样率参数（越小越精确，处理时间越长）
4. 等待 AI 分析完成
5. 查看四个标签页的完整分析报告：
   - 📊 分析结果：动作类型、评分、置信度
   - 🎯 姿态可视化：带关键点标注的帧
   - 📈 动作指标：时序曲线图
   - 📚 AI 反馈报告：完整的改进建议和训练计划

## 核心改进（v2.0）

参考 Hermes Agent 的设计理念进行了全面升级：

1. **从规则到深度学习**：简单的肩膀距离判断 → 基于 LSTM+Attention 的时序分类
2. **智能反馈系统**：固定提示 → 基于知识库和动作质量的个性化反馈
3. **多维度分析**：单一指标 → 肩、髋、膝、肘、速度、重心等综合评估
4. **可视化增强**：基础预览 → 带曲线图和分阶段分析的专业界面

## 许可证

Apache 2.0 License
