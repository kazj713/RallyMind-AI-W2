"""
RallyMind AI - FastAPI 后端服务
生产级异步视频分析API
"""

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import uuid
import os
import shutil
from pathlib import Path
from enum import Enum

from pose_analyzer import AdvancedPoseAnalyzer, MotionMetrics
from motion_classifier import TennisMotionClassifier, ClassificationResult
from feedback_generator import IntelligentFeedbackGenerator


app = FastAPI(
    title="RallyMind AI API",
    description="智能网球动作分析系统 API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisTask(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    video_filename: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ClassificationResponse(BaseModel):
    motion_type: str
    confidence: float
    sub_type: str
    quality_score: float
    phase_analysis: Dict[str, float]


class QualityEvaluation(BaseModel):
    rhythm_score: float = Field(description="动作节奏评分")
    balance_score: float = Field(description="身体平衡评分")
    power_score: float = Field(description="发力效率评分")
    overall_score: float = Field(description="综合评分")


class FeedbackResponse(BaseModel):
    summary: str
    strengths: List[str]
    improvements: List[Dict[str, Any]]
    exercise_suggestions: List[str]
    overall_score: float


TASKS: Dict[str, AnalysisTask] = {}


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@app.get("/readiness")
async def readiness_check():
    """就绪检查端点"""
    try:
        classifier = TennisMotionClassifier()
        return {
            "status": "ready",
            "models_loaded": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"系统未就绪: {str(e)}")


@app.post("/upload", response_model=Dict[str, str])
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    上传网球训练视频并开始异步分析
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.mp4', '.mov', '.avi', '.mkv']:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}。支持的格式: mp4, mov, avi, mkv"
        )
    
    task_id = str(uuid.uuid4())
    video_filename = f"{task_id}{file_ext}"
    video_path = UPLOAD_DIR / video_filename
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    task = AnalysisTask(
        task_id=task_id,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        video_filename=file.filename
    )
    TASKS[task_id] = task
    
    background_tasks.add_task(process_video_task, task_id, video_path)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "视频上传成功，正在排队处理"
    }


def process_video_task(task_id: str, video_path: Path):
    """
    后台视频分析任务
    """
    asyncio.run(_process_video_async(task_id, video_path))


async def _process_video_async(task_id: str, video_path: Path):
    """
    异步执行视频分析
    """
    import numpy as np
    
    try:
        task = TASKS[task_id]
        task.status = TaskStatus.PROCESSING
        
        analyzer = AdvancedPoseAnalyzer()
        classifier = TennisMotionClassifier()
        feedback_gen = IntelligentFeedbackGenerator()
        
        pose_frames, metrics, annotated_frames = analyzer.analyze_pose_sequence(
            str(video_path),
            sample_rate=2
        )
        
        features = analyzer.get_temporal_features(metrics)
        classification = classifier.classify(features)
        quality_eval = classifier.evaluate_motion_quality(metrics)
        feedback = feedback_gen.generate_feedback(
            ClassificationResult(
                motion_type=classification.motion_type,
                confidence=classification.confidence,
                sub_type=classification.sub_type,
                quality_score=classification.quality_score,
                phase_analysis=classification.phase_analysis
            ),
            metrics,
            quality_eval
        )
        
        result = {
            "classification": {
                "motion_type": classification.motion_type.value,
                "confidence": classification.confidence,
                "sub_type": classification.sub_type,
                "quality_score": classification.quality_score,
                "phase_analysis": classification.phase_analysis
            },
            "quality_evaluation": quality_eval,
            "feedback": {
                "summary": feedback.summary,
                "strengths": feedback.strengths,
                "improvements": [
                    {
                        "category": imp.category,
                        "message": imp.message,
                        "priority": imp.priority.value,
                        "tip": imp.improvement_tip
                    }
                    for imp in feedback.improvements
                ],
                "exercise_suggestions": feedback.exercise_suggestions,
                "overall_score": feedback.overall_score
            },
            "metrics_summary": {
                "total_frames_analyzed": len(pose_frames),
                "avg_shoulder_rotation": float(np.mean(metrics.shoulder_rotation)),
                "avg_hip_rotation": float(np.mean(metrics.hip_rotation)),
                "avg_knee_flexion": float(np.mean(metrics.knee_flexion)),
                "avg_velocity": float(np.mean(metrics.velocity))
            }
        }
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
        
    except Exception as e:
        task = TASKS[task_id]
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        task.error = str(e)
    
    finally:
        if video_path.exists():
            os.remove(video_path)


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    查询任务状态
    """
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = TASKS[task_id]
    
    response = {
        "task_id": task.task_id,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "video_filename": task.video_filename
    }
    
    if task.completed_at:
        response["completed_at"] = task.completed_at.isoformat()
    
    if task.status == TaskStatus.COMPLETED and task.result:
        response["result"] = task.result
    
    if task.status == TaskStatus.FAILED and task.error:
        response["error"] = task.error
    
    return response


@app.get("/tasks")
async def list_tasks(
    status: Optional[TaskStatus] = None,
    limit: int = 10
):
    """
    列出所有任务
    """
    tasks = list(TASKS.values())
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "total": len(tasks),
        "tasks": [
            {
                "task_id": t.task_id,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "video_filename": t.video_filename
            }
            for t in tasks[:limit]
        ]
    }


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    """
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del TASKS[task_id]
    return {"message": "任务已删除"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
        loop="uvloop",
        http="httptools"
    )
