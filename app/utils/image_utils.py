"""Image utility functions for thumbnail generation."""

from typing import Optional
from PIL import Image
import io


class ThumbnailCache:
    """Cache for generated thumbnails."""
    
    def __init__(self):
        """Initialize thumbnail cache."""
        self.cache: dict = {}
    
    def getThumbnail(self, filePath: str, size: int) -> Optional[bytes]:
        """
        Get thumbnail from cache or generate it.
        
        Args:
            filePath: Path to image file
            size: Thumbnail size in pixels
            
        Returns:
            Thumbnail image bytes (PNG format) or None
        """
        cacheKey = f"{filePath}:{size}"
        
        if cacheKey in self.cache:
            return self.cache[cacheKey]
        
        thumbnail = self._generateThumbnail(filePath, size)
        if thumbnail:
            self.cache[cacheKey] = thumbnail
        
        return thumbnail
    
    def _generateThumbnail(self, filePath: str, size: int) -> Optional[bytes]:
        """
        Generate thumbnail from image file.
        
        Args:
            filePath: Path to image file
            size: Thumbnail size in pixels
            
        Returns:
            Thumbnail image bytes (PNG format) or None
        """
        try:
            image = Image.open(filePath)
            image.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()
        
        except Exception:
            return None
    
    def clearCache(self):
        """Clear the thumbnail cache."""
        self.cache.clear()
    
    def invalidateFile(self, filePath: str):
        """
        Invalidate cache for a specific file.
        
        Args:
            filePath: Path to file to invalidate
        """
        keysToRemove = [key for key in self.cache.keys() if key.startswith(f"{filePath}:")]
        for key in keysToRemove:
            del self.cache[key]


# Global thumbnail cache instance
thumbnailCache = ThumbnailCache()

