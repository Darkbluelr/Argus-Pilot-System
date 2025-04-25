import logging

import grpc

# 导入配置 (移到顶部)
from config import settings

# 导入新的日志配置函数 (移到顶部)
from utils.logging_config import setup_logging

# 导入转换工具 (移到顶部)
from utils.proto_utils import (  # proto_struct_to_python_dict, # 未使用
    python_dict_to_proto_struct,
)

# 导入生成的 protobuf 代码
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

logger = logging.getLogger(__name__)


class ArgusClient:
    """gRPC 客户端，用于与 Argus 服务端交互。"""

    def __init__(self, server_address: str = "localhost:50051"):
        self.server_address = server_address
        self.channel = None
        self.perception_stub = None
        self.action_stub = None
        self.adapter_control_stub = None
        self._connect()

    def _connect(self):
        """建立到 gRPC 服务器的连接并创建服务存根。"""
        try:
            self.channel = grpc.insecure_channel(self.server_address)
            # 可以添加 channel readiness 检查
            # grpc.channel_ready_future(self.channel).result(timeout=10) # 等待连接就绪
            self.perception_stub = pb2_grpc.PerceptionServiceStub(self.channel)
            self.action_stub = pb2_grpc.ActionServiceStub(self.channel)
            self.adapter_control_stub = pb2_grpc.AdapterControlServiceStub(self.channel)
            logger.info(
                "Successfully connected to gRPC server at %s", self.server_address
            )
        except grpc.RpcError as e:
            logger.error(
                "Failed to connect to gRPC server at %s: %s",
                self.server_address,
                e,
                exc_info=True,
            )
            # 可以选择抛出异常或设置标志位
            self.channel = None
            raise ConnectionError(f"Failed to connect to {self.server_address}") from e

    def close(self):
        """关闭 gRPC 连接。"""
        if self.channel:
            self.channel.close()
            logger.info("gRPC channel closed.")

    # --- AdapterControlService 方法 ---
    def initialize_adapter(
        self,
        adapter_name: str,
        config: pb2.Struct,  # Changed: Expect pre-converted struct
    ) -> pb2.InitializeResponse:
        if not self.adapter_control_stub:
            raise ConnectionError("Client not connected.")
        request = pb2.InitializeRequest(
            adapter_name=adapter_name, config=config
        )  # Use passed-in struct
        logger.info("Sending Initialize request for adapter '%s'", adapter_name)
        try:
            response = self.adapter_control_stub.Initialize(request)
            logger.info(f"Initialize response: {response}")
            return response
        except grpc.RpcError as e:
            logger.error("RPC failed for Initialize: %s", e, exc_info=True)
            # 返回失败的响应或抛出异常
            return pb2.InitializeResponse(success=False, message=f"RPC Error: {e}")

    def shutdown_server(self) -> pb2.ShutdownResponse:
        if not self.adapter_control_stub:
            raise ConnectionError("Client not connected.")
        request = pb2.ShutdownRequest()
        logger.info("Sending Shutdown request")
        try:
            response = self.adapter_control_stub.Shutdown(request)
            logger.info(f"Shutdown response: {response}")
            return response
        except grpc.RpcError as e:
            logger.error("RPC failed for Shutdown: %s", e, exc_info=True)
            return pb2.ShutdownResponse(success=False, message=f"RPC Error: {e}")

    # --- PerceptionService 方法 (示例) ---
    def get_ui_snapshot(
        self, options: pb2.Struct | None = None
    ) -> pb2.UISnapshot | None:
        if not self.perception_stub:
            raise ConnectionError("Client not connected.")
        request = pb2.GetUISnapshotRequest(options=options if options else pb2.Struct())
        logger.info("Sending GetUISnapshot request")
        try:
            response = self.perception_stub.GetUISnapshot(request)
            logger.debug("GetUISnapshot response received (details omitted)")
            return response
        except grpc.RpcError as e:
            logger.error("RPC failed for GetUISnapshot: %s", e, exc_info=True)
            return None

    def find_element(
        self, query_criteria: dict, strategy: str = "xpath", max_results: int = 1
    ) -> pb2.FindElementResponse | None:
        if not self.perception_stub:
            raise ConnectionError("Client not connected.")
        # query_struct = convert_dict_to_struct(query_criteria)
        request = pb2.ElementQuery(
            strategy=strategy,
            query=query_criteria.get("value", ""),  # Example access
            # criteria=query_struct, # Needs proper implementation
            max_results=max_results,
        )
        logger.info("Sending FindElement request with strategy '%s'", strategy)
        try:
            response = self.perception_stub.FindElement(request)
            logger.debug(f"FindElement response: {response}")
            return response
        except grpc.RpcError as e:
            logger.error("RPC failed for FindElement: %s", e, exc_info=True)
            return None

    # --- ActionService 方法 (示例) ---
    def click_element(
        self, element_id: bytes, options: pb2.Struct | None = None
    ) -> pb2.ActionResult | None:
        if not self.action_stub:
            raise ConnectionError("Client not connected.")
        request = pb2.ClickRequest(
            adapter_specific_id=element_id,
            options=options if options else pb2.Struct(),
        )
        logger.info("Sending Click request")
        try:
            response = self.action_stub.Click(request)
            logger.info(f"Click response: {response}")
            return response
        except grpc.RpcError as e:
            logger.error("RPC failed for Click: %s", e, exc_info=True)
            return None

    def type_text_in_element(
        self,
        text: str,
        element_id: bytes | None = None,
        options: pb2.Struct | None = None,
    ) -> pb2.ActionResult | None:
        if not self.action_stub:
            raise ConnectionError("Client not connected.")
        request = pb2.TypeTextRequest(
            text=text, options=options if options else pb2.Struct()
        )
        if element_id:
            request.adapter_specific_id = element_id
        # Truncate long text in log message
        log_text = (text[:50] + "...") if len(text) > 50 else text
        logger.info("Sending TypeText request with text: '%s'", log_text)
        try:
            response = self.action_stub.TypeText(request)
            logger.info(f"TypeText response: {response}")
            return response
        except grpc.RpcError as e:
            logger.error("RPC failed for TypeText: %s", e, exc_info=True)
            return None


