import logging
import threading

# import time # 未使用
from concurrent import futures

import grpc

# 导入配置 (移到底部，仅在 __main__ 中使用)
from config import settings

# 导入日志配置 (移到底部，仅在 __main__ 中使用)
from utils.logging_config import setup_logging

# 导入转换工具 (移到顶部)
from utils.proto_utils import proto_struct_to_python_dict, python_dict_to_proto_struct

# from google.protobuf.struct_pb2 import Struct  # 未直接使用，通过转换函数间接使用


# 导入生成的 protobuf 代码
# 假设 generated_protobuf 在项目根目录下，并且已添加 __init__.py
# 如果你的项目结构不同，需要调整这里的导入路径
try:
    import generated_protobuf.core_services_pb2 as pb2
    import generated_protobuf.core_services_pb2_grpc as pb2_grpc
except ImportError:
    print("Error: Could not import generated protobuf files.")
    print("Please ensure you have run the protobuf compilation step and")
    print(
        "that the generated_protobuf directory is in your Python path or project root."
    )
    exit(1)

# 导入接口定义（用于类型提示和模拟逻辑，实际服务实现应与适配器交互）
# from interfaces.perception import PerceptionAdapterInterface
# from interfaces.action import ActionAdapterInterface


# --- 临时定义，直到实际文件创建 --- START
class PerceptionAdapterInterface:
    def initialize(self, config: dict) -> None:
        pass

    def get_ui_snapshot(self, options: dict) -> pb2.UISnapshot:
        return pb2.UISnapshot()

    def find_element(self, query: pb2.ElementQuery) -> pb2.FindElementResponse:
        return pb2.FindElementResponse()

    def find_elements(self, query: pb2.ElementQuery) -> pb2.FindElementsResponse:
        return pb2.FindElementsResponse()

    def get_element_state(self, element_id: bytes) -> dict:
        return {}

    def get_element_text(self, element_id: bytes) -> str | None:
        return None

    def get_focused_element(self) -> pb2.UIElement | None:
        return None

    def close(self) -> None:
        pass


class ActionAdapterInterface:
    def initialize(self, config: dict) -> None:
        pass

    def click(self, element_id: bytes, options: dict) -> pb2.ActionResult:
        return pb2.ActionResult(success=False, message="Not implemented")

    def type_text(
        self, text: str, element_id: bytes | None, options: dict
    ) -> pb2.ActionResult:
        return pb2.ActionResult(success=False, message="Not implemented")

    def scroll(
        self, direction: str, magnitude: int, element_id: bytes | None, options: dict
    ) -> pb2.ActionResult:
        return pb2.ActionResult(success=False, message="Not implemented")

    def press_key(self, key_combination: str, options: dict) -> pb2.ActionResult:
        return pb2.ActionResult(success=False, message="Not implemented")

    def drag_and_drop(
        self,
        source_element_id: bytes,
        target_element_id: bytes | None,
        target_coords: tuple | None,
        options: dict,
    ) -> pb2.ActionResult:
        return pb2.ActionResult(success=False, message="Not implemented")

    def execute_native_command(
        self, command_name: str, params: dict
    ) -> pb2.ActionResult:
        return pb2.ActionResult(success=False, message="Not implemented")

    def close(self) -> None:
        pass


# 模拟适配器实例 (实际应由 AdapterManager 提供)
global_mock_perception_adapter = PerceptionAdapterInterface()
global_mock_action_adapter = ActionAdapterInterface()
# --- 临时定义 --- END

# 移除重复导入
# from utils.proto_utils import proto_struct_to_python_dict, python_dict_to_proto_struct

logger = logging.getLogger(__name__)

# --- 服务实现类 (Servicers) ---


