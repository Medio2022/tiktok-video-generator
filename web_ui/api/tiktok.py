"""
TikTok publication API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web_ui.database.db import update_video_published, create_schedule, get_video
from web_ui.services.tiktok_uploader import upload_to_tiktok

router = APIRouter()

# Publication status tracking
publication_status = {}

class PublishRequest(BaseModel):
    video_id: int
    description: str
    hashtags: str
    privacy: str = "public"  # public, friends, private
    publish_now: bool = True
    scheduled_time: str = None

async def publish_video_task(video_id: int, video_path: str, description: str, hashtags: str, privacy: str):
    """Background task to publish video to TikTok"""
    try:
        publication_status[video_id] = {"status": "uploading", "progress": 10, "message": "Initialisation..."}
        
        # Get TikTok credentials from env
        username = os.getenv("TIKTOK_USERNAME")
        password = os.getenv("TIKTOK_PASSWORD")
        
        if not username or not password:
            publication_status[video_id] = {
                "status": "error",
                "progress": 0,
                "message": "TikTok credentials not configured"
            }
            return
        
        publication_status[video_id] = {"status": "uploading", "progress": 30, "message": "Connexion à TikTok..."}
        
        # Upload video
        result = await upload_to_tiktok(
            video_path=video_path,
            description=description,
            hashtags=hashtags,
            username=username,
            password=password,
            privacy=privacy,
            headless=False,  # Show browser for debugging
            dry_run=False
        )
        
        if result["status"] == "success":
            publication_status[video_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Vidéo publiée avec succès !",
                "video_url": result.get("video_url")
            }
            
            # Update database
            update_video_published(video_id)
        else:
            publication_status[video_id] = {
                "status": "error",
                "progress": 0,
                "message": f"Erreur: {result.get('message')}"
            }
            
    except Exception as e:
        publication_status[video_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Erreur: {str(e)}"
        }

@router.post("/publish")
async def publish_video(request: PublishRequest, background_tasks: BackgroundTasks):
    """Publish video to TikTok"""
    try:
        # Get video details
        video_data = get_video(request.video_id)
        if not video_data["success"]:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video = video_data["video"]
        video_path = video["filename"]
        
        if not Path(video_path).exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        if request.publish_now:
            # Immediate publication (background task)
            background_tasks.add_task(
                publish_video_task,
                request.video_id,
                video_path,
                request.description,
                request.hashtags,
                request.privacy
            )
            
            publication_status[request.video_id] = {
                "status": "uploading",
                "progress": 5,
                "message": "Démarrage de la publication..."
            }
            
            return {
                "success": True,
                "message": "Publication démarrée",
                "video_id": request.video_id
            }
        else:
            # Schedule for later
            if not request.scheduled_time:
                raise HTTPException(status_code=400, detail="scheduled_time required")
            
            schedule_id = create_schedule(
                video_id=request.video_id,
                scheduled_time=request.scheduled_time,
                description=request.description,
                hashtags=request.hashtags
            )
            
            return {
                "success": True,
                "message": "Video scheduled for publication",
                "schedule_id": schedule_id
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/publish/status/{video_id}")
async def get_publish_status(video_id: int):
    """Get publication status"""
    try:
        status = publication_status.get(video_id, {
            "status": "not_started",
            "progress": 0,
            "message": "Publication non démarrée"
        })
        
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{video_id}")
async def get_publish_status_legacy(video_id: int):
    """Legacy endpoint - redirects to /publish/status"""
    return await get_publish_status(video_id)
