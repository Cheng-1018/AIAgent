from typing import List, Tuple, Optional
from collections import Counter


example=['3', '3', '3', '4', '4', '4']


class CardType:
    """牌型定义"""
    INVALID = "无效牌型"
    SINGLE = "单张"
    PAIR = "对子"
    TRIPLE = "三张"
    TRIPLE_WITH_SINGLE = "三带一"
    TRIPLE_WITH_PAIR = "三带二"
    BOMB_WITH_SINGLES = "四带二单"
    BOMB_WITH_PAIR = "四带二对"
    STRAIGHT = "顺子"
    CONSECUTIVE_PAIRS = "连对"
    AIRPLANE = "飞机"
    AIRPLANE_WITH_SINGLES = "飞机带单"
    AIRPLANE_WITH_PAIRS = "飞机带对"
    BOMB = "炸弹"
    ROCKET = "王炸"
    PASS = "不要"

class CardValidator:
    """斗地主牌型验证器"""
    
    CARD_ORDER = {
        '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17
    }
    
    @staticmethod
    def get_card_value(card: str) -> int:
        """获取牌的点数值"""
        if card in ['小王', '大王']:
            return CardValidator.CARD_ORDER[card]
        return CardValidator.CARD_ORDER.get(card, 0)
    
    
    @classmethod
    def identify_card_type(cls, cards: List[str]) -> Tuple[str, int]:
        """
        识别牌型并返回(牌型, 主要点数)
        返回: (牌型名称, 主要牌的点数)
        """
        if not cards:
            return (CardType.INVALID, 0)
        
        if cards == ['PASS']:
            return (CardType.PASS, 0)
        # 统计每张牌的数量
        try:
            card_values = [cls.get_card_value(card) for card in cards]
        except KeyError:
            return (CardType.INVALID, 0)
        face_counter = Counter(cards)
        
        num_cards = len(cards)
        unique_faces = len(face_counter)
        
        # 王炸
        if num_cards == 2 and set(cards) == {'小王', '大王'}:
            return (CardType.ROCKET, 17)
        
        # 炸弹：四张相同（纯炸弹，不带牌）
        if num_cards == 4 and unique_faces == 1:
            return (CardType.BOMB, card_values[0])
        
        # 四带二单：四张相同 + 两张单牌
        if num_cards == 6 and unique_faces == 3:
            counts = sorted(face_counter.values(), reverse=True)
            if counts == [4, 1, 1]:
                bomb_face = [face for face, count in face_counter.items() if count == 4][0]
                return (CardType.BOMB_WITH_SINGLES, cls.CARD_ORDER[bomb_face])
        
        # 四带二对：四张相同 + 一对
        if num_cards == 6 and unique_faces == 2:
            counts = sorted(face_counter.values(), reverse=True)
            if counts == [4, 2]:
                bomb_face = [face for face, count in face_counter.items() if count == 4][0]
                return (CardType.BOMB_WITH_PAIR, cls.CARD_ORDER[bomb_face])
        
        # 四带二对（两对的情况）：四张相同 + 两对
        if num_cards == 8 and unique_faces == 3:
            counts = sorted(face_counter.values(), reverse=True)
            if counts == [4, 2, 2]:
                bomb_face = [face for face, count in face_counter.items() if count == 4][0]
                return (CardType.BOMB_WITH_PAIR, cls.CARD_ORDER[bomb_face])
        
        # 单张
        if num_cards == 1:
            return (CardType.SINGLE, card_values[0])
        
        # 对子
        if num_cards == 2 and unique_faces == 1:
            return (CardType.PAIR, card_values[0])
        
        # 三张
        if num_cards == 3 and unique_faces == 1:
            return (CardType.TRIPLE, card_values[0])
        
        # 三带一
        if num_cards == 4 and unique_faces == 2:
            counts = list(face_counter.values())
            if 3 in counts and 1 in counts:
                triple_face = [face for face, count in face_counter.items() if count == 3][0]
                return (CardType.TRIPLE_WITH_SINGLE, cls.CARD_ORDER[triple_face])
        
        # 三带二
        if num_cards == 5 and unique_faces == 2:
            counts = list(face_counter.values())
            if 3 in counts and 2 in counts:
                triple_face = [face for face, count in face_counter.items() if count == 3][0]
                return (CardType.TRIPLE_WITH_PAIR, cls.CARD_ORDER[triple_face])
        
        # 顺子：至少5张连续单张（不包括2和王）
        if num_cards >= 5 and unique_faces == num_cards:
            sorted_values = sorted(card_values)
            # 检查是否包含2或王
            if any(v >= 15 for v in sorted_values):
                return (CardType.INVALID, 0)
            # 检查是否连续
            if cls._is_consecutive(sorted_values):
                return (CardType.STRAIGHT, sorted_values[-1])
        
        # 连对：至少3对连续对子
        if num_cards >= 6 and num_cards % 2 == 0 and all(count == 2 for count in face_counter.values()):
            sorted_values = sorted(set(card_values))
            if len(sorted_values) >= 3 and all(v < 15 for v in sorted_values):
                if cls._is_consecutive(sorted_values):
                    return (CardType.CONSECUTIVE_PAIRS, sorted_values[-1])
        
        # 飞机：至少2个连续的三张
        triple_faces = [face for face, count in face_counter.items() if count == 3]
        if len(triple_faces) >= 2:
            triple_values = sorted([cls.CARD_ORDER[face] for face in triple_faces])
            if all(v < 15 for v in triple_values) and cls._is_consecutive(triple_values):
                # 纯飞机
                if num_cards == len(triple_faces) * 3:
                    return (CardType.AIRPLANE, triple_values[-1])
                # 飞机带单
                elif num_cards == len(triple_faces) * 4:
                    return (CardType.AIRPLANE_WITH_SINGLES, triple_values[-1])
                # 飞机带对
                elif num_cards == len(triple_faces) * 5:
                    pair_count = sum(1 for count in face_counter.values() if count == 2)
                    if pair_count == len(triple_faces):
                        return (CardType.AIRPLANE_WITH_PAIRS, triple_values[-1])
        
        return (CardType.INVALID, 0)
    
    @classmethod
    def hint_all(cls,hand:list[str])->list[Tuple[str, int, List[str]]]:
        """ 遍历所有牌型，给出当前手牌中可出的牌列表-即动作空间"""    
        counter=Counter(hand)
        singles=[f for f,c in counter.items()]
        pairs=[f for f,c in counter.items() if c>=2]
        triples=[f for f,c in counter.items() if c>=3]
        bombs=[f for f,c in counter.items() if c==4]
        rocket=hand.count('小王')>0 and hand.count('大王')>0
        
        action=[(CardType.PASS,0,['PASS'])]
        # 王炸类型
        if rocket:
            action.append( (CardType.ROCKET, 17, ['小王','大王']) )
        # 单排类型
        for s in singles:
            action.append( (CardType.SINGLE, cls.CARD_ORDER[s], [s]) )
        # 对子类型
        for p in pairs:
            action.append( (CardType.PAIR, cls.CARD_ORDER[p], [p,p]) )
        # 三张类型
        for t in triples:
            action.append( (CardType.TRIPLE, cls.CARD_ORDER[t], [t,t,t]) )
        # 三带一类型
        for t in triples:
            for s in singles:
                if s != t:
                    action.append( (CardType.TRIPLE_WITH_SINGLE, cls.CARD_ORDER[t], [t,t,t,s]) )
        # 三带二类型
        for t in triples:
            for p in pairs:
                if p != t:
                    action.append( (CardType.TRIPLE_WITH_PAIR, cls.CARD_ORDER[t], [t,t,t,p,p]) )
        # 炸弹类型
        for b in bombs:
            action.append( (CardType.BOMB, cls.CARD_ORDER[b], [b,b,b,b]) )
        # 四带二单类型
        for b in bombs:
            for s1 in singles:
                for s2 in singles:
                    if s1 != b and s2 != b and s1 != s2:
                        action.append( (CardType.BOMB_WITH_SINGLES, cls.CARD_ORDER[b], [b,b,b,b,s1,s2]) )
        # 四带二对类型
        for b in bombs:
            for p1 in pairs:
                for p2 in pairs:
                    if p1 != b and p2 != b and p1 != p2:
                        action.append( (CardType.BOMB_WITH_PAIR, cls.CARD_ORDER[b], [b,b,b,b,p1,p1,p2,p2]) )
        # 顺子类型：至少5张连续单张（不包括2和王）
        for start in range(3, 11):  # 从3开始，最多到10开头的顺子（10-A最长）
            for length in range(5, 13):  # 顺子长度5-12张
                if start + length - 1 > 14:  # 不能包含2（点数15）
                    break
                straight = []
                valid = True
                for i in range(length):
                    card_value = start + i
                    # 找到这个点数的牌
                    card_str = [k for k, v in cls.CARD_ORDER.items() if v == card_value and k not in ['小王', '大王']][0]
                    # 检查手中是否有这张牌
                    matching_cards = [c for c in hand if cls.get_card_value(c) == card_value]
                    if not matching_cards:
                        valid = False
                        break
                    straight.append(matching_cards[0])
                
                if valid and len(straight) == length:
                    action.append((CardType.STRAIGHT, start + length - 1, straight))
        
        # 连对类型：至少3对连续对子
        for start in range(3, 13):  # 从3开始，最多到Q开头
            for length in range(3, 11):  # 连对长度3-10对
                if start + length - 1 > 14:  # 不能包含2
                    break
                consecutive_pairs = []
                valid = True
                for i in range(length):
                    card_value = start + i
                    # 找到这个点数的牌（至少要有2张）
                    matching_cards = [c for c in hand if cls.get_card_value(c) == card_value]
                    if len(matching_cards) < 2:
                        valid = False
                        break
                    consecutive_pairs.extend(matching_cards[:2])
                
                if valid and len(consecutive_pairs) == length * 2:
                    action.append((CardType.CONSECUTIVE_PAIRS, start + length - 1, consecutive_pairs))
        
        # 飞机（纯）：至少2个连续的三张
        for start in range(3, 13):  # 从3开始，最多到Q开头
            for length in range(2, 6):  # 飞机长度2-5组
                if start + length - 1 > 14:  # 不能包含2
                    break
                airplane = []
                valid = True
                for i in range(length):
                    card_value = start + i
                    # 找到这个点数的牌（至少要有3张）
                    matching_cards = [c for c in hand if cls.get_card_value(c) == card_value]
                    if len(matching_cards) < 3:
                        valid = False
                        break
                    airplane.extend(matching_cards[:3])
                
                if valid and len(airplane) == length * 3:
                    action.append((CardType.AIRPLANE, start + length - 1, airplane))
        
        # 飞机带单牌：n个连续三张 + n张单牌
        for start in range(3, 13):
            for length in range(2, 6):  # 飞机长度2-5组
                if start + length - 1 > 14:
                    break
                airplane = []
                valid = True
                # 先检查三张部分
                for i in range(length):
                    card_value = start + i
                    matching_cards = [c for c in hand if cls.get_card_value(c) == card_value]
                    if len(matching_cards) < 3:
                        valid = False
                        break
                    airplane.extend(matching_cards[:3])
                
                if valid:
                    # 找单牌（不在飞机中的牌）
                    used_values = set(range(start, start + length))
                    available_singles = [c for c in hand if cls.get_card_value(c) not in used_values]
                    
                    # 需要length张单牌
                    if len(available_singles) >= length:
                        from itertools import combinations
                        for single_combo in combinations(available_singles, length):
                            full_airplane = airplane + list(single_combo)
                            action.append((CardType.AIRPLANE_WITH_SINGLES, start + length - 1, full_airplane))
        
        # 飞机带对牌：n个连续三张 + n对
        for start in range(3, 13):
            for length in range(2, 6):  # 飞机长度2-5组
                if start + length - 1 > 14:
                    break
                airplane = []
                valid = True
                # 先检查三张部分
                for i in range(length):
                    card_value = start + i
                    matching_cards = [c for c in hand if cls.get_card_value(c) == card_value]
                    if len(matching_cards) < 3:
                        valid = False
                        break
                    airplane.extend(matching_cards[:3])
                
                if valid:
                    # 找对子（不在飞机中的牌）
                    used_values = set(range(start, start + length))
                    available_pairs_dict = {}
                    for card in hand:
                        card_val = cls.get_card_value(card)
                        if card_val not in used_values:
                            available_pairs_dict[card] = available_pairs_dict.get(card, 0) + 1
                    
                    available_pairs = [c for c, count in available_pairs_dict.items() if count >= 2]
                    
                    # 需要length对
                    if len(available_pairs) >= length:
                        from itertools import combinations
                        for pair_combo in combinations(available_pairs, length):
                            pairs_cards = []
                            for p in pair_combo:
                                pairs_cards.extend([p, p])
                            full_airplane = airplane + pairs_cards
                            action.append((CardType.AIRPLANE_WITH_PAIRS, start + length - 1, full_airplane))
        
        return action

    @staticmethod
    def _is_consecutive(values: List[int]) -> bool:
        """检查数值是否连续"""
        for i in range(len(values) - 1):
            if values[i + 1] - values[i] != 1:
                return False
        return True
    
    @classmethod
    def can_beat(cls, current_cards: List[str], last_valid_play: List[str]) -> bool:
        """
        判断当前牌是否能压过上一手牌
        
        Args:
            current_cards: 当前要出的牌
            last_valid_play: 上一手的有效牌
            
        Returns:
            bool: 是否能出
        """
        # PASS可以随时出
        if current_cards == ['PASS'] and last_valid_play:
            return True
        
        # 如果上一手是没有有效牌型，当前牌只要有效即可
        if not last_valid_play :
            current_type, _ = cls.identify_card_type(current_cards)
            return current_type != CardType.INVALID and current_type != CardType.PASS
        
        current_type, current_value = cls.identify_card_type(current_cards)
        previous_type, previous_value = cls.identify_card_type(last_valid_play)
        
        # 牌型无效
        if current_type == CardType.INVALID:
            return False
        
        # 王炸可以压任何牌
        if current_type == CardType.ROCKET:
            return True
        
        # 炸弹可以压除王炸和更大炸弹外的所有牌
        if current_type == CardType.BOMB:
            if previous_type == CardType.ROCKET:
                return False
            if previous_type == CardType.BOMB:
                return current_value > previous_value
            return True
        
        # # 四带二单和四带二对只能压同类型的炸弹
        # if current_type in [CardType.BOMB_WITH_SINGLES, CardType.BOMB_WITH_PAIR]:
        #     if previous_type == CardType.ROCKET:
        #         return False
        #     if previous_type in [CardType.BOMB, CardType.BOMB_WITH_SINGLES, CardType.BOMB_WITH_PAIR]:
        #         return current_value > previous_value
        #     return False
        
        # 其他牌型必须类型相同且数量相同
        if current_type != previous_type:
            return False
        
        if len(current_cards) != len(last_valid_play):
            return False
        
        # 比较点数大小
        return current_value > previous_value
    
    @staticmethod
    def has_cards(hand: List[str], cards_to_play: List[str]) -> bool:
        """验证手牌中是否有要出的牌"""
        if cards_to_play == ['PASS']:
            return True
        
        hand_counter = Counter(hand)
        play_counter = Counter(cards_to_play)
        
        for card, count in play_counter.items():
            if hand_counter[card] < count:
                return False
        return True

    @classmethod
    def hint(cls,hand:list[str],last_valid_play:list[str])->list[List[str]]:
        """ 给出当前手牌中可出的牌列表-即动作空间"""    
        all_actions=cls.hint_all(hand)
        if not last_valid_play:
            all_actions.remove( (CardType.PASS,0,['PASS']) )
            return [action[2] for action in all_actions]
        valid_actions=[]
        for action in all_actions:
            card_type, value, cards=action
            if cls.can_beat(cards,last_valid_play):
                valid_actions.append(cards)
        return valid_actions

