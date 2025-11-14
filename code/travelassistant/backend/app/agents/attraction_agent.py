"""景点搜索AGENT"""

from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.config import config
from app.services.amap_service import get_amap_service
from app.services.unsplash_service import get_unsplash_service


class AttractionAgent(BaseAgent):
    """景点搜索Agent"""
    
    def __init__(self):
        super().__init__(
            name="AttractionAgent",
            system_prompt=config.ATTRACTION_AGENT_PROMPT
        )
        
    async def search_attractions(
        self, 
        city: str, 
        preferences: List[str],
        num_attractions: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索景点
        
        Args:
            city: 城市名称
            preferences: 用户偏好列表
            num_attractions: 返回景点数量
            
        Returns:
            景点列表
        """
        amap_service = await get_amap_service()
        unsplash_service = get_unsplash_service()
        
        all_attractions = []
        
        # 根据偏好搜索不同类型的景点
        preference_keywords = {
            "历史文化": ["博物馆", "历史", "文化", "古迹", "名胜"],
            "自然风光": ["公园", "山", "湖", "风景区", "自然"],
            "美食": ["美食街", "小吃", "餐厅"],
            "购物": ["商场", "购物中心", "商业街"],
            "艺术": ["艺术馆", "美术馆", "画廊", "艺术中心"],
            "休闲": ["公园", "广场", "休闲"]
        }
        
        # 如果没有偏好，搜索通用景点
        if not preferences:
            keywords = "景点"
            results = await amap_service.text_search(keywords, city)
            all_attractions.extend(results)
        else:
            # 根据偏好搜索
            for pref in preferences:
                keywords_list = preference_keywords.get(pref, [pref])
                for keyword in keywords_list[:2]:  # 限制每个偏好的关键词数量
                    results = await amap_service.text_search(keyword, city)
                    all_attractions.extend(results[:5])  # 每个关键词最多5个结果
                    
        # 去重（基于名称）
        seen_names = set()
        unique_attractions = []
        for attr in all_attractions:
            name = attr.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                unique_attractions.append(attr)
                
        # 限制数量
        attractions = unique_attractions[:num_attractions]
        
        # 为每个景点获取图片
        for attraction in attractions:
            name = attraction.get("name", "")
            if name:
                image_url = await unsplash_service.get_photo_for_attraction(name, city)
                attraction["image_url"] = image_url
                
        return attractions
