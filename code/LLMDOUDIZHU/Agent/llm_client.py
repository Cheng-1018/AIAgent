import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
from utils import logger
# 加载 .env 文件中的环境变量
load_dotenv()

class AgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0, show_thinking: bool = True) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            show_thinking: 是否显示thinking过程（对于thinking模型）
        """
        # print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=False,
                timeout=60
            )
            
            # 处理非流式响应
            choice = response.choices[0]
            content = choice.message.content or ""
            
            # 处理thinking内容（如果模型支持）
            thinking_content = ""
            if hasattr(choice.message, 'reasoning_content') and choice.message.reasoning_content:
                thinking_content = choice.message.reasoning_content
                # if show_thinking:
                #     logger.info(f"\n💭 Thinking过程:")
                #     logger.info(f"\033[90m{thinking_content}\033[0m")
                #     logger.info("\n📝 最终输出:")
            
            # 输出最终内容
            # logger.info(content)
            
            # 输出token使用统计
            # if thinking_content:
            #     logger.info(f"\n💭 Thinking tokens: ~{len(thinking_content)} chars")
            #     logger.info(f"📝 Output tokens: ~{len(content)} chars")
            
            return content

        except Exception as e:
            logger.error(f"❌ 调用LLM API时发生错误: {e}")
            return None

    def think_streaming(self, messages: List[Dict[str, str]], temperature: float = 0, show_thinking: bool = True) -> str:
        """
        调用大语言模型进行思考，使用流式输出，并打印思考内容和最终内容。
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            show_thinking: 是否显示thinking过程（对于thinking模型）
        """
        # print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
                timeout=60
            )
            
            full_content = ""
            thinking_content = ""
            
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    
                    # 处理thinking内容
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        thinking_content += delta.reasoning_content
                        if show_thinking:
                            print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                    
                    # 处理最终内容
                    if delta.content:
                        full_content += delta.content
                        print(delta.content, end="", flush=True)
            
            print()  # 换行
            logger.info(thinking_content)
            logger.info(full_content)
            return full_content

        except Exception as e:
            logger.error(f"❌ 调用LLM API时发生错误: {e}")
            return None




