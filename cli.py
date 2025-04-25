import argparse
import logging

from config.settings import settings  # 导入配置

# 假设核心模块可以这样导入 (根据实际结构调整)
from core.adapter_manager import AdapterManager
from core.grpc_server import GrpcServer
from utils.logging_config import setup_logging  # 导入日志配置

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)


def start_server_command(args):
    """处理启动服务器的命令"""
    logger.info("Attempting to start gRPC server...")
    try:
        # 这里假设 GrpcServer 可以直接实例化并启动
        # 你可能需要传入 AdapterManager 或其他依赖
        # TODO: 确认 GrpcServer 的实例化和启动方式
        manager = AdapterManager()  # 示例：可能需要 manager
        server = GrpcServer(
            adapter_manager=manager, host=settings.GRPC_HOST, port=settings.GRPC_PORT
        )
        server.start()
        # 注意: server.start() 通常会阻塞，需要考虑如何在 CLI 中处理
        # 可能需要一个 server.serve() 或类似的方法，并在后台运行？
        # 或者 start() 本身就在后台线程启动？需要查看 GrpcServer 实现
        logger.info(f"gRPC server started on {settings.GRPC_HOST}:{settings.GRPC_PORT}")
        # 如果 server.start() 阻塞，下面的代码可能不会执行
        # 可以考虑添加 server.wait_for_termination() 如果有的话
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {e}", exc_info=True)


def list_adapters_command(args):
    """处理列出适配器的命令"""
    logger.info("Listing available registered adapters...")
    try:
        manager = AdapterManager()
        available_adapters = manager.list_available_adapters()
        if available_adapters:
            print("Available adapters:")
            for adapter_name in available_adapters:
                print(f"- {adapter_name}")
        else:
            print("No adapters discovered or registered.")
    except Exception as e:
        logger.error(f"Failed to list adapters: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(
        description="Argus Pilot System Command Line Interface."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- start-server command ---
    parser_start = subparsers.add_parser("start-server", help="Start the gRPC server.")
    # 可以为 start-server 添加更多参数，例如 --host, --port
    parser_start.set_defaults(func=start_server_command)

    # --- list-adapters command ---
    parser_list = subparsers.add_parser(
        "list-adapters", help="List available registered adapters."
    )
    parser_list.set_defaults(func=list_adapters_command)

    # 解析参数
    args = parser.parse_args()

    # 根据命令执行相应的函数
    if hasattr(args, "func"):
        args.func(args)
    else:
        # 如果没有输入子命令，打印帮助信息
        parser.print_help()


if __name__ == "__main__":
    main()
