"""地图服务API路由"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    RouteRequest, RouteResponse, RouteInfo,
    WeatherResponse, WeatherInfo
)
from app.services.amap_service import get_amap_service

router = APIRouter()


@router.post("/route", response_model=RouteResponse)
async def plan_route(request: RouteRequest):
    """规划路线
    
    Args:
        request: 路线规划请求
        
    Returns:
        路线规划响应
    """
    try:
        amap_service = await get_amap_service()
        
        # 规划路线
        route = await amap_service.route_plan(
            origin=request.origin_address,
            destination=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type
        )
        
        if route:
            # 解析路线信息（简化版）
            route_info = RouteInfo(
                distance=float(route.get("distance", 0)),
                duration=int(route.get("duration", 0)),
                route_type=request.route_type,
                description="路线规划成功"
            )
            
            return RouteResponse(
                success=True,
                message="路线规划成功",
                data=route_info
            )
        else:
            return RouteResponse(
                success=False,
                message="路线规划失败"
            )
    except Exception as e:
        print(f"路线规划失败: {e}")
        raise HTTPException(status_code=500, detail=f"路线规划失败: {str(e)}")


@router.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str):
    """查询天气
    
    Args:
        city: 城市名称
        
    Returns:
        天气查询响应
    """
    try:
        amap_service = await get_amap_service()
        
        # 查询天气
        weather_data = await amap_service.weather_query(city)
        
        weather_list = []
        for weather in weather_data:
            weather_info = WeatherInfo(
                date=weather.get("date", ""),
                day_weather=weather.get("dayweather", ""),
                night_weather=weather.get("nightweather", ""),
                day_temp=weather.get("daytemp", 0),
                night_temp=weather.get("nighttemp", 0),
                wind_direction=weather.get("daywind", ""),
                wind_power=weather.get("daypower", "")
            )
            weather_list.append(weather_info)
        
        return WeatherResponse(
            success=True,
            message="天气查询成功",
            data=weather_list
        )
    except Exception as e:
        print(f"天气查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"天气查询失败: {str(e)}")
