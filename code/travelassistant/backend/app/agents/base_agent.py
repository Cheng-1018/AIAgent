"""基础Agent类"""

from typing import Optional, Dict, Any
from app.services.llm_service import get_llm_service
from app.services.amap_service import get_amap_service


class BaseAgent:
    """Agent基类"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.llm_service = get_llm_service()
        
    async def execute(self, user_input: str) -> str:
        """执行Agent任务
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent响应
        """
        # 调用LLM获取响应
        response = await self.llm_service.chat(
            prompt=user_input,
            system_prompt=self.system_prompt
        )
        
        # 检查是否包含工具调用
        tool_call = await self.llm_service.parse_tool_call(response)
        if tool_call:
            # 执行工具调用
            tool_result = await self.execute_tool(tool_call)
            if tool_result:
                return tool_result
                
        return response
        
    async def execute_tool(self, tool_call: Dict[str, Any]) -> Optional[str]:
        """执行工具调用
        
        Args:
            tool_call: 工具调用信息
            
        Returns:
            工具执行结果
        """
        tool_name = tool_call.get("tool_name")
        params = tool_call.get("parameters", {})
        
        # 获取高德地图服务
        amap_service = await get_amap_service()
        
        try:
            if tool_name == "amap_maps_text_search":
                # POI搜索
                keywords = params.get("keywords", "")
                city = params.get("city", "")
                results = await amap_service.text_search(keywords, city)
                return str(results)
                
            elif tool_name == "amap_maps_weather":
                # 天气查询
                city = params.get("city", "")
                results = await amap_service.weather_query(city)
                return str(results)
                
            else:
                print(f"未知工具: {tool_name}")
                return None
        except Exception as e:
            print(f"工具执行失败: {e}")
            return None
