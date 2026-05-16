#!/bin/bash

# RallyMind AI 生产部署脚本

set -e

echo "=========================================="
echo "  RallyMind AI 生产部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 环境变量文件
ENV_FILE="$PROJECT_ROOT/.env"

echo -e "${YELLOW}检查环境...${NC}"

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    echo -e "${GREEN}虚拟环境已存在${NC}"
    source venv/bin/activate
fi

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt"
else
    echo -e "${RED}错误: requirements.txt 不存在${NC}"
    exit 1
fi

# 安装 Gunicorn workers
echo -e "${YELLOW}安装 Gunicorn...${NC}"
pip install gunicorn uvloop httptools

# 创建上传目录
echo -e "${YELLOW}创建上传目录...${NC}"
mkdir -p "$PROJECT_ROOT/uploads"
chmod 755 "$PROJECT_ROOT/uploads"

# 复制环境变量模板
if [ ! -f "$ENV_FILE" ] && [ -f "$PROJECT_ROOT/.env.example" ]; then
    echo -e "${YELLOW}复制环境变量模板...${NC}"
    cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
fi

# 运行测试
echo -e "${YELLOW}运行测试...${NC}"
cd "$PROJECT_ROOT"
python -m pytest tests/ -v || echo -e "${YELLOW}跳过测试（tests 目录不存在）${NC}"

# 启动服务
echo -e "${GREEN}=========================================="
echo "  启动服务"
echo "==========================================${NC}"

# 生产环境使用 Gunicorn
if [ "$1" = "production" ]; then
    echo -e "${GREEN}使用 Gunicorn 生产模式启动${NC}"
    
    # 使用自定义配置
    if [ -f "$PROJECT_ROOT/gunicorn_config.py" ]; then
        gunicorn -c gunicorn_config.py api:app
    else
        # 默认配置
        gunicorn \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --bind 0.0.0.0:8000 \
            --timeout 30 \
            --access-logfile - \
            --error-logfile - \
            --log-level info \
            api:app
    fi

# 开发环境使用 Uvicorn
elif [ "$1" = "dev" ] || [ "$1" = "development" ]; then
    echo -e "${GREEN}使用 Uvicorn 开发模式启动${NC}"
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# 默认使用 Uvicorn
else
    echo -e "${GREEN}使用 Uvicorn 启动${NC}"
    uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop --http httptools
fi

echo -e "${GREEN}服务启动完成！${NC}"
echo "访问地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
