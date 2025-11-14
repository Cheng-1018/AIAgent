"""FastAPI主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from app.config import config
from app.api.routes import trip, poi, map as map_route


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("智能旅行助手服务启动...")
    
    yield
    
    # 关闭时
    print("智能旅行助手服务关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="智能旅行助手",
    description="基于LLM和MCP的智能旅行规划助手",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查路由
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "travel-assistant"}

# 注册路由
app.include_router(trip.router, prefix="/api", tags=["旅行规划"])
app.include_router(poi.router, prefix="/api", tags=["POI搜索"])
app.include_router(map_route.router, prefix="/api", tags=["地图服务"])

# 静态文件服务（前端）
frontend_dir = Path(__file__).parent.parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="static")
