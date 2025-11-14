"""Unsplash图片服务"""

import httpx
from typing import Optional, List
from app.config import config


class UnsplashService:
    """Unsplash图片服务"""
    
    def __init__(self):
        self.access_key = config.UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com"
        
    async def search_photos(
        self, 
        query: str, 
        per_page: int = 5,
        orientation: str = "landscape"
    ) -> List[str]:
        """搜索图片
        
        Args:
            query: 搜索关键词
            per_page: 每页数量
            orientation: 方向(landscape/portrait/squarish)
            
        Returns:
            图片URL列表
        """
        # 如果没有配置API密钥，直接返回空列表
        if not self.access_key or self.access_key == "your_unsplash_access_key":
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/photos",
                    params={
                        "query": query,
                        "per_page": per_page,
                        "orientation": orientation,
                        "client_id": self.access_key
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    return [photo["urls"]["regular"] for photo in results if "urls" in photo]
                elif response.status_code == 403:
                    # API密钥无效或权限不足，静默失败
                    return []
                else:
                    print(f"Unsplash API错误: {response.status_code}")
                    return []
        except Exception as e:
            # 网络错误等，静默失败
            return []
            
    async def get_photo_for_attraction(self, attraction_name: str, city: str = "") -> Optional[str]:
        """获取景点图片
        
        Args:
            attraction_name: 景点名称
            city: 城市名称
            
        Returns:
            图片URL
        """
        query = f"{city} {attraction_name}" if city else attraction_name
        photos = await self.search_photos(query, per_page=1)
        return photos[0] if photos else None


# 全局服务实例
_unsplash_service: Optional[UnsplashService] = None


def get_unsplash_service() -> UnsplashService:
    """获取Unsplash服务实例"""
    global _unsplash_service
    if _unsplash_service is None:
        _unsplash_service = UnsplashService()
    return _unsplash_service
