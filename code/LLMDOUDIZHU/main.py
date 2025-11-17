from Agent.base_agent import BaseAgent
from Agent.llm_client import AgentsLLM
from Environment.doudizhu import Env
from Agent.human_agent import HumanAgent
from utils import logger


llm_client = AgentsLLM
env = Env()
env.reset()

# 配置玩家类型：可以选择 BaseAgent(AI) 或 HumanAgent(人类)
landlord = HumanAgent(name="地主")  # 地主由人类控制
farmerA = BaseAgent(name="农民甲", llm_client=llm_client)  # 农民甲由AI控制
farmerB = BaseAgent(name="农民乙", llm_client=llm_client)  # 农民乙由AI控制


current_player:str
hand:list[str]
action_space:list[list[str]]
history:list[str]
state:str

while not env.game_over():
    current_player, hand, action_space, history, state = env.Observe()
    
    logger.info(f'\n{current_player} ： {str(hand)}')
    print('\n'.join(history))
    
    # 根据当前玩家选择对应的Agent
    if current_player == "地主":
        Agent = landlord
    elif current_player == "农民甲":
        Agent = farmerA
    else:
        Agent = farmerB
    
    # 获取决策（支持错误重试）
    decision = Agent.make_decision(history, state, hand, err_msg=None, action_space=action_space)
    out = env.step(current_player, decision)
    
    # 如果出牌失败，继续让玩家重新出牌
    while not out[0]:
        logger.error(out[1])
        decision = Agent.make_decision(history, state, hand, err_msg=out[1],action_space=action_space)
        out = env.step(current_player, decision)
    
    # 检查游戏是否结束
    if env.game_over():
        logger.info(f"游戏结束，{current_player}获胜！")
        env.render()
        break
    


