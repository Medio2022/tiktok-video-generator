"""
Videos API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import sys
import os
from pathlib import Path
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web_ui.database.db import create_video, get_all_videos, get_video
from main import TikTokPipeline
from modules.config_schemas import SubtitleConfig

router = APIRouter()



class VideoGenerateRequest(BaseModel):
    theme: str = "motivation"
    subtitle_color: Optional[str] = None # Deprecated, kept for backward compatibility
    subtitle_size: Optional[int] = None # Deprecated
    
    # Advanced Subtitle Config (New)
    subtitle_config: Optional[SubtitleConfig] = None

    # Avatar AI fields
    use_avatar: bool = False
    avatar_id: Optional[str] = "anna_casual_v2"
    voice_id: Optional[str] = "en-US-JennyNeural"
    aspect_ratio: str = "9:16"
    # ElevenLabs voice
    elevenlabs_voice: str = "rachel"

# Background task tracker
generation_status = {}

async def generate_video_task(
    request_id: str,
    theme: str,
    use_avatar: bool = False,
    avatar_id: str = "anna_casual_v2",
    voice_id: str = "en-US-JennyNeural",
    aspect_ratio: str = "9:16",
    elevenlabs_voice: str = "rachel",
    subtitle_config: Optional[SubtitleConfig] = None
):
    """Background task to generate video with progress updates"""
    try:
        generation_status[request_id] = {"status": "generating", "progress": 5, "message": "Initialisation du pipeline..."}
        
        # Initialize pipeline with avatar support
        pipeline = TikTokPipeline(
            theme=theme,
            use_avatar=use_avatar,
            avatar_id=avatar_id,
            voice_id=voice_id,
            aspect_ratio=aspect_ratio,
            elevenlabs_voice=elevenlabs_voice,
            subtitle_config=subtitle_config
        )
        
        # Step 1: Generate idea
        generation_status[request_id] = {"status": "generating", "progress": 10, "message": "Génération de l'idée virale..."}
        
        # Step 2: Generate script
        generation_status[request_id] = {"status": "generating", "progress": 25, "message": "Écriture du script..."}
        
        # Step 3: Generate voice / avatar
        if use_avatar:
            generation_status[request_id] = {"status": "generating", "progress": 40, "message": f"Génération avatar AI ({avatar_id})..."}
        else:
            generation_status[request_id] = {"status": "generating", "progress": 40, "message": "Génération de la voix off (Edge TTS)..."}
        
        # Step 4: Generate subtitles
        generation_status[request_id] = {"status": "generating", "progress": 55, "message": "Transcription Whisper..."}
        
        # Step 5: Get video background
        if use_avatar:
            generation_status[request_id] = {"status": "generating", "progress": 70, "message": "Création vidéo UGC avec avatar..."}
        else:
            generation_status[request_id] = {"status": "generating", "progress": 70, "message": "Téléchargement vidéo Pexels HD..."}
        
        # Step 6: Assemble video (this is the actual generation)
        generation_status[request_id] = {"status": "generating", "progress": 85, "message": "Assemblage vidéo complète..."}
        
        # Run synchronous pipeline in thread executor to avoid blocking
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            video_data = await loop.run_in_executor(pool, pipeline.generate_video)
        
        # Save to database
        generation_status[request_id] = {"status": "generating", "progress": 95, "message": "Finalisation..."}
        
        # Extract video info from pipeline metadata  
        video_path = str(video_data['video_path'])
        audio_duration = video_data.get('audio_duration', 0)
        
        # Count subtitles from SRT file
        subtitle_count = 0
        subtitle_path = video_data.get('subtitle_path')
        if subtitle_path and os.path.exists(subtitle_path):
            try:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count subtitle blocks (separated by double newlines)
                    subtitle_count = len([block for block in content.split('\n\n') if block.strip()])
            except:
                subtitle_count = 0
        
        video_id = create_video(
            filename=video_path,
            theme=theme,
            duration=audio_duration,
            subtitle_count=subtitle_count,
            metadata={
                "idea": video_data.get('idea'),
                "description": video_data.get('description'),
                "directory": str(video_data.get('output_dir', ''))
            }
        )
        
        generation_status[request_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Vidéo générée avec succès !",
            "video_id": video_id,
            "video_path": video_path,
            "duration": audio_duration,
            "subtitle_count": subtitle_count
        }
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        generation_status[request_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Erreur: {str(e)}"
        }
        print(f"Generation error: {error_detail}")  # Log for debugging

@router.get("")
async def list_videos():
    """Get all generated videos"""
    try:
        videos = get_all_videos()
        return {"success": True, "videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}")
async def get_video_details(video_id: int):
    """Get single video details"""
    try:
        video = get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"success": True, "video": video}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_video(request: VideoGenerateRequest, background_tasks: BackgroundTasks):
    """Generate new video"""
    try:
        import uuid
        request_id = str(uuid.uuid4())
        
        # Add task to background
        background_tasks.add_task(
            generate_video_task,
            request_id,
            request.theme,
            request.use_avatar,
            request.avatar_id,
            request.voice_id,
            request.aspect_ratio,
            request.elevenlabs_voice
        )
        
        return {
            "success": True,
            "message": "Video generation started",
            "request_id": request_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate/status/{request_id}")
async def get_generation_status(request_id: str):
    """Get generation status"""
    status = generation_status.get(request_id, {"status": "not_found"})
    return {"success": True, "status": status}

@router.get("/{video_id}/download")
@router.head("/{video_id}/download")
async def download_video(video_id: int, force_download: bool = False):
    """Download/stream video file with Range Request support"""
    from fastapi.responses import FileResponse, Response
    from fastapi import Request, Header
    from typing import Optional
    import os
    
    try:
        video = get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_path = Path(video['filename'])
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        # Generate a readable filename with theme and timestamp
        video_theme = video.get('theme', 'video')
        video_id_str = str(video_id)
        filename = f"tiktok_{video_theme}_{video_id_str}.mp4"
        
        # Determine headers based on intent
        if force_download:
            media_type = "application/octet-stream" # Force browser to save
            content_disposition = f'attachment; filename="{filename}"'
        else:
            media_type = "video/mp4" # Allow streaming
            content_disposition = f'inline; filename="{filename}"'

        # Use FileResponse with media_type for video streaming
        # FileResponse in FastAPI handles Range Requests automatically
        return FileResponse(
            path=str(video_path),
            media_type=media_type,
            filename=filename,
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-cache",
                "Content-Disposition": content_disposition
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}")
async def delete_video(video_id: int):
    """Delete video file and database record"""
    import os
    
    try:
        video = get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Delete video file if exists
        video_path = Path(video['filename'])
        if video_path.exists():
            try:
                os.remove(str(video_path))
                # Also try to delete the directory if it's empty
                if video_path.parent.exists() and not any(video_path.parent.iterdir()):
                    video_path.parent.rmdir()
            except Exception as e:
                print(f"Warning: Could not delete video file: {e}")
        
        # Delete from database
        from web_ui.database.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Video deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
