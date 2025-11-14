"""酒店推荐AGENT"""

from typing import List, Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.config import config
from app.services.amap_service import get_amap_service
from app.models.schemas import Hotel, Location


class HotelAgent(BaseAgent):
    """酒店推荐Agent"""
    
    def __init__(self):
        super().__init__(
            name="HotelAgent",
            system_prompt=config.HOTEL_AGENT_PROMPT
        )
        
    async def recommend_hotels(
        self, 
        city: str, 
        accommodation: str,
        num_hotels: int = 5
    ) -> List[Hotel]:
        """推荐酒店
        
        Args:
            city: 城市名称
            accommodation: 住宿类型偏好
            num_hotels: 推荐数量
            
        Returns:
            酒店列表
        """
        amap_service = await get_amap_service()
        
        # 根据住宿类型选择搜索关键词
        keywords_map = {
            "经济型酒店": "经济型酒店",
            "舒适型酒店": "酒店",
            "豪华酒店": "五星级酒店",
            "民宿": "民宿"
        }
        
        keywords = keywords_map.get(accommodation, "酒店")
        
        # 搜索酒店
        hotels_data = await amap_service.text_search(keywords, city)
        
        hotels = []
        
        # 根据住宿偏好设置价格范围和类型
        price_ranges = {
            "经济型酒店": ("150-300元", 200),
            "舒适型酒店": ("300-500元", 400),
            "豪华酒店": ("800-2000元", 1200),
            "民宿": ("200-400元", 300)
        }
        
        price_range, estimated_cost = price_ranges.get(accommodation, ("300-500元", 400))
        
        for hotel_data in hotels_data[:num_hotels]:
            location_str = hotel_data.get("location", "")
            if location_str and "," in location_str:
                lng, lat = location_str.split(",")
                location = Location(longitude=float(lng), latitude=float(lat))
            else:
                location = None
                
            hotel = Hotel(
                name=hotel_data.get("name", ""),
                address=hotel_data.get("address", ""),
                location=location,
                price_range=price_range,
                rating="4.5",
                distance="市中心",
                type=accommodation,
                estimated_cost=estimated_cost
            )
            hotels.append(hotel)
            
        return hotels