class PerceptionServiceImpl(pb2_grpc.PerceptionServiceServicer):
    """实现 PerceptionService 定义的 RPC 方法。"""

    def GetUISnapshot(
        self, request: pb2.GetUISnapshotRequest, context
    ) -> pb2.UISnapshot:
        logger.info("RPC: GetUISnapshot received")
        # 使用转换工具处理 options
        options_dict = proto_struct_to_python_dict(request.options)
        logger.debug(f"GetUISnapshot options: {options_dict}")
        snapshot = global_mock_perception_adapter.get_ui_snapshot(options=options_dict)
        logger.debug("RPC: GetUISnapshot returning snapshot (details omitted)")
        return snapshot

    def FindElement(
        self, request: pb2.ElementQuery, context
    ) -> pb2.FindElementResponse:
        logger.info("RPC: FindElement received")
        # 实际应调用对应适配器的 find_element
        response = global_mock_perception_adapter.find_element(request)
        logger.debug(f"RPC: FindElement returning: {response}")
        return response

    def FindElements(
        self, request: pb2.ElementQuery, context
    ) -> pb2.FindElementsResponse:
        logger.info("RPC: FindElements received")
        # 实际应调用对应适配器的 find_elements
        response = global_mock_perception_adapter.find_elements(request)
        logger.debug(
            f"RPC: FindElements returning elements count: {len(response.elements)}"
        )
        return response

    def GetElementState(
        self, request: pb2.GetElementStateRequest, context
    ) -> pb2.GetElementStateResponse:
        logger.info("RPC: GetElementState received")
        state_dict = global_mock_perception_adapter.get_element_state(
            request.adapter_specific_id
        )
        # 使用转换工具将 dict 转换为 Struct 下的 Value map (通过 Struct 转换间接实现)
        response_state_struct = python_dict_to_proto_struct(state_dict or {})
        logger.debug("RPC: GetElementState returning state (details omitted)")
        # GetElementStateResponse 需要 map<string, Value>, Struct 内部就是这个结构
        return pb2.GetElementStateResponse(state=response_state_struct.fields)

    def GetElementText(
        self, request: pb2.GetElementTextRequest, context
    ) -> pb2.GetElementTextResponse:
        logger.info("RPC: GetElementText received")
        # 实际应调用对应适配器的 get_element_text
        text = global_mock_perception_adapter.get_element_text(
            request.adapter_specific_id
        )
        logger.debug(f"RPC: GetElementText returning: {text}")
        return pb2.GetElementTextResponse(text=text)

    def GetFocusedElement(
        self, request: pb2.GetFocusedElementRequest, context
    ) -> pb2.GetFocusedElementResponse:
        logger.info("RPC: GetFocusedElement received")
        # 实际应调用对应适配器的 get_focused_element
        element = global_mock_perception_adapter.get_focused_element()
        logger.debug(f"RPC: GetFocusedElement returning: {element}")
        return pb2.GetFocusedElementResponse(element=element)


class ActionServiceImpl(pb2_grpc.ActionServiceServicer):
    """实现 ActionService 定义的 RPC 方法。"""

    def Click(self, request: pb2.ClickRequest, context) -> pb2.ActionResult:
        logger.info("RPC: Click received")
        options_dict = proto_struct_to_python_dict(request.options)
        logger.debug(f"Click options: {options_dict}")
        result = global_mock_action_adapter.click(
            request.adapter_specific_id, options=options_dict
        )
        logger.debug(f"RPC: Click returning: {result}")
        return result

    def TypeText(self, request: pb2.TypeTextRequest, context) -> pb2.ActionResult:
        logger.info("RPC: TypeText received")
        options_dict = proto_struct_to_python_dict(request.options)
        logger.debug(f"TypeText options: {options_dict}")
        element_id = (
            request.adapter_specific_id
            if request.HasField("adapter_specific_id")
            else None
        )
        result = global_mock_action_adapter.type_text(
            request.text, element_id, options=options_dict
        )
        logger.debug(f"RPC: TypeText returning: {result}")
        return result

    def Scroll(self, request: pb2.ScrollRequest, context) -> pb2.ActionResult:
        logger.info("RPC: Scroll received")
        options_dict = proto_struct_to_python_dict(request.options)
        logger.debug(f"Scroll options: {options_dict}")
        element_id = (
            request.adapter_specific_id
            if request.HasField("adapter_specific_id")
            else None
        )
        result = global_mock_action_adapter.scroll(
            request.direction, request.magnitude, element_id, options=options_dict
        )
        logger.debug(f"RPC: Scroll returning: {result}")
        return result

    def PressKey(self, request: pb2.PressKeyRequest, context) -> pb2.ActionResult:
        logger.info("RPC: PressKey received")
        options_dict = proto_struct_to_python_dict(request.options)
        logger.debug(f"PressKey options: {options_dict}")
        result = global_mock_action_adapter.press_key(
            request.key_combination, options=options_dict
        )
        logger.debug(f"RPC: PressKey returning: {result}")
        return result

    def DragAndDrop(self, request: pb2.DragAndDropRequest, context) -> pb2.ActionResult:
        logger.info("RPC: DragAndDrop received")
        options_dict = proto_struct_to_python_dict(request.options)
        logger.debug(f"DragAndDrop options: {options_dict}")
        target_id = None
        target_coords = None
        if request.HasField("target_adapter_specific_id"):
            target_id = request.target_adapter_specific_id
        elif request.HasField("target_coords"):
            target_coords = (request.target_coords.x, request.target_coords.y)
        result = global_mock_action_adapter.drag_and_drop(
            request.source_adapter_specific_id,
            target_id,
            target_coords,
            options=options_dict,
        )
        logger.debug(f"RPC: DragAndDrop returning: {result}")
        return result

    def ExecuteNativeCommand(
        self, request: pb2.ExecuteNativeCommandRequest, context
    ) -> pb2.ActionResult:
        logger.info("RPC: ExecuteNativeCommand received")
        params_dict = proto_struct_to_python_dict(request.params)
        logger.debug(f"ExecuteNativeCommand params: {params_dict}")
        result = global_mock_action_adapter.execute_native_command(
            request.command_name, params=params_dict
        )
        logger.debug(f"RPC: ExecuteNativeCommand returning: {result}")
        return result


