"""天气查询AGENT"""

from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.config import config
from app.services.amap_service import get_amap_service
from app.models.schemas import WeatherInfo


class WeatherAgent(BaseAgent):
    """天气查询Agent"""
    
    def __init__(self):
        super().__init__(
            name="WeatherAgent",
            system_prompt=config.WEATHER_AGENT_PROMPT
        )
        
    async def query_weather(self, city: str, dates: List[str]) -> List[WeatherInfo]:
        """查询天气
        
        Args:
            city: 城市名称
            dates: 日期列表 (YYYY-MM-DD)
            
        Returns:
            天气信息列表
        """
        amap_service = await get_amap_service()
        
        # 查询天气
        weather_data = await amap_service.weather_query(city)
        
        weather_info_list = []
        
        # 将天气数据映射到指定日期
        for i, date in enumerate(dates):
            if i < len(weather_data):
                weather = weather_data[i]
                weather_info = WeatherInfo(
                    date=date,
                    day_weather=weather.get("dayweather", ""),
                    night_weather=weather.get("nightweather", ""),
                    day_temp=weather.get("daytemp", 0),
                    night_temp=weather.get("nighttemp", 0),
                    wind_direction=weather.get("daywind", ""),
                    wind_power=weather.get("daypower", "")
                )
            else:
                # 如果天气数据不足，使用默认值
                weather_info = WeatherInfo(
                    date=date,
                    day_weather="未知",
                    night_weather="未知",
                    day_temp=20,
                    night_temp=10,
                    wind_direction="无持续风向",
                    wind_power="微风"
                )
            weather_info_list.append(weather_info)
            
        return weather_info_list
