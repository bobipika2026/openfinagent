#!/usr/bin/env python3
"""
OpenFinAgent API 服务启动脚本

使用方法:
    python run_api.py
    
或者使用 uvicorn 直接启动:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    print("🚀 启动 OpenFinAgent API 服务...")
    print("📖 API 文档：http://localhost:8000/api/docs")
    print("📖 ReDoc: http://localhost:8000/api/redoc")
    print("💡 按 Ctrl+C 停止服务")
    print("-" * 60)
    
    uvicorn.run(
        "__init__:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
