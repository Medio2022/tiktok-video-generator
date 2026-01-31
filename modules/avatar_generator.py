"""
Avatar Video Generator using HeyGen API
Generates realistic AI spokesperson videos with lip-sync
"""

import requests
import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AvatarVideoGenerator:
    """Generate videos with AI avatars using HeyGen API"""
    
    def __init__(self):
        self.api_key = os.getenv('HEYGEN_API_KEY')
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY not found in environment variables")
        
        self.base_url = 'https://api.heygen.com/v2'
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_avatar_video(
        self,
        script: str,
        avatar_id: str = "default",
        voice_id: str = "en-US-JennyNeural",
        background_color: str = "#FFFFFF",
        aspect_ratio: str = "9:16"
    ) -> str:
        """
        Create a video with AI avatar speaking the script
        
        Args:
            script: Text for the avatar to speak
            avatar_id: HeyGen avatar identifier
            voice_id: Voice identifier from HeyGen
            background_color: Hex color for background
            aspect_ratio: Video aspect ratio (9:16, 16:9, 1:1)
        
        Returns:
            str: URL of the generated video
        
        Raises:
            Exception: If video generation fails
        """
        logger.info(f"Creating avatar video with avatar={avatar_id}, voice={voice_id}")
        
        # Determine dimensions based on aspect ratio
        dimensions = self._get_dimensions(aspect_ratio)
        
        endpoint = f"{self.base_url}/video/generate"
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id
                },
                "background": {
                    "type": "color",
                    "value": background_color
                }
            }],
            "dimension": dimensions,
            "aspect_ratio": aspect_ratio,
            "test": False  # Set to True for testing (watermarked)
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            video_id = data['data']['video_id']
            
            logger.info(f"Video generation started. Video ID: {video_id}")
            
            # Wait for video to be ready
            video_url = self._wait_for_video(video_id)
            
            logger.info(f"Video generation completed: {video_url}")
            return video_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HeyGen API error: {e}")
            raise Exception(f"Failed to generate avatar video: {str(e)}")
    
    def _wait_for_video(self, video_id: str, max_wait: int = 300) -> str:
        """
        Poll HeyGen API until video is ready
        
        Args:
            video_id: HeyGen video identifier
            max_wait: Maximum seconds to wait
        
        Returns:
            str: URL of completed video
        """
        endpoint = f"{self.base_url}/video/{video_id}"
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait:
                raise TimeoutError(f"Video generation timed out after {max_wait}s")
            
            try:
                response = requests.get(endpoint, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()['data']
                status = data['status']
                
                if status == 'completed':
                    return data['video_url']
                elif status == 'failed':
                    error = data.get('error', 'Unknown error')
                    raise Exception(f"Video generation failed: {error}")
                
                # Status is 'processing' or 'pending'
                logger.debug(f"Video {video_id} status: {status}")
                time.sleep(5)  # Check every 5 seconds
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking video status: {e}")
                time.sleep(5)
    
    def download_video(self, video_url: str, output_path: str) -> Path:
        """
        Download generated video to local file
        
        Args:
            video_url: URL of the video to download
            output_path: Local path to save video
        
        Returns:
            Path: Path to downloaded video
        """
        logger.info(f"Downloading video from {video_url}")
        
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Video downloaded to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise
    
    def _get_dimensions(self, aspect_ratio: str) -> Dict[str, int]:
        """Get video dimensions based on aspect ratio"""
        dimensions_map = {
            "9:16": {"width": 1080, "height": 1920},  # TikTok/Reels
            "16:9": {"width": 1920, "height": 1080},  # YouTube
            "1:1": {"width": 1080, "height": 1080}    # Instagram
        }
        return dimensions_map.get(aspect_ratio, dimensions_map["9:16"])
    
    def list_available_avatars(self) -> list:
        """
        Get list of available avatars from HeyGen
        
        Returns:
            list: Available avatar configurations
        """
        # This would call HeyGen API to get available avatars
        # For now, return predefined list
        return AVAILABLE_AVATARS
    
    def list_available_voices(self) -> list:
        """
        Get list of available voices from HeyGen
        
        Returns:
            list: Available voice configurations
        """
        return AVAILABLE_VOICES


# Predefined avatars (curated selection)
AVAILABLE_AVATARS = [
    {
        "id": "anna_casual_v2",
        "name": "Anna",
        "description": "Casual, friendly young woman",
        "gender": "female",
        "age_range": "25-35",
        "style": "casual",
        "preview_image": "/static/avatars/anna.jpg"
    },
    {
        "id": "john_professional_v2",
        "name": "John",
        "description": "Professional businessman",
        "gender": "male",
        "age_range": "35-45",
        "style": "professional",
        "preview_image": "/static/avatars/john.jpg"
    },
    {
        "id": "sarah_friendly_v2",
        "name": "Sarah",
        "description": "Friendly and energetic",
        "gender": "female",
        "age_range": "20-30",
        "style": "energetic",
        "preview_image": "/static/avatars/sarah.jpg"
    },
    {
        "id": "marcus_tech_v2",
        "name": "Marcus",
        "description": "Tech-savvy presenter",
        "gender": "male",
        "age_range": "25-35",
        "style": "tech",
        "preview_image": "/static/avatars/marcus.jpg"
    },
    {
        "id": "lisa_beauty_v2",
        "name": "Lisa",
        "description": "Beauty and lifestyle",
        "gender": "female",
        "age_range": "25-35",
        "style": "beauty",
        "preview_image": "/static/avatars/lisa.jpg"
    }
]

# Predefined voices
AVAILABLE_VOICES = [
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (US Female)",
        "language": "English (US)",
        "gender": "female",
        "style": "friendly"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (US Male)",
        "language": "English (US)",
        "gender": "male",
        "style": "professional"
    },
    {
        "id": "en-GB-LibbyNeural",
        "name": "Libby (UK Female)",
        "language": "English (UK)",
        "gender": "female",
        "style": "elegant"
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria (US Female)",
        "language": "English (US)",
        "gender": "female",
        "style": "energetic"
    },
    {
        "id": "en-US-DavisNeural",
        "name": "Davis (US Male)",
        "language": "English (US)",
        "gender": "male",
        "style": "casual"
    }
]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    generator = AvatarVideoGenerator()
    
    test_script = """
    Hey there! Today I want to share an amazing product with you.
    This product has completely changed my daily routine.
    If you're looking for quality and value, this is exactly what you need.
    Check the link in my bio to get yours today!
    """
    
    try:
        video_url = generator.create_avatar_video(
            script=test_script,
            avatar_id="anna_casual_v2",
            voice_id="en-US-JennyNeural"
        )
        
        print(f"Video generated successfully: {video_url}")
        
        # Download video
        output_path = "test_avatar_video.mp4"
        generator.download_video(video_url, output_path)
        print(f"Video saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
