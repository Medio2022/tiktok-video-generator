"""
Configuration API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web_ui.database.db import set_config, get_config, get_all_config
import config as app_config

router = APIRouter()

class ConfigUpdate(BaseModel):
    deepseek_api_key: Optional[str] = None
    pexels_api_key: Optional[str] = None
    theme: Optional[str] = None
    subtitle_color: Optional[str] = None
    subtitle_size: Optional[int] = None
    tiktok_username: Optional[str] = None
    tiktok_password: Optional[str] = None

@router.get("")
async def get_configuration():
    """Get current configuration"""
    try:
        # Get from database or defaults
        config_data = {
            "deepseek_api_key": get_config("deepseek_api_key") or "***",
            "pexels_api_key": get_config("pexels_api_key") or "***",
            "theme": get_config("theme") or app_config.THEME,
            "subtitle_color": get_config("subtitle_color") or str(app_config.SUBTITLE_CONFIG.get("color")),
            "subtitle_size": int(get_config("subtitle_size") or app_config.SUBTITLE_CONFIG.get("size", 85)),
            "tiktok_username": get_config("tiktok_username") or "***",
            "tiktok_password": "***",  # Never return actual password
        }
        
        return {"success": True, "config": config_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def update_configuration(config: ConfigUpdate):
    """Update configuration"""
    try:
        updates = {}
        
        if config.deepseek_api_key:
            set_config("deepseek_api_key", config.deepseek_api_key)
            updates["deepseek_api_key"] = "updated"
        
        if config.pexels_api_key:
            set_config("pexels_api_key", config.pexels_api_key)
            updates["pexels_api_key"] = "updated"
        
        if config.theme:
            set_config("theme", config.theme)
            updates["theme"] = config.theme
        
        if config.subtitle_color:
            set_config("subtitle_color", config.subtitle_color)
            updates["subtitle_color"] = config.subtitle_color
        
        if config.subtitle_size:
            set_config("subtitle_size", str(config.subtitle_size))
            updates["subtitle_size"] = config.subtitle_size
        
        if config.tiktok_username:
            set_config("tiktok_username", config.tiktok_username)
            updates["tiktok_username"] = "updated"
        
        if config.tiktok_password:
            set_config("tiktok_password", config.tiktok_password)
            updates["tiktok_password"] = "updated"
        
        return {"success": True, "message": "Configuration updated", "updates": updates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_api_keys():
    """Test API keys validity"""
    results = {}
    
    # Test DeepSeek
    deepseek_key = get_config("deepseek_api_key")
    if deepseek_key:
        try:
            # Simple validation (could add actual API test)
            results["deepseek"] = {"status": "valid" if len(deepseek_key) > 10 else "invalid"}
        except:
            results["deepseek"] = {"status": "error"}
    else:
        results["deepseek"] = {"status": "missing"}
    
    # Test Pexels
    pexels_key = get_config("pexels_api_key")
    if pexels_key:
        results["pexels"] = {"status": "valid" if len(pexels_key) > 10 else "invalid"}
    else:
        results["pexels"] = {"status": "missing"}
    
    return {"success": True, "results": results}
