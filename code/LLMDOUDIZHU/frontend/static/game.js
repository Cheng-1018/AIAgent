// 游戏主逻辑
class DouDiZhuGame {
    constructor() {
        this.socket = null;
        this.currentPlayer = null;
        this.playerTypes = {
            '地主': 'human',
            '农民甲': 'human',
            '农民乙': 'human'
        };
        this.gameState = null;
        this.initSocket();
        this.initUI();
    }

    // 初始化Socket连接
    initSocket() {
        // 自动使用当前页面的主机地址和端口
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = window.location.port || '5000';
        const serverUrl = `${protocol}//${hostname}:${port}`;

        this.socket = io(serverUrl);

        this.socket.on('connected', (data) => {
            console.log('已连接到服务器:', data);
        });

        this.socket.on('game_started', (state) => {
            console.log('游戏开始:', state);
            this.gameState = state;
            this.updateUI(state);
            this.hideLoading();
        });

        this.socket.on('game_updated', (state) => {
            console.log('游戏更新:', state);
            this.gameState = state;
            this.updateUI(state);
            this.hideLoading();
        });

        this.socket.on('action_failed', (data) => {
            console.error('出牌失败:', data);
            alert(`出牌失败：${data.message}`);
            this.hideLoading();
        });

        this.socket.on('game_over', (data) => {
            console.log('游戏结束:', data);
            this.showGameOver(data.winner);
            this.hideLoading();
        });

        this.socket.on('error', (data) => {
            console.error('错误:', data);
            alert(data.message);
            this.hideLoading();
        });
    }

    // 初始化UI事件
    initUI() {
        // 开始游戏按钮
        document.getElementById('btnStartGame').addEventListener('click', () => {
            this.startGame();
        });

        // 重新开始按钮
        document.getElementById('btnRestart').addEventListener('click', () => {
            this.startGame();
        });

        // 设置按钮
        document.getElementById('btnSettings').addEventListener('click', () => {
            this.showSettings();
        });

        // 出牌按钮
        document.getElementById('btnPlay').addEventListener('click', () => {
            this.playCards();
        });

        // 不出按钮
        document.getElementById('btnPass').addEventListener('click', () => {
            this.pass();
        });

        // 提示按钮
        document.getElementById('btnHint').addEventListener('click', () => {
            this.showHint();
        });

        // 设置模态框
        const settingsModal = document.getElementById('settingsModal');
        const closeBtn = settingsModal.querySelector('.close');
        const saveBtn = document.getElementById('btnSaveSettings');
        const cancelBtn = document.getElementById('btnCancelSettings');

        closeBtn.addEventListener('click', () => {
            this.hideSettings();
        });

        saveBtn.addEventListener('click', () => {
            this.saveSettings();
        });

        cancelBtn.addEventListener('click', () => {
            this.hideSettings();
        });

        // 监听玩家类型选择变化
        document.getElementById('landlordPlayerType').addEventListener('change', () => {
            this.updatePlayerTypeOptions();
        });
        document.getElementById('farmerAPlayerType').addEventListener('change', () => {
            this.updatePlayerTypeOptions();
        });
        document.getElementById('farmerBPlayerType').addEventListener('change', () => {
            this.updatePlayerTypeOptions();
        });

        // 游戏结束模态框
        document.getElementById('btnPlayAgain').addEventListener('click', () => {
            this.hideGameOverModal();
            this.startGame();
        });

        // 点击模态框外部关闭
        window.addEventListener('click', (event) => {
            if (event.target === settingsModal) {
                this.hideSettings();
            }
        });
    }

