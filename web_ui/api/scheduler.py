"""
Scheduler API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web_ui.database.db import create_schedule, get_all_schedules, update_schedule_status, delete_schedule

router = APIRouter()

class ScheduleCreate(BaseModel):
    video_id: int
    scheduled_time: str  # ISO format
    description: str
    hashtags: str

class ScheduleUpdate(BaseModel):
    status: str

@router.get("")
async def list_schedules():
    """Get all scheduled publications"""
    try:
        schedules = get_all_schedules()
        return {"success": True, "schedules": schedules, "count": len(schedules)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_schedule_job(schedule: ScheduleCreate):
    """Create new scheduled publication"""
    try:
        schedule_id = create_schedule(
            video_id=schedule.video_id,
            scheduled_time=schedule.scheduled_time,
            description=schedule.description,
            hashtags=schedule.hashtags
        )
        
        return {
            "success": True,
            "message": "Publication scheduled",
            "schedule_id": schedule_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{schedule_id}")
async def update_schedule(schedule_id: int, update: ScheduleUpdate):
    """Update schedule status"""
    try:
        update_schedule_status(schedule_id, update.status)
        return {"success": True, "message": "Schedule updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{schedule_id}")
async def delete_schedule_job(schedule_id: int):
    """Delete scheduled publication"""
    try:
        delete_schedule(schedule_id)
        return {"success": True, "message": "Schedule deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
