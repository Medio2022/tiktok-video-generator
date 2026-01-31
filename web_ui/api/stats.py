"""
Stats API endpoints for dashboard
"""

from fastapi import APIRouter, HTTPException
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web_ui.database.db import get_connection

router = APIRouter()

@router.get("")
async def get_stats():
    """Get dashboard statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total videos
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        
        # Published videos
        cursor.execute("SELECT COUNT(*) FROM videos WHERE published = 1")
        published_count = cursor.fetchone()[0]
        
        # Scheduled publications
        cursor.execute("SELECT COUNT(*) FROM schedule WHERE status = 'pending'")
        scheduled_count = cursor.fetchone()[0]
        
        # Recent videos (last 5)
        cursor.execute("""
            SELECT id, filename, theme, duration, created_at, published
            FROM videos
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        recent_videos = []
        for row in cursor.fetchall():
            recent_videos.append({
                "id": row[0],
                "filename": row[1],
                "theme": row[2],
                "duration": row[3],
                "created_at": row[4],
                "published": bool(row[5])
            })
        
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_videos": total_videos,
                "published_count": published_count,
                "scheduled_count": scheduled_count,
                "recent_videos": recent_videos
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
