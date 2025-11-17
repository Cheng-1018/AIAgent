
class HumanAgent:
    """人类玩家代理，通过控制台输入进行决策"""
    
    def __init__(self, name: str):
        self.name = name
    @staticmethod
    def colorize_card(card: str) -> str:
        """为单张牌添加颜色"""
        SUIT_COLORS = {
            '': '\033[91m',  # 红色
            '': '\033[91m',  # 红色
            '': '\033[90m',  # 黑色
            '': '\033[90m',  # 黑色
        }
        
        if card in ['小王', '大王']:
            return f'\033[93m{card}\033[0m'  # 黄色
        
        for suit, color in SUIT_COLORS.items():
            if suit in card:
                return f'{color}{card}\033[0m'
        return card
    def make_decision(self, 
                      history: list[str], 
                      state: str, 
                      hand: list[str],
                      err_msg: str = None, 
                      action_space:list[list[str]]=None
                      ) -> list[str]:
        """
        通过控制台输入获取人类玩家的出牌决策
        
        Args:
            history: 出牌历史
            state: 当前游戏状态
            hand: 当前手牌
            err_msg: 错误信息（如果上一次出牌失败）
            
        Returns:
            出牌决策列表
        """
        print("\n" + "=" * 60)
        print(f"轮到 {self.name} 出牌")
        print("=" * 60)
        
        # 显示游戏状态
        print(f"\n当前游戏状态：")
        print(state)
        
        # 显示历史（最近5条）
        if history:
            print(f"\n出牌历史：")
            recent_history = history
            for record in recent_history:
                if record.strip():
                    print(f"  {record}")
        
        
        
        # 显示当前手牌（带编号）
        print(f"\n你的当前手牌：")
        for i, card in enumerate(hand, 1):
            card= self.colorize_card(card)  
            print(f"  {i:2d}. {card}", end="  ")
            if i % 8 == 0:  # 每行显示8张牌
                print()
        # 显示可选动作
        if action_space is not None:
            print(f"\n\n可选动作：")
            for action in action_space:
                action_str = ', '.join(action)
                print(f"  - {action_str}")
        print("\n")
        # 显示错误信息
        if err_msg:
            print(f"\n注意：你上次的出牌尝试失败，原因是：\n {err_msg}")
        # 获取用户输入
        print("💡 输入说明：")
        print("  - 输入卡牌编号（用空格或逗号分隔），例如：1 2 3 或 1,2,3")
        print("  - 输入 'p' 或 'pass' 表示不要")
        print("  - 输入 'h' 或 'help' 查看手牌")
        
        while True:
            user_input = input(f"\n👉 请出牌 ({self.name}): ").strip().lower()
            
            # 处理帮助命令
            if user_input in ['h', 'help']:
                print(f"\n你的手牌：{hand}")
                continue
            
            # 处理PASS
            if user_input in ['p', 'pass', '不要']:
                return ['PASS']
            
            # 处理退出
            if user_input in ['q', 'quit', 'exit']:
                print("退出游戏")
                exit(0)
            
            # 解析卡牌编号
            try:
                # 支持空格或逗号分隔
                indices_str = user_input.replace(',', ' ').split()
                indices = [int(idx) for idx in indices_str]
                
                # 验证编号范围
                if any(idx < 1 or idx > len(hand) for idx in indices):
                    print(f"❌ 编号超出范围！请输入 1-{len(hand)} 之间的数字")
                    continue
                
                # 获取对应的卡牌
                selected_cards = [hand[idx - 1] for idx in indices]
                
                # 确认选择
                print(f"✅ 你选择出：{selected_cards}")
                confirm = input("确认吗？(y/n 或直接回车确认): ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return selected_cards
                else:
                    print("已取消，请重新选择")
                    continue
                    
            except ValueError:
                print("❌ 输入格式错误！请输入数字编号，例如：1 2 3")
                continue
            except Exception as e:
                print(f"❌ 发生错误：{e}")
                continue


# 测试代码
if __name__ == '__main__':
    human = HumanAgent("测试玩家")
    
    test_hand = ['3', '4', '5', '6', '7', '8', '9', '10']
    test_history = "地主： ['3', '3', '3']\n农民甲： ['PASS']"
    test_state = "底牌为：['10', 'K', '2']\n各玩家手中牌数：\n地主17张\n农民甲17张\n农民乙17张"
    
    decision = human.make_decision(test_history, test_state, test_hand)
    print(f"\n最终决策：{decision}")