# 测试代码
if __name__ == '__main__':
    validator = CardValidator()
    
    # 测试牌型识别
    test_cases = [
        (['3'], "单张"),
        (['3', '3'], "对子"),
        (['3', '3', '3'], "三张"),
        (['3', '3', '3', '4'], "三带一"),
        (['3', '3', '3', '4', '4'], "三带二"),
        (['3', '4', '5', '6', '7'], "顺子"),
        (['3', '3', '4', '4', '5', '5'], "连对"),
        (['3', '3', '3', '4', '4', '4'], "飞机"),
        (['K', 'K', 'K', 'K'], "炸弹"),
        (['6', '6', '6', '6', '3', '5'], "四带二单"),
        (['6', '6', '6', '6', '3', '3'], "四带二对"),
        (['6', '6', '6', '6', '3', '3', '4', '4'], "四带两对"),
        (['小王', '大王'], "王炸"),
    ]
    
    for cards, expected in test_cases:
        card_type, value = validator.identify_card_type(cards)
        print(f"{cards} -> {card_type} (点数: {value}), 预期: {expected}")
    
    # 测试能否压牌
    print("\n=== 测试压牌 ===")
    print("单张5能否压单张3:", validator.can_beat(['5'], ['3']))
    print("对子5能否压单张3:", validator.can_beat(['5', '5'], ['3']))
    print("炸弹能否压顺子:", validator.can_beat(['K', 'K', 'K', 'K'], ['3', '4', '5', '6', '7']))
    print("四带二单能否压顺子:", validator.can_beat(['6', '6', '6', '6', '3', '5'], ['3', '4', '5', '6', '7']))
    print("四带二对能否压三张:", validator.can_beat(['6', '6', '6', '6', '3', '3'], ['5', '5', '5']))
    
    example_hand = ['3', '3', '3', '4', '4', '4', '5', '6', '7', '8']
    actions = validator.hint(example_hand)
    print("\n=== 可出牌列表 ===")
    for action in actions:
        print(action,end=' -> ')
        print(validator.identify_card_type(action[2]))