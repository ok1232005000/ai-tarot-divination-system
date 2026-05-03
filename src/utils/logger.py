"""
日志系统配置
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "tarot_system", level: str = "INFO") -> logging.Logger:
    """设置日志系统"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(
        log_dir / f"tarot_system_{today}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# 创建默认logger实例
default_logger = setup_logger()


def log_info(message: str):
    """记录信息日志"""
    default_logger.info(message)


def log_error(message: str, exception: Exception = None):
    """记录错误日志"""
    if exception:
        default_logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        default_logger.error(message)


def log_warning(message: str):
    """记录警告日志"""
    default_logger.warning(message)


def log_debug(message: str):
    """记录调试日志"""
    default_logger.debug(message)