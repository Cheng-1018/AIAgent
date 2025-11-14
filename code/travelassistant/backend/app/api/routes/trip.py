"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import TripRequest, TripPlanResponse
from app.agents.trip_planner_agent import TripPlannerAgent

router = APIRouter()


@router.post("/plan", response_model=TripPlanResponse)
async def plan_trip(request: TripRequest):
    """规划旅行
    
    Args:
        request: 旅行规划请求
        
    Returns:
        旅行计划响应
    """
    try:
        # 创建行程规划Agent
        planner = TripPlannerAgent()
        
        # 规划行程
        trip_plan = await planner.plan_trip(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            travel_days=request.travel_days,
            transportation=request.transportation,
            accommodation=request.accommodation,
            preferences=request.preferences,
            free_text_input=request.free_text_input or ""
        )
        
        return TripPlanResponse(
            success=True,
            message="行程规划成功",
            data=trip_plan
        )
    except Exception as e:
        print(f"行程规划失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"行程规划失败: {str(e)}")

from fastapi import APIRouter, HTTPException
from app.models.schemas import TripRequest, TripPlanResponse
from app.agents.trip_planner_agent import TripPlannerAgent

router = APIRouter()


@router.post("/plan", response_model=TripPlanResponse)
async def plan_trip(request: TripRequest):
    """规划旅行行程
    
    Args:
        request: 旅行规划请求
        
    Returns:
        旅行计划响应
    """
    try:
        # 创建行程规划Agent
        planner = TripPlannerAgent()
        
        # 规划行程
        trip_plan = await planner.plan_trip(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            travel_days=request.travel_days,
            transportation=request.transportation,
            accommodation=request.accommodation,
            preferences=request.preferences,
            free_text_input=request.free_text_input or ""
        )
        
        return TripPlanResponse(
            success=True,
            message="行程规划成功",
            data=trip_plan
        )
    except Exception as e:
        print(f"行程规划失败: {e}")
        raise HTTPException(status_code=500, detail=f"行程规划失败: {str(e)}")
