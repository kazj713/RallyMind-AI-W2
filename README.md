# RallyMind AI - 智能网球动作分析系统

## 项目说明

这是一个基于深度学习的智能网球动作分析系统，参考 NousResearch Hermes Agent 的设计理念实现，采用 FastAPI 生产级框架部署。

## 技术架构

### 核心模块

#### 1. 高级姿态识别 (`pose_analyzer.py`)
* MediaPipe 人体33个关键点识别
* 3D 角度计算（肩膀、髋部、膝盖、肘部）
* 时序动作特征提取

#### 2. 深度学习动作分类 (`motion_classifier.py`)
* LSTM + Attention 架构（PyTorch）
* 7种网球动作类型识别
* 动作质量自动评分

#### 3. 智能 AI 反馈系统 (`feedback_generator.py`)
* 分优先级反馈机制
* 个性化训练建议
* 运动生物力学分析

#### 4. FastAPI 生产级后端 (`api.py`)
* RESTful API 设计
* 异步任务队列
* 实时任务状态轮询
* 健康检查和就绪检查

## 生产级特性

### FastAPI 生产部署最佳实践

1. **多 Worker 架构**
   - Gunicorn + Uvicorn Workers
   - CPU 核心数 × 2 + 1 workers
   - 自动 worker 重启防止内存泄漏

2. **异步任务处理**
   - BackgroundTasks 处理视频分析
   - 非阻塞 I/O 操作
   - 任务状态实时跟踪

3. **安全配置**
   - CORS 中间件
   - 输入验证（Pydantic）
   - 文件类型检查

4. **性能优化**
   - uvloop 事件循环
   - httptools HTTP 解析
   - Keep-Alive 连接复用

5. **监控和日志**
   - 健康检查端点
   - 访问日志（包含响应时间）
   - 错误追踪

## 安装与运行

### 方式一：快速启动（开发环境）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（Uvicorn）
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 方式二：生产环境（Gunicorn）

```bash
# 使用部署脚本
chmod +x deploy.sh
./deploy.sh production
```

或手动启动：

```bash
# 安装 Gunicorn
pip install gunicorn

# 使用配置文件启动
gunicorn -c gunicorn_config.py api:app
```

## API 端点

### 健康检查

```bash
# 健康检查
GET /health

# 就绪检查
GET /readiness
```

### 视频分析

```bash
# 上传视频
POST /upload
Content-Type: multipart/form-data

# 查询任务状态
GET /tasks/{task_id}

# 列出所有任务
GET /tasks?status=completed&limit=10

# 删除任务
DELETE /tasks/{task_id}
```

### API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 前端界面

打开 `frontend/index.html` 文件即可使用现代美观的前端界面。

### 前端特性
- 拖拽上传
- 实时进度条
- 任务状态轮询
- 美观的分析报告展示
- 响应式设计

## 项目结构

```
/workspace/
├── api.py                    # FastAPI 后端服务
├── pose_analyzer.py          # 高级姿态分析引擎
├── motion_classifier.py      # 深度学习动作分类器
├── feedback_generator.py      # 智能反馈系统
├── gunicorn_config.py        # Gunicorn 生产配置
├── deploy.sh                 # 部署脚本
├── requirements.txt          # Python 依赖
├── frontend/
│   └── index.html           # 前端界面
├── test_api.py              # API 测试脚本
├── test_system.py           # 系统测试脚本
└── README.md                # 项目文档
```

## 核心改进（v2.0）

参考 Hermes Agent 和 FastAPI 生产部署最佳实践：

1. **从 Streamlit 到 FastAPI**：交互式原型 → 生产级 API 服务
2. **深度学习集成**：规则判断 → LSTM+Attention 神经网络
3. **异步任务队列**：同步处理 → BackgroundTasks 异步分析
4. **多 Worker 部署**：单进程 → Gunicorn 多进程架构
5. **智能反馈系统**：固定提示 → 基于知识库的个性化建议

## 技术栈

| 模块 | 技术 |
| --- | --- |
| Web 框架 | FastAPI + Uvicorn + Gunicorn |
| 姿态识别 | MediaPipe Pose |
| 深度学习 | PyTorch (LSTM + Attention) |
| 机器学习 | scikit-learn |
| 数据处理 | NumPy, Pandas |
| 前端 | HTML5 + JavaScript (原生) |

## 许可证

Apache 2.0 License

---

**参考来源**：
- [FastAPI 生产部署最佳实践](https://render.com/articles/fastapi-production-deployment-best-practices)
- [NousResearch Hermes Agent v2026.5.7](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.5.7)
- [Celery 视频处理架构](https://mixpeek.com/blog/using-celery-to-process-thousands-of-videos)
