"""
斗地主Web前端Flask后端服务
提供HTTP API和Socket.IO实时通信
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sys
import os

# 添加父目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.base_agent import BaseAgent
from Agent.llm_client import AgentsLLM
from Environment.doudizhu import Env
from Agent.human_agent import HumanAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'doudizhu_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 全局游戏状态
game_env = None
players = {}
current_game_state = {}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/start_game', methods=['POST'])
def start_game():
    """开始游戏"""
    global game_env, players, current_game_state
    
    data = request.json
    player_types = data.get('player_types', {
        '地主': 'human',
        '农民甲': 'ai',
        '农民乙': 'ai'
    })
    
    # 初始化环境
    game_env = Env()
    game_env.reset()
    
    # 配置玩家
    players = {}
    for player_name, player_type in player_types.items():
        if player_type == 'human':
            players[player_name] = HumanAgent(name=player_name)
        else:
            players[player_name] = BaseAgent(name=player_name, llm_client=AgentsLLM)
    
    # 获取初始状态
    current_player, hand, action_space, history, state = game_env.Observe()
    
    current_game_state = {
        'current_player': current_player,
        'hands': {
            '地主': game_env.hands['地主'],
            '农民甲': game_env.hands['农民甲'],
            '农民乙': game_env.hands['农民乙']
        },
        'action_space': action_space,
        'history': history,
        'state': state,
        'game_over': False,
        'last_plays': {
            '地主': [],
            '农民甲': [],
            '农民乙': []
        }
    }
    
    # 广播游戏开始
    socketio.emit('game_started', current_game_state)
    
    # 如果当前玩家是AI，自动出牌
    if player_types[current_player] == 'ai':
        socketio.start_background_task(ai_make_decision)
    
    return jsonify({'success': True, 'state': current_game_state})


@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """获取当前游戏状态"""
    return jsonify(current_game_state)


@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('Client connected')
    emit('connected', {'message': '连接成功'})


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    print('Client disconnected')


@socketio.on('player_action')
def handle_player_action(data):
    """处理玩家出牌"""
    global game_env, current_game_state
    
    player = data.get('player')
    decision = data.get('decision')
    
    if not game_env or game_env.game_over():
        emit('error', {'message': '游戏未开始或已结束'})
        return
    
    # 执行出牌
    success, message = game_env.step(player, decision)
    
    if not success:
        # 出牌失败
        emit('action_failed', {
            'player': player,
            'message': message,
            'decision': decision
        })
        return
    
    # 更新游戏状态
    if game_env.game_over():
        current_game_state['game_over'] = True
        current_game_state['winner'] = player
        socketio.emit('game_over', {
            'winner': player,
            'hands': game_env.hands
        })
    else:
        # 更新该玩家的最后出牌（如果不是PASS）
        if 'last_plays' not in current_game_state:
            current_game_state['last_plays'] = {'地主': [], '农民甲': [], '农民乙': []}
        current_game_state['last_plays'][player] = decision
        
        current_player, hand, action_space, history, state = game_env.Observe()
        current_game_state.update({
            'current_player': current_player,
            'hands': {
                '地主': game_env.hands['地主'],
                '农民甲': game_env.hands['农民甲'],
                '农民乙': game_env.hands['农民乙']
            },
            'action_space': action_space,
            'history': history,
            'state': state,
            'game_over': False
        })
        
        socketio.emit('game_updated', current_game_state)
        
        # 如果下一个玩家是AI，自动出牌
        if isinstance(players[current_player], BaseAgent):
            socketio.start_background_task(ai_make_decision)


def ai_make_decision():
    """AI自动决策（后台任务）"""
    global game_env, players, current_game_state
    
    if not game_env or game_env.game_over():
        return
    
    current_player, hand, action_space, history, state = game_env.Observe()
    
    # 获取AI决策
    agent = players[current_player]
    decision = agent.make_decision(history, state, hand, err_msg=None, action_space=action_space)
    
    # 执行出牌
    out = game_env.step(current_player, decision)
    
    # 如果出牌失败，重试
    retry_count = 0
    while not out[0] and retry_count < 3:
        decision = agent.make_decision(history, state, hand, err_msg=out[1], action_space=action_space)
        out = game_env.step(current_player, decision)
        retry_count += 1
    
    # 如果重试3次仍失败，从动作空间随机选择
    if not out[0] and action_space:
        import random
        decision = random.choice(action_space)
        out = game_env.step(current_player, decision)
        print(f"⚠️  {current_player} AI重试3次失败，随机选择: {decision}")
    
    # 更新状态
    if game_env.game_over():
        current_game_state['game_over'] = True
        current_game_state['winner'] = current_player
        socketio.emit('game_over', {
            'winner': current_player,
            'hands': game_env.hands
        })
    else:
        # 获取出牌的玩家名称（在step之前保存）
        playing_player = current_player
        
        # 更新该玩家的最后出牌（如果不是PASS）
        if decision != ['PASS']:
            if 'last_plays' not in current_game_state:
                current_game_state['last_plays'] = {'地主': [], '农民甲': [], '农民乙': []}
            current_game_state['last_plays'][playing_player] = decision
        
        current_player, hand, action_space, history, state = game_env.Observe()
        current_game_state.update({
            'current_player': current_player,
            'hands': {
                '地主': game_env.hands['地主'],
                '农民甲': game_env.hands['农民甲'],
                '农民乙': game_env.hands['农民乙']
            },
            'action_space': action_space,
            'history': history,
            'state': state,
            'game_over': False
        })
        
        socketio.emit('game_updated', current_game_state)
        
        # 如果下一个玩家还是AI，继续
        if isinstance(players[current_player], BaseAgent):
            socketio.start_background_task(ai_make_decision)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