    // 开始游戏
    async startGame() {
        this.showLoading();

        try {
            // 自动使用当前页面的主机地址和端口
            const protocol = window.location.protocol;
            const hostname = window.location.hostname;
            const port = window.location.port || '5000';
            const apiUrl = `${protocol}//${hostname}:${port}/api/start_game`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    player_types: this.playerTypes
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log('游戏启动成功');
            }
        } catch (error) {
            console.error('启动游戏失败:', error);
            alert('启动游戏失败，请检查服务器是否运行');
            this.hideLoading();
        }
    }

    // 更新UI
    updateUI(state) {
        // 更新游戏状态显示
        document.getElementById('gameState').textContent = state.state;

        // 更新每个玩家的信息
        this.updatePlayerInfo('地主', 'landlord', state);
        this.updatePlayerInfo('农民甲', 'farmerA', state);
        this.updatePlayerInfo('农民乙', 'farmerB', state);

        // 高亮当前玩家
        this.highlightCurrentPlayer(state.current_player);

        // 更新每个玩家的出牌显示
        if (state.last_plays) {
            // 地主的出牌
            CardUtils.renderPlayedCards(
                document.getElementById('landlordLastPlay'),
                state.last_plays['地主'] || []
            );
            // 农民甲的出牌
            CardUtils.renderPlayedCards(
                document.getElementById('farmerALastPlay'),
                state.last_plays['农民甲'] || []
            );
            // 农民乙的出牌
            CardUtils.renderPlayedCards(
                document.getElementById('farmerBLastPlay'),
                state.last_plays['农民乙'] || []
            );
        }

        // 更新操作按钮状态
        this.updateActionButtons(state);
    }

    // 更新玩家信息
    updatePlayerInfo(playerName, playerId, state) {
        const hands = state.hands[playerName] || [];
        const cardCount = hands.length;

        // 更新牌数
        document.getElementById(`${playerId}Count`).textContent = `${cardCount}张`;

        // 更新手牌显示
        const cardsContainer = document.getElementById(`${playerId}Cards`);

        if (playerName === '地主' && this.playerTypes['地主'] === 'human') {
            // 地主且为人类玩家，显示完整手牌
            CardUtils.renderCards(cardsContainer, hands, true);
        } else if (this.playerTypes[playerName] === 'human') {
            // 其他人类玩家，显示完整手牌
            CardUtils.renderCards(cardsContainer, hands, true);
        } else {
            // AI玩家，显示牌背
            CardUtils.renderCardBacks(cardsContainer, cardCount);
        }
    }

    // 高亮当前玩家
    highlightCurrentPlayer(currentPlayer) {
        // 移除所有高亮
        document.querySelectorAll('.player-area').forEach(el => {
            el.classList.remove('player-active');
        });

        // 添加当前玩家高亮
        const playerMap = {
            '地主': 'landlord',
            '农民甲': 'farmerA',
            '农民乙': 'farmerB'
        };

        const playerId = playerMap[currentPlayer];
        if (playerId) {
            document.getElementById(playerId).classList.add('player-active');
        }

        this.currentPlayer = currentPlayer;
    }

    // 更新操作按钮状态
    updateActionButtons(state) {
        const isCurrentPlayerHuman = this.playerTypes[state.current_player] === 'human';
        const actionPanel = document.getElementById('playerActions');

        if (isCurrentPlayerHuman && !state.game_over) {
            actionPanel.style.display = 'flex';

            // 根据action_space更新按钮状态
            const canPass = state.action_space && state.action_space.some(
                action => action.length === 1 && action[0] === 'PASS'
            );

            document.getElementById('btnPass').disabled = !canPass;
        } else {
            actionPanel.style.display = 'none';
        }
    }

    // 出牌
    playCards() {
        if (!this.gameState || this.gameState.game_over) {
            alert('游戏未开始或已结束');
            return;
        }

        const currentPlayerName = this.gameState.current_player;
        if (this.playerTypes[currentPlayerName] !== 'human') {
            alert('不是你的回合');
            return;
        }

        // 获取选中的牌
        const playerMap = {
            '地主': 'landlord',
            '农民甲': 'farmerA',
            '农民乙': 'farmerB'
        };

        const playerId = playerMap[currentPlayerName];
        const cardsContainer = document.getElementById(`${playerId}Cards`);
        const selectedCards = CardUtils.getSelectedCards(cardsContainer);

        if (selectedCards.length === 0) {
            alert('请选择要出的牌');
            return;
        }

        // 发送出牌动作
        this.showLoading();
        this.socket.emit('player_action', {
            player: currentPlayerName,
            decision: selectedCards
        });

        // 清除选中状态
        CardUtils.clearSelection(cardsContainer);
    }

    // 不出
    pass() {
        if (!this.gameState || this.gameState.game_over) {
            alert('游戏未开始或已结束');
            return;
        }

        const currentPlayerName = this.gameState.current_player;
        if (this.playerTypes[currentPlayerName] !== 'human') {
            alert('不是你的回合');
            return;
        }

        // 发送PASS动作
        this.showLoading();
        this.socket.emit('player_action', {
            player: currentPlayerName,
            decision: ['PASS']
        });
    }

    // 提示
    showHint() {
        if (!this.gameState || !this.gameState.action_space) {
            alert('暂无提示');
            return;
        }

        const validActions = this.gameState.action_space.filter(
            action => !(action.length === 1 && action[0] === 'PASS')
        );

        if (validActions.length === 0) {
            alert('没有可出的牌');
            return;
        }

        // 显示第一个可行的牌型
        const hint = validActions[0];
        alert(`提示：可以出 ${hint.join(', ')}`);

        // 自动选中提示的牌
        const currentPlayerName = this.gameState.current_player;
        const playerMap = {
            '地主': 'landlord',
            '农民甲': 'farmerA',
            '农民乙': 'farmerB'
        };

        const playerId = playerMap[currentPlayerName];
        const cardsContainer = document.getElementById(`${playerId}Cards`);

        // 清除之前的选中
        CardUtils.clearSelection(cardsContainer);

        // 选中提示的牌
        hint.forEach(card => {
            const cardElement = cardsContainer.querySelector(`[data-card="${card}"]`);
            if (cardElement) {
                cardElement.classList.add('selected');
            }
        });
    }

    // 显示设置
    showSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.add('show');

        // 设置当前值
        document.getElementById('landlordPlayerType').value = this.playerTypes['地主'];
        document.getElementById('farmerAPlayerType').value = this.playerTypes['农民甲'];
        document.getElementById('farmerBPlayerType').value = this.playerTypes['农民乙'];

        // 更新选项状态
        this.updatePlayerTypeOptions();
    }

    // 更新玩家类型选项（确保至少有一个人类玩家）
    updatePlayerTypeOptions() {
        const landlordSelect = document.getElementById('landlordPlayerType');
        const farmerASelect = document.getElementById('farmerAPlayerType');
        const farmerBSelect = document.getElementById('farmerBPlayerType');

        const selects = [landlordSelect, farmerASelect, farmerBSelect];

        // 统计AI数量
        let aiCount = 0;
        selects.forEach(select => {
            if (select.value === 'ai') {
                aiCount++;
            }
        });

        // 如果已经有2个AI，则禁用其他选项的AI选择
        selects.forEach(select => {
            const aiOption = select.querySelector('option[value="ai"]');
            if (select.value === 'human' && aiCount >= 2) {
                // 当前是人类，且已有2个AI，禁用AI选项
                aiOption.disabled = true;
            } else {
                // 否则启用AI选项
                aiOption.disabled = false;
            }
        });
    }

    // 隐藏设置
    hideSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.remove('show');
    }

    // 保存设置
    saveSettings() {
        const landlordType = document.getElementById('landlordPlayerType').value;
        const farmerAType = document.getElementById('farmerAPlayerType').value;
        const farmerBType = document.getElementById('farmerBPlayerType').value;

        // 验证：至少有一个人类玩家
        const aiCount = [landlordType, farmerAType, farmerBType].filter(type => type === 'ai').length;
        if (aiCount >= 3) {
            alert('至少需要一个人类玩家！');
            return;
        }

        this.playerTypes['地主'] = landlordType;
        this.playerTypes['农民甲'] = farmerAType;
        this.playerTypes['农民乙'] = farmerBType;

        // 更新UI显示
        document.getElementById('landlordType').textContent =
            this.playerTypes['地主'] === 'human' ? '人类' : 'AI';
        document.getElementById('farmerAType').textContent =
            this.playerTypes['农民甲'] === 'human' ? '人类' : 'AI';
        document.getElementById('farmerBType').textContent =
            this.playerTypes['农民乙'] === 'human' ? '人类' : 'AI';

        // 更新AI徽章显示
        document.getElementById('landlordBadge').style.display =
            this.playerTypes['地主'] === 'ai' ? 'block' : 'none';
        document.getElementById('farmerABadge').style.display =
            this.playerTypes['农民甲'] === 'ai' ? 'block' : 'none';
        document.getElementById('farmerBBadge').style.display =
            this.playerTypes['农民乙'] === 'ai' ? 'block' : 'none';

        this.hideSettings();
    }

    // 显示游戏结束
    showGameOver(winner) {
        const modal = document.getElementById('gameOverModal');
        const winnerText = document.getElementById('winnerText');

        winnerText.textContent = `🎉 ${winner} 获胜！🎉`;
        modal.classList.add('show');
    }

    // 隐藏游戏结束模态框
    hideGameOverModal() {
        const modal = document.getElementById('gameOverModal');
        modal.classList.remove('show');
    }

    // 显示加载动画
    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    // 隐藏加载动画
    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    // 初始化AI徽章显示
    initializeAIBadges() {
        document.getElementById('landlordBadge').style.display =
            this.playerTypes['地主'] === 'ai' ? 'block' : 'none';
        document.getElementById('farmerABadge').style.display =
            this.playerTypes['农民甲'] === 'ai' ? 'block' : 'none';
        document.getElementById('farmerBBadge').style.display =
            this.playerTypes['农民乙'] === 'ai' ? 'block' : 'none';
    }
}

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    window.game = new DouDiZhuGame();
    // 初始化AI徽章显示状态
    window.game.initializeAIBadges();
});
