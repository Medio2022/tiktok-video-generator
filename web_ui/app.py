"""
FastAPI Web UI for TikTok Video Generator
Main application entry point
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import API routes
from api import config, videos, scheduler, tiktok, stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TikTok Video Generator",
    description="AI-powered TikTok video generation with Whisper, DeepSeek, and Edge TTS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Include API routers
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(scheduler.router, prefix="/api/schedule", tags=["Scheduler"])
app.include_router(tiktok.router, prefix="/api/tiktok", tags=["TikTok"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# WebSocket endpoint for live updates
@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now (will be implemented in video generation)
            await manager.send_personal_message({"status": "received", "data": data}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Root endpoint
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/generate")
async def generate_page(request: Request):
    return templates.TemplateResponse("generate.html", {"request": request})

@app.get("/config")
async def config_page(request: Request):
    return templates.TemplateResponse("config.html", {"request": request})

@app.get("/scheduler")
async def scheduler_page(request: Request):
    return templates.TemplateResponse("scheduler.html", {"request": request})

@app.get("/history")
async def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok", "message": "TikTok Video Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting TikTok Video Generator Web UI...")
    logger.info("📍 Dashboard: http://localhost:8000")
    logger.info("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "web_ui.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
