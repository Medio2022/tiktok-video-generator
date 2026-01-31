import sys
import os
from pathlib import Path
import inspect

sys.path.insert(0, str(Path.cwd()))

try:
    from main import TikTokPipeline
    print(f"✅ Loaded TikTokPipeline from: {sys.modules['main'].__file__}")
    
    sig = inspect.signature(TikTokPipeline.__init__)
    print(f"📝 Signature: {sig}")
    
    if 'subtitle_config' in sig.parameters:
        print("✅ subtitle_config IS present in __init__")
    else:
        print("❌ subtitle_config is MISSING from __init__")
        
except Exception as e:
    print(f"❌ Error importing: {e}")
