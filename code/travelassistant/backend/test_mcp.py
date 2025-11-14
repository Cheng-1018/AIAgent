"""测试MCP连接"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp():
    """测试MCP连接"""
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-gdmaps",
            "d81b6b372fc32ebc932a3d8509eab323"
        ]
    )
    
    print("正在连接MCP服务器...")
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("stdio_client连接成功")
            
            async with ClientSession(read_stream, write_stream) as session:
                print("ClientSession创建成功")
                
                # 初始化会话
                await session.initialize()
                print("会话初始化成功")
                
                # 测试调用工具
                print("\n测试POI搜索...")
                result = await session.call_tool(
                    "amap_maps_text_search",
                    arguments={
                        "keywords": "景点",
                        "city": "北京",
                        "citylimit": "true"
                    }
                )
                
                print(f"调用结果: {result}")
                
                if result and result.content:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"响应内容: {content.text[:200]}...")
                            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

"""测试高德地图服务"""

import asyncio
import json
from app.services.amap_service import AmapMCPService


async def test():
    """测试POI搜索"""
    service = AmapMCPService()
    
    print("=== 测试POI搜索 ===")
    result = await service.text_search("公园", "北京")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    
    print("\n=== 测试天气查询 ===")
    weather = await service.weather_query("北京")
    print(json.dumps(weather, ensure_ascii=False, indent=2))
    
    with open ("test_poi_search_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        json.dump(weather, f, ensure_ascii=False, indent=2)

'''测试景点搜索agent'''

from app.agents.attraction_agent import AttractionAgent

AttractionAgent=AttractionAgent()
async def test():
    """测试景点搜索agent"""
    query = "推荐几个北京的著名景点"
    print(f"用户查询: {query}")
    
    response = await AttractionAgent.execute(query)
    with open("test_poi_search_result.jsonl", "a", encoding="utf-8") as f:
        f.write(response)

# if __name__ == "__main__":
#     asyncio.run(test())



