"""POI相关API路由"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import POISearchRequest, POISearchResponse, POIInfo, Location
from app.services.amap_service import get_amap_service

router = APIRouter()


@router.post("/poi/search", response_model=POISearchResponse)
async def search_poi(request: POISearchRequest):
    """搜索POI
    
    Args:
        request: POI搜索请求
        
    Returns:
        POI搜索响应
    """
    try:
        amap_service = await get_amap_service()
        
        # 搜索POI
        pois = await amap_service.text_search(
            keywords=request.keywords,
            city=request.city,
            citylimit=request.citylimit
        )
        
        # 转换为响应格式
        poi_list = []
        for poi in pois:
            location_str = poi.get("location", "")
            if location_str and "," in location_str:
                lng, lat = location_str.split(",")
                location = Location(longitude=float(lng), latitude=float(lat))
            else:
                location = Location(longitude=0, latitude=0)
                
            poi_info = POIInfo(
                id=poi.get("id", ""),
                name=poi.get("name", ""),
                type=poi.get("type", ""),
                address=poi.get("address", ""),
                location=location,
                tel=poi.get("tel", None)
            )
            poi_list.append(poi_info)
        
        return POISearchResponse(
            success=True,
            message="搜索成功",
            data=poi_list
        )
    except Exception as e:
        print(f"POI搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"POI搜索失败: {str(e)}")
