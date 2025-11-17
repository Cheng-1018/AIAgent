from .llm_client import AgentsLLM
from .prompt import BASE_PROMPT, SYSTEMPROMPT,ERR_PROMPT
import ast
from utils import logger
import random
import time
# 地主、农民甲、农民乙基础agent
class BaseAgent:
    def __init__(self, name: str, llm_client: AgentsLLM):
        self.name = name
        self.llm_client = llm_client()

    def make_decision(self,
                      history: list[str],
                      state:str,hand:list[str],
                      err_msg:str=None,
                      action_space:list[list[str]]=None) -> list[str]:
        """
        根据当前游戏状态做出决策。
        这个方法需要被具体的代理类实现。
        """
        if  action_space==[['PASS']]:
            time.sleep(6)
            return ['PASS']
        
        if not err_msg:
            prompt= BASE_PROMPT.format(role=self.name, history="\n".join(history), state=state, hand=hand,action_space=str(action_space))
        else:
            prompt= ERR_PROMPT.format(role=self.name, history="\n".join(history), state=state, hand=hand, err_msg=err_msg,action_space=str(action_space))
        
        exampleMessages = [
            {"role": "system", "content": SYSTEMPROMPT},
            {"role": "user", "content": prompt}
        ]
        
        # print("--- 调用LLM ---")
        try:
            responseText = self.llm_client.think_streaming(exampleMessages)
            # logger.info(f"{self.name}\n: {responseText}")
            action= self._parse_response(responseText)
            return action
        except Exception as e:
            logger.error(f"调用LLM时出错: {e}")
            return  random.choice(action_space) # 出现错误时，随机从选择空间出一个牌型
    def _parse_response(self, response: str) -> list[str]:
        """
        解析LLM的响应，提取出决策部分。
        这个方法需要根据具体的响应格式进行实现。
        """
        # 这里只是一个简单的示例，假设响应格式为 "[THOUGHT]: ... [ACTION]: <decision>"
        action_part = response.split("[ACTION]:")[1].strip()
        # 使用 ast.literal_eval 将字符串形式的列表转换为真正的列表
        return ast.literal_eval(action_part)
        



# --- 代理使用示例 ---
if __name__ == '__main__':
    agent = BaseAgent(name="玩家2", llm_client=AgentsLLM)
    print(agent._parse_response("""[THGOUGHT]: 作为地主，第一轮出牌，我需要选择一个强牌型来控制局面。手牌中包含8、9、10、J、Q，可以组成顺子（点数8、9、10、11、12连续，不包括2和王牌）。这是可能的最大顺子，因为K和A缺失，且顺子牌型大于三张、连对等其他牌型。出此顺子可以有效压制农民，因为农
民可能没有更大的顺子或炸弹（当前手牌无炸弹）。其他选项如出三张2（点数2最大，但三张牌型小于顺子）或单张大王（太弱，易被压制）均不理想。因此，选择出8-Q顺子。

[ACTION]: ['8','9','10','J','Q']"""))
    history="""
    玩家1： ['抢地主']
    """
    hand="['9','9','9','10','10','10','10','J','Q','K','A','A','2','2','2','JOKER','JOKER']"

    state=""""
    现在是抢地主阶段
    """
    decision = agent.make_decision(history,state,hand)