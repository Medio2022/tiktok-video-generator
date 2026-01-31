"""
Database models and operations using SQLite
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "tiktok_generator.db"

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Videos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            theme TEXT,
            duration REAL,
            subtitle_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published BOOLEAN DEFAULT 0,
            published_at TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # Schedule table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'pending',
            description TEXT,
            hashtags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(video_id) REFERENCES videos(id)
        )
    """)
    
    # Configuration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuration (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized: {DB_PATH}")

def get_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))

# Video operations
def create_video(filename: str, theme: str, duration: float, subtitle_count: int, metadata: dict) -> int:
    """Create new video record"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO videos (filename, theme, duration, subtitle_count, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, theme, duration, subtitle_count, json.dumps(metadata)))
    
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return video_id

def get_all_videos() -> List[Dict]:
    """Get all videos"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM videos ORDER BY created_at DESC
    """)
    
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Parse metadata JSON
    for video in videos:
        if video['metadata']:
            video['metadata'] = json.loads(video['metadata'])
    
    return videos

def get_video(video_id: int) -> Optional[Dict]:
    """Get single video by ID"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        video = dict(row)
        if video['metadata']:
            video['metadata'] = json.loads(video['metadata'])
        return video
    return None

def update_video_published(video_id: int):
    """Mark video as published"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE videos 
        SET published = 1, published_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (video_id,))
    
    conn.commit()
    conn.close()

# Schedule operations
def create_schedule(video_id: int, scheduled_time: str, description: str, hashtags: str) -> int:
    """Create new scheduled publication"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO schedule (video_id, scheduled_time, description, hashtags)
        VALUES (?, ?, ?, ?)
    """, (video_id, scheduled_time, description, hashtags))
    
    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return schedule_id

def get_all_schedules() -> List[Dict]:
    """Get all scheduled publications"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, v.filename, v.theme
        FROM schedule s
        LEFT JOIN videos v ON s.video_id = v.id
        ORDER BY s.scheduled_time ASC
    """)
    
    schedules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return schedules

def update_schedule_status(schedule_id: int, status: str):
    """Update schedule status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE schedule SET status = ? WHERE id = ?
    """, (status, schedule_id))
    
    conn.commit()
    conn.close()

def delete_schedule(schedule_id: int):
    """Delete scheduled publication"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM schedule WHERE id = ?", (schedule_id,))
    
    conn.commit()
    conn.close()

# Configuration operations
def set_config(key: str, value: str):
    """Set configuration value"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO configuration (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (key, value))
    
    conn.commit()
    conn.close()

def get_config(key: str) -> Optional[str]:
    """Get configuration value"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM configuration WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None

def get_all_config() -> Dict:
    """Get all configuration"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT key, value FROM configuration")
    config = {row['key']: row['value'] for row in cursor.fetchall()}
    conn.close()
    
    return config

# Initialize database on import
init_db()