class AdapterControlServiceImpl(pb2_grpc.AdapterControlServiceServicer):
    """实现 AdapterControlService 定义的 RPC 方法。"""

    def Initialize(
        self, request: pb2.InitializeRequest, context
    ) -> pb2.InitializeResponse:
        logger.info("RPC: Initialize received")
        adapter_name = request.adapter_name
        config_dict = proto_struct_to_python_dict(request.config)
        logger.debug(
            f"Initialize request for adapter '{adapter_name}' with config {config_dict}"
        )
        try:
            # 这里应该调用实际的 AdapterManager 来加载和初始化
            # 暂时使用全局模拟适配器进行模拟
            if adapter_name == "mock_adapter":  # 仅模拟 mock_adapter
                global_mock_perception_adapter.initialize(
                    config_dict.get("perception", {})
                )
                global_mock_action_adapter.initialize(config_dict.get("action", {}))
                logger.info(f"Mock adapter '{adapter_name}' initialized successfully.")
                return pb2.InitializeResponse(success=True, message="Initialized mock")
            else:
                logger.warning(
                    f"Adapter '{adapter_name}' not found for initialization."
                )
                return pb2.InitializeResponse(
                    success=False, message=f"Adapter '{adapter_name}' not found"
                )
        except Exception as e:
            logger.error(
                f"Error initializing adapter '{adapter_name}': {e}", exc_info=True
            )
            return pb2.InitializeResponse(success=False, message=f"Error: {e}")

    def Shutdown(self, request: pb2.ShutdownRequest, context) -> pb2.ShutdownResponse:
        logger.info("RPC: Shutdown received. Scheduling server stop...")
        # 在新线程中延迟停止服务器，以便响应可以发送回去
        threading.Thread(target=schedule_server_stop).start()
        return pb2.ShutdownResponse(success=True, message="Server shutdown initiated")


# 引用全局服务器实例 (稍后在 serve 函数中创建)
server_instance = None


def schedule_server_stop():
    """延迟停止服务器。"""
    global server_instance
    if server_instance:
        logger.info("Stopping server gracefully...")
        server_instance.stop(grace=1)  # 等待1秒让响应发送
        logger.info("Server stopped.")


def serve(port: int = 50051, workers: int = 10):
    """启动 gRPC 服务器。"""
    global server_instance
    server_instance = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))

    # 注册服务实现者
    pb2_grpc.add_PerceptionServiceServicer_to_server(
        PerceptionServiceImpl(), server_instance
    )
    pb2_grpc.add_ActionServiceServicer_to_server(ActionServiceImpl(), server_instance)
    pb2_grpc.add_AdapterControlServiceServicer_to_server(
        AdapterControlServiceImpl(), server_instance
    )

    # 监听端口
    listen_addr = f"[::]:{port}"  # 监听所有接口
    server_instance.add_insecure_port(listen_addr)

    # 启动服务器
    logger.info(f"Starting gRPC server on {listen_addr}...")
    server_instance.start()
    logger.info("Server started. Waiting for termination signal...")
    try:
        # 保持主线程活动，直到服务器被外部停止（例如通过 Shutdown RPC）
        server_instance.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, stopping server...")
        server_instance.stop(0)  # 立即停止


if __name__ == "__main__":
    # 使用日志配置函数
    setup_logging()
    # setup_logging(log_level=logging.DEBUG) # 如果需要更详细的日志

    # 从配置读取端口
    grpc_port = settings.GRPC_PORT
    serve(port=grpc_port)
