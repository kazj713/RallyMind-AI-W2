"""
Gunicorn 配置文件 - 生产环境
参考 FastAPI 官方部署最佳实践
"""

import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# 进程日志
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 进程命名
proc_name = "rallymind-ai-api"

# Worker 进程配置
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
graceful_timeout = 30
keepalive = 5

# 预加载应用（共享内存，减少内存使用）
preload_app = True

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 日志格式（包含响应时间）
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 服务器机制
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# 环境变量
raw_env = [
    'PYTHONUNBUFFERED=1',
]

def post_fork(server, worker):
    server.log.info(f"Worker {worker.pid} 启动")


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("主进程启动")


def when_ready(server):
    server.log.info("服务器已就绪")


def worker_int(worker):
    worker.log.info("Worker 收到 SIGINT/INT 信号")


def worker_abort(worker):
    worker.log.info("Worker 收到 SIGABRT 信号")
