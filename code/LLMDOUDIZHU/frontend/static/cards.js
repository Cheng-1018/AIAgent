// 扑克牌工具类
class CardUtils {
    // 花色映射
    static SUITS = {
        '♠': 'black',
        '♥': 'red',
        '♦': 'red',
        '♣': 'black'
    };

    // 牌值映射
    static CARD_VALUES = {
        '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15, '小王': 16, '大王': 17
    };

    /**
     * 解析牌面信息
     * @param {string} card - 牌的字符串表示，如 "♠3", "小王"
     * @returns {object} - {suit: 花色, value: 牌值, color: 颜色}
     */
    static parseCard(card) {
        if (card === '小王') {
            return {
                suit: '',
                value: '小王',
                color: 'joker-small',
                displayValue: '小王',
                displaySuit: ''
            };
        }

        if (card === '大王') {
            return {
                suit: '',
                value: '大王',
                color: 'joker-big',
                displayValue: '大王',
                displaySuit: ''
            };
        }

        // 提取花色和数值
        let suit = '';
        let value = card;

        for (let s of ['♠', '♥', '♦', '♣']) {
            if (card.includes(s)) {
                suit = s;
                value = card.replace(s, '');
                break;
            }
        }

        return {
            suit: suit,
            value: value,
            color: this.SUITS[suit] || 'black',
            displayValue: value,
            displaySuit: suit
        };
    }

    /**
     * 创建扑克牌DOM元素
     * @param {string} card - 牌的字符串表示
     * @param {boolean} selectable - 是否可选择
     * @returns {HTMLElement} - 牌的DOM元素
     */
    static createCardElement(card, selectable = true) {
        const cardInfo = this.parseCard(card);
        const cardDiv = document.createElement('div');
        cardDiv.className = `card ${cardInfo.color}`;
        cardDiv.dataset.card = card;

        if (cardInfo.color.startsWith('joker')) {
            // 王牌特殊显示
            const valueDiv = document.createElement('div');
            valueDiv.className = 'card-value';
            valueDiv.textContent = cardInfo.displayValue;
            cardDiv.appendChild(valueDiv);
        } else {
            // 普通牌显示
            const valueDiv = document.createElement('div');
            valueDiv.className = 'card-value';
            valueDiv.textContent = cardInfo.displayValue;

            const suitDiv = document.createElement('div');
            suitDiv.className = 'card-suit';
            suitDiv.textContent = cardInfo.displaySuit;

            cardDiv.appendChild(valueDiv);
            cardDiv.appendChild(suitDiv);
        }

        if (selectable) {
            cardDiv.addEventListener('click', function () {
                this.classList.toggle('selected');
            });
        }

        return cardDiv;
    }

    /**
     * 创建牌背面元素
     * @returns {HTMLElement} - 牌背面DOM元素
     */
    static createCardBackElement() {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card card-back';
        cardDiv.innerHTML = '<div class="card-value">🂠</div>';
        return cardDiv;
    }

    /**
     * 渲染玩家手牌
     * @param {HTMLElement} container - 容器元素
     * @param {Array<string>} cards - 牌数组
     * @param {boolean} selectable - 是否可选择
     */
    static renderCards(container, cards, selectable = true) {
        container.innerHTML = '';

        if (!cards || cards.length === 0) {
            return;
        }

        cards.forEach(card => {
            const cardElement = this.createCardElement(card, selectable);
            container.appendChild(cardElement);
        });
    }

    /**
     * 渲染牌背（用于其他玩家）
     * @param {HTMLElement} container - 容器元素
     * @param {number} count - 牌的数量
     */
    static renderCardBacks(container, count) {
        container.innerHTML = '';

        for (let i = 0; i < count; i++) {
            const cardBack = this.createCardBackElement();
            container.appendChild(cardBack);
        }
    }

    /**
     * 获取选中的牌
     * @param {HTMLElement} container - 容器元素
     * @returns {Array<string>} - 选中的牌数组
     */
    static getSelectedCards(container) {
        const selectedCards = container.querySelectorAll('.card.selected');
        return Array.from(selectedCards).map(card => card.dataset.card);
    }

    /**
     * 清除所有选中状态
     * @param {HTMLElement} container - 容器元素
     */
    static clearSelection(container) {
        const selectedCards = container.querySelectorAll('.card.selected');
        selectedCards.forEach(card => card.classList.remove('selected'));
    }

    /**
     * 排序牌（按牌值）
     * @param {Array<string>} cards - 牌数组
     * @returns {Array<string>} - 排序后的牌数组
     */
    static sortCards(cards) {
        return cards.sort((a, b) => {
            const valueA = this.getCardValue(a);
            const valueB = this.getCardValue(b);
            return valueA - valueB;
        });
    }

    /**
     * 获取牌的数值（用于排序）
     * @param {string} card - 牌的字符串表示
     * @returns {number} - 牌的数值
     */
    static getCardValue(card) {
        const cardInfo = this.parseCard(card);
        return this.CARD_VALUES[cardInfo.value] || 0;
    }

    /**
     * 渲染出牌区域（缩小版卡片）
     * @param {HTMLElement} container - 容器元素
     * @param {Array<string>} cards - 牌数组
     */
    static renderPlayedCards(container, cards) {
        container.innerHTML = '';

        if (!cards || cards.length === 0) {
            return;
        }

        cards.forEach(card => {
            const cardElement = this.createCardElement(card, false);
            // 为出牌区域的卡片添加特殊样式
            cardElement.classList.add('played-card');
            container.appendChild(cardElement);
        });
    }
}

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CardUtils;
}