# --- 辅助函数占位符 (需要实现) ---
# def convert_dict_to_struct(py_dict):
#     pass
# def convert_struct_to_dict(proto_struct):
#     pass
# def convert_dict_to_value_map(py_dict):
#     pass

# 删除重复或移走的导入
# from config import settings # 移到顶部
# from utils.logging_config import setup_logging # 移到顶部
# from utils.proto_utils import proto_struct_to_python_dict,\
# python_dict_to_proto_struct # 移到顶部

# --- 示例用法 ---
if __name__ == "__main__":
    # 使用日志配置函数，它会从 settings 读取默认值
    setup_logging()
    # setup_logging(log_level=logging.INFO)

    client = None
    try:
        # 从配置读取服务器地址和端口
        server_addr = f"{settings.GRPC_SERVER_ADDRESS.strip('[]')}:{settings.GRPC_PORT}"
        # 处理 settings.GRPC_SERVER_ADDRESS 可能包含的 '[::]' 格式
        if settings.GRPC_SERVER_ADDRESS == "[::]":
            # 客户端连接通常用 localhost
            server_addr = f"localhost:{settings.GRPC_PORT}"
        else:
            server_addr = f"{settings.GRPC_SERVER_ADDRESS}:{settings.GRPC_PORT}"

        client = ArgusClient(server_address=server_addr)
        # client = ArgusClient() # 使用默认地址 localhost:50051

        # 示例: 初始化一个适配器
        adapter_config_dict = {"some_key": "some_value", "nested": {"level": 1}}
        # 使用转换工具
        proto_config = python_dict_to_proto_struct(adapter_config_dict)
        init_response = client.initialize_adapter(
            adapter_name="mock_adapter", config=proto_config
        )
        if init_response and init_response.success:
            logger.info("Adapter initialization successful (simulated by server).")
        else:
            logger.warning("Adapter initialization failed or returned error.")

        # 示例: 获取 UI 快照 (带选项)
        snapshot_options_dict = {"include_invisible": False, "max_depth": 5}
        proto_options = python_dict_to_proto_struct(snapshot_options_dict)
        snapshot = client.get_ui_snapshot(options=proto_options)
        if snapshot:
            logger.info(
                "Received UI Snapshot (window title: '%s')", snapshot.window_title
            )
        else:
            logger.warning("Failed to get UI snapshot.")

        # 示例: 查找元素
        query_dict = {"value": "//*[@id='button1']", "timeout": 10}
        # 注意: ElementQuery 不是 Struct, 这里只是演示转换, 实际调用不用转换
        # query_struct = python_dict_to_proto_struct(query_dict)
        find_resp = client.find_element(query_criteria=query_dict, strategy="xpath")
        if find_resp and find_resp.elements:
            found_element_id = find_resp.elements[0].adapter_specific_id
            logger.info(f"Found element with ID (bytes): {found_element_id}")

            # 示例: 点击找到的元素 (带选项)
            click_options_dict = {"button": "left", "click_count": 1}
            proto_click_options = python_dict_to_proto_struct(click_options_dict)
            click_resp = client.click_element(
                element_id=found_element_id, options=proto_click_options
            )
            if click_resp:
                logger.info(
                    "Click action result: success=%s, message='%s'",
                    click_resp.success,
                    click_resp.message,
                )

        else:
            logger.warning("Failed to find element or no elements found.")

        # 示例: 输入文本 (带选项)
        type_options_dict = {
            "delay_between_keys_ms": 50,
            "clear_before_typing": True,
        }
        proto_type_options = python_dict_to_proto_struct(type_options_dict)
        # Assume typing globally if element_id is None
        type_resp = client.type_text_in_element(
            text="Hello from Argus Client!", options=proto_type_options
        )
        if type_resp:
            logger.info(
                "TypeText action result: success=%s, message='%s'",
                type_resp.success,
                type_resp.message,
            )

        # 示例：调用服务端关闭
        # shutdown_resp = client.shutdown_server()
        # if shutdown_resp:
        #     logger.info(f"Server shutdown result: {shutdown_resp.success}")

    except ConnectionError as e:
        logger.critical(f"Connection Error: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if client:
            client.close()
