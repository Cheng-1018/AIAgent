"""LLM服务模块"""

import json
from typing import Optional, Dict, Any
from openai import OpenAI
from app.config import config


class LLMService:
    """LLM服务"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )
        self.model = config.LLM_MODEL_ID
        
    async def chat(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """调用LLM进行对话
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            LLM响应文本
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return ""
            
    async def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取JSON
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            解析后的JSON对象
        """
        try:
            # 尝试直接解析
            return json.loads(text)
        except:
            pass
            
        try:
            # 提取```json...```之间的内容
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
        except:
            pass
            
        try:
            # 提取{...}之间的内容
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
            
        return None
        
    async def parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """解析工具调用
        
        格式: [TOOL_CALL:tool_name:param1=value1,param2=value2]
        
        Args:
            text: 包含工具调用的文本
            
        Returns:
            工具调用信息
        """
        try:
            if "[TOOL_CALL:" not in text:
                return None
                
            start = text.find("[TOOL_CALL:") + 11
            end = text.find("]", start)
            if end == -1:
                return None
                
            call_str = text[start:end]
            parts = call_str.split(":", 1)
            if len(parts) != 2:
                return None
                
            tool_name = parts[0].strip()
            params_str = parts[1].strip()
            
            # 解析参数
            params = {}
            if params_str:
                for param in params_str.split(","):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key.strip()] = value.strip()
                        
            return {
                "tool_name": tool_name,
                "parameters": params
            }
        except Exception as e:
            print(f"工具调用解析失败: {e}")
            return None


# 全局服务实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
