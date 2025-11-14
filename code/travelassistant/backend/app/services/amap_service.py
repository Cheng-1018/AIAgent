"""高德地图服务封装 - 直接HTTP API调用"""

import json
import httpx
from typing import List, Dict, Any, Optional
from app.config import config


class AmapMCPService:
    """高德地图服务 - 使用HTTP API"""
    
    def __init__(self):
        self.api_key = config.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
        
    async def text_search(self, keywords: str, city: str, citylimit: bool = True) -> List[Dict[str, Any]]:
        """文本搜索POI
        
        Args:
            keywords: 搜索关键词
            city: 城市名称
            citylimit: 是否限制在城市范围内
            
        Returns:
            POI列表
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/place/text",
                    params={
                        "key": self.api_key,
                        "keywords": keywords,
                        "city": city,
                        "citylimit": str(citylimit).lower(),
                        "output": "json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        return data.get("pois", [])
                    else:
                        print(f"高德API错误: {data.get('info')}")
            return []
        except Exception as e:
            print(f"POI搜索失败: {e}")
            return []
            
    async def weather_query(self, city: str) -> List[Dict[str, Any]]:
        """查询天气
        
        Args:
            city: 城市名称
            
        Returns:
            天气信息列表
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/weather/weatherInfo",
                    params={
                        "key": self.api_key,
                        "city": city,
                        "extensions": "all",
                        "output": "json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        forecasts = data.get("forecasts", [])
                        if forecasts:
                            return forecasts[0].get("casts", [])
                    else:
                        print(f"高德API错误: {data.get('info')}")
            return []
        except Exception as e:
            print(f"天气查询失败: {e}")
            return []
            
    async def geocode(self, address: str, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """地理编码(地址转坐标)
        
        Args:
            address: 地址
            city: 城市(可选)
            
        Returns:
            地理编码结果
        """
        try:
            params = {
                "key": self.api_key,
                "address": address,
                "output": "json"
            }
            if city:
                params["city"] = city
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/geocode/geo",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        geocodes = data.get("geocodes", [])
                        if geocodes:
                            return geocodes[0]
                    else:
                        print(f"高德API错误: {data.get('info')}")
            return None
        except Exception as e:
            print(f"地理编码失败: {e}")
            return None
            
    async def route_plan(
        self, 
        origin: str, 
        destination: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Optional[Dict[str, Any]]:
        """路线规划
        
        Args:
            origin: 起点地址
            destination: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型(walking/driving/transit)
            
        Returns:
            路线规划结果
        """
        try:
            # 先进行地理编码
            origin_geo = await self.geocode(origin, origin_city)
            dest_geo = await self.geocode(destination, destination_city)
            
            if not origin_geo or not dest_geo:
                return None
                
            origin_location = origin_geo.get("location")
            dest_location = dest_geo.get("location")
            
            # 调用路线规划API
            api_map = {
                "walking": "walking",
                "driving": "driving",
                "transit": "integrated"
            }
            
            api_type = api_map.get(route_type, "walking")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                if api_type == "walking":
                    response = await client.get(
                        f"{self.base_url}/direction/walking",
                        params={
                            "key": self.api_key,
                            "origin": origin_location,
                            "destination": dest_location,
                            "output": "json"
                        }
                    )
                elif api_type == "driving":
                    response = await client.get(
                        f"{self.base_url}/direction/driving",
                        params={
                            "key": self.api_key,
                            "origin": origin_location,
                            "destination": dest_location,
                            "output": "json"
                        }
                    )
                else:  # transit
                    response = await client.get(
                        f"{self.base_url}/direction/transit/integrated",
                        params={
                            "key": self.api_key,
                            "origin": origin_location,
                            "destination": dest_location,
                            "city": destination_city or origin_city,
                            "output": "json"
                        }
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        return data.get("route", {})
                    else:
                        print(f"高德API错误: {data.get('info')}")
                        
            return None
        except Exception as e:
            print(f"路线规划失败: {e}")
            return None


# 全局服务实例
_amap_service: Optional[AmapMCPService] = None


async def get_amap_service() -> AmapMCPService:
    """获取高德地图服务实例"""
    global _amap_service
    if _amap_service is None:
        _amap_service = AmapMCPService()
    return _amap_service

