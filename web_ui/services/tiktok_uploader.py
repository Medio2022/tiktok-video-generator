"""TikTok Uploader Service using Playwright"""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logger = logging.getLogger(__name__)


class TikTokUploader:
    """Upload videos to TikTok using Playwright automation"""
    
    def __init__(self, username: str, password: str, headless: bool = True):
        """
        Initialize TikTok uploader
        
        Args:
            username: TikTok username or email
            password: TikTok password
            headless: Run browser in headless mode
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def init_browser(self):
        """Initialize Playwright browser"""
        logger.info("🌐 Initializing browser...")
        
        playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Create context with realistic user agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Remove automation indicators
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        logger.info("✅ Browser initialized")
        
    async def login(self) -> bool:
        """
        Login to TikTok
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("🔐 Logging in to TikTok...")
            
            # Navigate to TikTok login
            await self.page.goto('https://www.tiktok.com/login/phone-or-email/email')
            await asyncio.sleep(2)
            
            # Fill username
            username_input = await self.page.wait_for_selector('input[name="username"]', timeout=10000)
            await username_input.fill(self.username)
            await asyncio.sleep(0.5)
            
            # Fill password
            password_input = await self.page.wait_for_selector('input[type="password"]', timeout=10000)
            await password_input.fill(self.password)
            await asyncio.sleep(0.5)
            
            # Click login button
            login_button = await self.page.wait_for_selector('button[type="submit"]', timeout=10000)
            await login_button.click()
            
            # Wait for navigation (or CAPTCHA/2FA)
            await asyncio.sleep(5)
            
            # Check if logged in (look for upload button or profile)
            current_url = self.page.url
            
            if 'login' not in current_url.lower():
                logger.info("✅ Login successful")
                return True
            else:
                logger.warning("⚠️ Login may require manual intervention (CAPTCHA/2FA)")
                # Wait longer for manual intervention
                await asyncio.sleep(30)
                return 'login' not in self.page.url.lower()
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
            
    async def upload_video(
        self, 
        video_path: str | Path,
        description: str,
        hashtags: str,
        privacy: str = "public",
        dry_run: bool = False
    ) -> dict:
        """
        Upload video to TikTok
        
        Args:
            video_path: Path to video file
            description: Video description
            hashtags: Hashtags (with #)
            privacy: Privacy setting (public, friends, private)
            dry_run: If True, don't actually publish
            
        Returns:
            Result dict with status, message, video_url
        """
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                return {"status": "error", "message": f"Video file not found: {video_path}"}
            
            logger.info(f"📤 Uploading video: {video_path.name}")
            
            # Navigate to upload page
            await self.page.goto('https://www.tiktok.com/upload')
            await asyncio.sleep(3)
            
            # Upload file
            logger.info("📁 Selecting video file...")
            file_input = await self.page.wait_for_selector('input[type="file"]', timeout=10000)
            await file_input.set_input_files(str(video_path))
            
            # Wait for upload to complete
            logger.info("⏳ Waiting for video to process...")
            await asyncio.sleep(10)
            
            # Fill caption (description + hashtags)
            full_caption = f"{description}\n\n{hashtags}"
            logger.info(f"✍️ Adding caption ({len(full_caption)} chars)...")
            
            caption_editor = await self.page.wait_for_selector(
                'div[contenteditable="true"]',
                timeout=10000
            )
            await caption_editor.fill(full_caption)
            await asyncio.sleep(1)
            
            # Set privacy (if selector exists)
            try:
                privacy_button = await self.page.wait_for_selector(
                    f'text={privacy.capitalize()}',
                    timeout=5000
                )
                await privacy_button.click()
                await asyncio.sleep(0.5)
            except:
                logger.warning(f"⚠️ Could not set privacy to {privacy}, using default")
            
            if dry_run:
                logger.info("🧪 Dry run mode - not publishing")
                return {
                    "status": "success",
                    "message": "Dry run completed",
                    "video_url": None
                }
            
            # Click Post button
            logger.info("🚀 Publishing video...")
            post_button = await self.page.wait_for_selector(
                'button:has-text("Post")',
                timeout=10000
            )
            await post_button.click()
            
            # Wait for upload to complete
            await asyncio.sleep(15)
            
            # Try to get video URL (if redirected)
            video_url = self.page.url if 'tiktok.com/@' in self.page.url else None
            
            logger.info("✅ Video published successfully!")
            
            return {
                "status": "success",
                "message": "Video published to TikTok",
                "video_url": video_url
            }
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "video_url": None
            }
            
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("🔒 Browser closed")


async def upload_to_tiktok(
    video_path: str,
    description: str,
    hashtags: str,
    username: str,
    password: str,
    privacy: str = "public",
    headless: bool = True,
    dry_run: bool = False
) -> dict:
    """
    Convenience function to upload video to TikTok
    
    Args:
        video_path: Path to video file
        description: Video description
        hashtags: Hashtags
        username: TikTok username
        password: TikTok password
        privacy: Privacy setting
        headless: Run browser in headless mode
        dry_run: Test mode without publishing
        
    Returns:
        Result dict
    """
    uploader = TikTokUploader(username, password, headless)
    
    try:
        await uploader.init_browser()
        
        logged_in = await uploader.login()
        if not logged_in:
            return {"status": "error", "message": "Login failed"}
        
        result = await uploader.upload_video(
            video_path=video_path,
            description=description,
            hashtags=hashtags,
            privacy=privacy,
            dry_run=dry_run
        )
        
        return result
        
    finally:
        await uploader.close()
