from Agent.base_agent import BaseAgent
from Agent.llm_client import AgentsLLM
from typing import Dict, List
from .card_validator import CardValidator
from utils import logger
cards= ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'JOKER', 'JOKER']
# suits = ['', '', '', '']

class Env:
    def __init__(self):
        self.history: List[str] = []
        self.hands: Dict[str, List[str]] = {
            "地主": [],
            "农民甲": [],
            "农民乙": []
        }
        self.bottom_cards: List[str] = []
        self.current_player: str = "地主"
        self.state: str = "游戏开始，准备发牌阶段"
        self.validator = CardValidator()
        self.last_valid_play: List[str] = []  # 记录最后一次有效出牌
        self.pass_count: int = 0  # 连续PASS计数
        self.round: int = 0  # 当前回合数
    def reset(self):
        import random
        
        self.history = []
        self.hands = {
            "地主": [],
            "农民甲": [],
            "农民乙": []
        }
        self.current_player = "地主"
        self.state = "游戏开始，准备发牌阶段"
        self.last_valid_play = []
        self.pass_count = 0
        # 生成完整牌组：52张普通牌 + 2张王牌 = 54张
        deck = []
        for card in cards[:-2]:  # 3到2
            for i in range(4):
                deck.append(f"{card}")
        deck.append("小王")
        deck.append("大王")
        
        # 洗牌
        random.shuffle(deck)
        
        # 发牌：每人17张，剩余3张作为底牌
        self.hands["地主"] = sorted(deck[0:17]+deck[51:54], key=lambda x: self._card_sort_key(x))
        self.hands["农民甲"] = sorted(deck[17:34], key=lambda x: self._card_sort_key(x))
        self.hands["农民乙"] = sorted(deck[34:51], key=lambda x: self._card_sort_key(x))
        self.bottom_cards = sorted(deck[51:54], key=lambda x: self._card_sort_key(x))
        
        self.state = f"底牌为：{self.bottom_cards}\n 各玩家手中牌数：\n地主{len(self.hands['地主'])}张\n农民甲{len(self.hands['农民甲'])}张\n农民乙{len(self.hands['农民乙'])}张"
        self.history.append(f"游戏开始\n回合{self.round}\n")
    def _card_sort_key(self, card: str):
        """用于排序的辅助函数，按牌的大小排序"""
        card_order = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        
        if card == "小王":
            return 100
        elif card == "大王":
            return 101
        else:
            if card in card_order:
                return card_order.index(card)
            return 0

    def step(self, player: str, decision: list[str]) -> tuple[bool, str]:
        """执行一步游戏，添加规则验证"""
        
        # 1. 验证牌型是否有效
        card_type, _ = self.validator.identify_card_type(decision)
        if card_type == "无效牌型":
            err_message = f"❌ {player} 出牌失败：无效的牌型 {decision}"
            
            return (False,err_message)
        
        # 2. 验证手中是否有这些牌
        if not self.validator.has_cards(self.hands[player], decision):
            err_message = f"❌ {player} 出牌失败：手中没有这些牌 {decision}"
            return (False, err_message)
        if not self.last_valid_play and decision == ['PASS']:
            err_message = f"❌ {player} 出牌失败：本轮尚无有效出牌，不能选择PASS，轮到你出牌"
            return (False, err_message)
        # 3. 验证是否能压过上一手牌
        if not self.validator.can_beat(decision, self.last_valid_play):
            err_message = f"❌ {player} 出牌失败：无法压过上一手牌"
            err_message += f"\n   上一手: {self.last_valid_play}"
            err_message += f"\n   当前出: {decision}"
            return (False, err_message)
        
        # 4. 记录历史
        self.history.append(f"{player}： {decision}")
        
        # 5. 更新最后有效出牌和PASS计数
        if decision == ['PASS']:
            self.pass_count += 1
            # 连续两家PASS，清空最后出牌记录（下家可以出任意牌）
            if self.pass_count >= 2:
                self.last_valid_play = []
                self.pass_count = 0
                self.round += 1
                self.history.append(f"\n回合{self.round}\n")
        else:
            self.last_valid_play = decision
            self.pass_count = 0
            # 移除已出的牌
            for card in decision:
                if card in self.hands[player]:
                    self.hands[player].remove(card)
        
        # 6. 切换到下一个玩家
        if self.current_player == "地主":
            self.current_player = "农民甲"
        elif self.current_player == "农民甲":
            self.current_player = "农民乙"
        else:
            self.current_player = "地主"
        
        # 7. 更新状态
        self.state = f"底牌为：{self.bottom_cards}\n 各玩家手中牌数：\n地主{len(self.hands['地主'])}张\n农民甲{len(self.hands['农民甲'])}张\n农民乙{len(self.hands['农民乙'])}张"
        
        return (True, "出牌成功")
    def game_over(self) -> bool:
        # 游戏结束判断逻辑省略
        for player, hand in self.hands.items():
            if len(hand) == 0:
                return True
        return False

    def render(self):
        logger.info("当前游戏状态：" + self.state)
        logger.info("游戏历史：" + '\n'.join(self.history))
    def Observe(self)->tuple[str,List[str],List[List[str]],List[str],str]:
        """返回当前游戏的观察信息"""
        return self.current_player, self.hands[self.current_player],self.validator.hint(self.hands[self.current_player],self.last_valid_play), self.history, self.state,