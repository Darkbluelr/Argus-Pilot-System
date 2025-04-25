import logging
import logging.config
import os

# 导入配置
from config import settings

# # 日志文件默认存放目录 (项目根目录下 logs/) # 改为从配置读取
# DEFAULT_LOG_DIR = os.path.join(os.path.dirname\
# (os.path.dirname(os.path.abspath(__file__))), 'logs')
# DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, 'argus_pilot.log')


def setup_logging(
    # 从配置读取默认值
    log_level: str | int = settings.LOG_LEVEL,
    log_dir: str = settings.LOG_DIR,
    log_file: str = settings.LOG_FILE,
    console_logging: bool = settings.LOG_CONSOLE_ENABLED,
    file_logging: bool = settings.LOG_FILE_ENABLED,
):
    """配置全局日志记录。

    Args:
        log_level: 日志级别 (例如 logging.DEBUG, logging.INFO, 'INFO').
        log_dir: 日志文件存放目录。
        log_file: 日志文件名。
        console_logging: 是否启用控制台日志输出。
        file_logging: 是否启用文件日志输出。
    """
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    handlers = {}

    # --- Formatter --- 定义日志格式
    log_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Console Handler --- 控制台输出
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": log_level,
        }

    # --- File Handler --- 文件输出
    if file_logging:
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        # 使用 RotatingFileHandler 进行日志滚动
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": log_file,
            "encoding": "utf-8",
            "level": log_level,
            "maxBytes": settings.LOG_FILE_MAX_BYTES,  # 从配置读取
            "backupCount": settings.LOG_FILE_BACKUP_COUNT,  # 从配置读取
        }

    # --- Logging Configuration Dictionary --- 使用 dictConfig 配置
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,  # 不禁用已存在的 logger
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            # 可以添加其他格式
        },
        "handlers": handlers,
        "loggers": {
            # 可以为特定模块配置不同的日志级别或 handler
            # 'core.adapter_manager': {
            #     'handlers': list(handlers.keys()), # 使用已配置的 handler
            #     'level': logging.DEBUG, # 例如让适配器管理器输出更详细的日志
            #     'propagate': False, # 不传递给 root logger
            # },
        },
        "root": {
            # 配置根 logger
            "handlers": list(handlers.keys()),
            "level": log_level,
        },
    }

    try:
        logging.config.dictConfig(logging_config)
        if console_logging or file_logging:
            logging.info("Logging configured successfully.")
            if file_logging:
                logging.info(f"Log file located at: {log_file}")
        else:
            print("Warning: No logging handlers enabled (console or file).")
    except Exception as e:
        # 如果日志配置失败，使用 basicConfig 作为备用
        print(
            f"Error configuring logging with dictConfig: {e}. "
            f"Falling back to basicConfig."
        )
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# --- 示例用法 ---
if __name__ == "__main__":
    print("Setting up logging using defaults from config/settings.py...")
    # 现在直接调用即可，默认值来自 settings
    setup_logging()
    logging.debug("This is a debug message.")  # 是否显示取决于 settings.LOG_LEVEL
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")

    print("\nSetting up logging with DEBUG level and console only...")
    setup_logging(log_level=logging.DEBUG, file_logging=False, console_logging=True)
    logging.debug("This debug message should now be visible on console.")
    logging.info("Info message (console only).")

    print(f"\nCheck the log file at: {settings.LOG_FILE}")
