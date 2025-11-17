import logging
import sys
from datetime import datetime

class Logger:
    """简单的日志工具类"""
    
    def __init__(self, name: str = "LLMDOUDIZHU", log_file: str = None, level=logging.INFO):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            log_file: 日志文件路径，如果为None则只输出到控制台
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了文件）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """严重错误"""
        self.logger.critical(message)


# 创建全局日志器实例
logger = Logger(log_file="game.log")


# 使用示例
if __name__ == '__main__':
    # 基本使用
    logger.info("游戏开始")
    logger.debug("这是调试信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    # 替代print的用法
    player = "地主"
    cards = ['♦3', '♥4', '♠5']
    logger.info(f"{player} 出牌: {cards}")
    
    # 不同级别的日志
    logger.info("=" * 50)
    logger.info("游戏状态更新")
    logger.error("出牌失败：牌型不匹配")
