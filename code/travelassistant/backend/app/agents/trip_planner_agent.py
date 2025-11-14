"""行程规划AGENT"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.agents.base_agent import BaseAgent
from app.agents.attraction_agent import AttractionAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.hotel_agent import HotelAgent
from app.config import config
from app.models.schemas import (
    TripPlan, DayPlan, Attraction, Meal, Budget, 
    Location, WeatherInfo, Hotel
)


class TripPlannerAgent(BaseAgent):
    """行程规划Agent"""
    
    def __init__(self):
        super().__init__(
            name="TripPlannerAgent",
            system_prompt=config.PLANNER_AGENT_PROMPT
        )
        self.attraction_agent = AttractionAgent()
        self.weather_agent = WeatherAgent()
        self.hotel_agent = HotelAgent()
        
    async def plan_trip(
        self, 
        city: str,
        start_date: str,
        end_date: str,
        travel_days: int,
        transportation: str,
        accommodation: str,
        preferences: List[str],
        free_text_input: str = ""
    ) -> TripPlan:
        """规划行程
        
        Args:
            city: 城市名称
            start_date: 开始日期
            end_date: 结束日期
            travel_days: 旅行天数
            transportation: 交通方式
            accommodation: 住宿偏好
            preferences: 兴趣偏好
            free_text_input: 额外要求
            
        Returns:
            旅行计划
        """
        # 1. 搜索景点
        attractions_data = await self.attraction_agent.search_attractions(
            city=city,
            preferences=preferences,
            num_attractions=travel_days * 3  # 每天计划3个景点
        )
        
        # 2. 查询天气
        dates = self._generate_dates(start_date, travel_days)
        weather_info = await self.weather_agent.query_weather(city, dates)
        
        # 3. 推荐酒店
        hotels = await self.hotel_agent.recommend_hotels(
            city=city,
            accommodation=accommodation,
            num_hotels=travel_days
        )
        
        # 4. 生成每日行程
        days = []
        total_attractions_cost = 0
        total_hotels_cost = 0
        total_meals_cost = 0
        
        for day_index in range(travel_days):
            date = dates[day_index]
            
            # 为当天选择景点
            start_idx = day_index * 3
            end_idx = start_idx + 3
            day_attractions_data = attractions_data[start_idx:end_idx]
            
            # 转换景点数据
            day_attractions = []
            for attr_data in day_attractions_data:
                location_str = attr_data.get("location", "")
                if location_str and "," in location_str:
                    lng, lat = location_str.split(",")
                    location = Location(longitude=float(lng), latitude=float(lat))
                else:
                    location = Location(longitude=0, latitude=0)
                
                # 根据景点类型设置门票价格
                ticket_price = self._estimate_ticket_price(attr_data.get("type", ""))
                
                attraction = Attraction(
                    name=attr_data.get("name", ""),
                    address=attr_data.get("address", ""),
                    location=location,
                    visit_duration=120,  # 默认2小时
                    description=attr_data.get("name", ""),
                    category=attr_data.get("type", "景点"),
                    image_url=attr_data.get("image_url"),
                    ticket_price=ticket_price
                )
                day_attractions.append(attraction)
                total_attractions_cost += ticket_price
            
            # 餐饮安排
            meals = [
                Meal(
                    type="breakfast",
                    name=f"{city}特色早餐",
                    description="当地特色早餐",
                    estimated_cost=30
                ),
                Meal(
                    type="lunch",
                    name=f"{city}特色午餐",
                    description="品尝当地美食",
                    estimated_cost=60
                ),
                Meal(
                    type="dinner",
                    name=f"{city}特色晚餐",
                    description="享受当地特色晚餐",
                    estimated_cost=80
                )
            ]
            total_meals_cost += sum(meal.estimated_cost for meal in meals)
            
            # 酒店
            hotel = hotels[day_index] if day_index < len(hotels) else None
            if hotel:
                total_hotels_cost += hotel.estimated_cost
            
            # 生成当日描述
            description = f"第{day_index + 1}天: 游览{', '.join([a.name for a in day_attractions])}"
            
            day_plan = DayPlan(
                date=date,
                day_index=day_index,
                description=description,
                transportation=transportation,
                accommodation=accommodation,
                hotel=hotel,
                attractions=day_attractions,
                meals=meals
            )
            days.append(day_plan)
        
        # 5. 预算估算
        total_transportation = self._estimate_transportation_cost(
            travel_days, 
            transportation
        )
        
        budget = Budget(
            total_attractions=total_attractions_cost,
            total_hotels=total_hotels_cost,
            total_meals=total_meals_cost,
            total_transportation=total_transportation,
            total=total_attractions_cost + total_hotels_cost + total_meals_cost + total_transportation
        )
        
        # 6. 生成总体建议
        suggestions = self._generate_suggestions(
            city=city,
            weather_info=weather_info,
            preferences=preferences,
            free_text_input=free_text_input
        )
        
        # 7. 返回完整计划
        trip_plan = TripPlan(
            city=city,
            start_date=start_date,
            end_date=end_date,
            days=days,
            weather_info=weather_info,
            overall_suggestions=suggestions,
            budget=budget
        )
        
        return trip_plan
    
    def _generate_dates(self, start_date: str, days: int) -> List[str]:
        """生成日期列表"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    
    def _estimate_ticket_price(self, poi_type: str) -> int:
        """估算门票价格"""
        price_map = {
            "风景名胜": 80,
            "公园广场": 0,
            "博物馆": 40,
            "游乐园": 150,
            "动物园": 100,
            "植物园": 50,
            "寺庙": 20,
            "教堂": 0,
            "商场": 0,
        }
        return price_map.get(poi_type, 60)
    
    def _estimate_transportation_cost(self, days: int, transportation: str) -> int:
        """估算交通费用"""
        daily_cost_map = {
            "公共交通": 50,
            "自驾": 100,
            "步行": 0,
            "混合": 70
        }
        daily_cost = daily_cost_map.get(transportation, 50)
        return daily_cost * days
    
    def _generate_suggestions(
        self,
        city: str,
        weather_info: List[WeatherInfo],
        preferences: List[str],
        free_text_input: str
    ) -> str:
        """生成旅行建议"""
        suggestions = [f"欢迎来到{city}！以下是为您准备的旅行建议："]
        
        # 天气建议
        if weather_info:
            first_weather = weather_info[0]
            suggestions.append(f"近期天气{first_weather.day_weather}，建议携带合适的衣物。")
        
        # 偏好建议
        if "历史文化" in preferences:
            suggestions.append("您对历史文化感兴趣，建议安排充足时间游览博物馆和古迹。")
        if "美食" in preferences:
            suggestions.append("别忘了品尝当地特色美食，可以向当地人咨询推荐。")
        if "自然风光" in preferences:
            suggestions.append("自然景观最佳观赏时间通常在早晨和傍晚。")
        
        # 其他建议
        suggestions.append("建议提前预订热门景点门票，避免排队等候。")
        suggestions.append("注意保管好个人财物，祝您旅途愉快！")
        
        # 额外要求
        if free_text_input:
            suggestions.append(f"根据您的要求：{free_text_input}")
        
        return "\n".join(suggestions)
