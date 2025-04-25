import logging

# import time  # For simulating work in stop - Unused
from enum import Enum, auto
from typing import Any, Dict, Optional

# 假设 AdapterManager 定义在 core.adapter_manager
# ActionAdapterInterface, - Unused in this file;
# PerceptionAdapterInterface, - Unused in this file
from core.adapter_manager import AdapterManager, AdapterPair

logger = logging.getLogger(__name__)


class EngineState(Enum):
    """引擎运行状态"""

    IDLE = auto()  # 初始化完成，未启动
    STARTING = auto()  # 正在启动中
    RUNNING = auto()  # 正在运行，可以接受任务
    STOPPING = auto()  # 正在停止中
    STOPPED = auto()  # 已完全停止
    ERROR = auto()  # 发生未恢复的错误


class CoreEngine:
    """
    GCC 核心引擎。
    负责协调感知、认知、行动的循环，并管理 Agent 生命周期。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        logger.info("Initializing Core Engine...")
        self._state = EngineState.IDLE
        self.config = config or {}
        try:
            # 初始化适配器管理器
            self.adapter_manager = AdapterManager()
            # 其他组件将在后续任务中初始化 (认知模块, 记忆模块, DKG 管理器等)
            self.cognitive_module = None  # Placeholder
            self.memory_module = None  # Placeholder
            self.dkg_manager = None  # Placeholder
            self._active_adapters: Dict[str, AdapterPair] = {}
            logger.info("Core Engine initialized successfully. State: IDLE")
        except Exception as e:
            logger.error(f"Core Engine initialization failed: {e}", exc_info=True)
            self._state = EngineState.ERROR
            # Propagate the error or handle it based on policy
            raise

    def get_status(self) -> EngineState:
        """获取当前引擎状态"""
        return self._state

    def start(self) -> None:
        """
        启动引擎。
        目前仅改变状态，为未来启动后台任务循环做准备。
        """
        if self._state not in [EngineState.IDLE, EngineState.STOPPED]:
            logger.warning("Cannot start engine from state: %s", self._state.name)
            return

        logger.info("Starting Core Engine...")
        self._state = EngineState.STARTING
        # 在这里可以启动后台线程/进程来运行主事件循环或任务队列
        # ... simulation of startup tasks ...
        self._state = EngineState.RUNNING
        logger.info("Core Engine started successfully. State: %s", self._state.name)

    def stop(self, timeout: float = 10.0) -> None:
        """
        停止引擎并清理资源。
        :param timeout: 等待后台任务（如果存在）正常停止的超时时间（秒）。
        """
        if self._state not in [
            EngineState.RUNNING,
            EngineState.STARTING,
            EngineState.ERROR,
        ]:
            logger.warning("Cannot stop engine from state: %s", self._state.name)
            # If already stopping or stopped, do nothing
            if self._state in [EngineState.STOPPING, EngineState.STOPPED]:
                return
            # If idle, just move to stopped
            if self._state == EngineState.IDLE:
                self._state = EngineState.STOPPED
                logger.info("Engine was idle, moved directly to STOPPED state.")
                return

        logger.info("Stopping Core Engine...")
        self._state = EngineState.STOPPING

        # 1. 通知后台任务停止 (如果存在)
        #    例如: self._main_loop_thread.stop_event.set()

        # 2. 等待后台任务结束 (如果存在)
        #    例如: self._main_loop_thread.join(timeout)
        #    if self._main_loop_thread.is_alive():
        #        logger.warning(
        #           "Engine main loop did not stop gracefully within timeout."
        #        )
        logger.debug("Simulating graceful shutdown wait (up to %ss)...", timeout)
        # time.sleep(min(1, timeout)) # Simulate some shutdown activity

        # 3. 执行清理操作
        self.shutdown()
        # Note: shutdown() already sets state to STOPPED if called directly,
        # We set it again here to ensure correct state after stop() sequence.
        self._state = EngineState.STOPPED
        logger.info("Core Engine stopped. State: %s", self._state.name)

    def _get_or_load_adapters(self, app_name: str) -> AdapterPair:
        """
        获取或加载指定应用的适配器。
        这是引擎与适配器管理器交互的核心点 (T1.2.1)。
        """
        if self._state != EngineState.RUNNING:
            logger.error(
                "Cannot load adapters when engine state is %s", self._state.name
            )
            raise RuntimeError(f"Engine is not running (state: {self._state.name})")

        if app_name in self._active_adapters:
            return self._active_adapters[app_name]
        else:
            try:
                # 从配置中获取特定于应用的适配器配置 (如果存在)
                adapter_config = self.config.get("adapters", {}).get(app_name, {})
                logger.info("Requesting adapters for '%s' from manager...", app_name)
                perception_adapter, action_adapter = self.adapter_manager.get_adapter(
                    app_name, config=adapter_config
                )

                # 基本检查，确保至少有一个适配器被加载
                if not perception_adapter and not action_adapter:
                    # 这通常不应发生，get_adapter 会在失败时引发异常
                    raise RuntimeError(
                        f"Adapter manager returned no adapters for {app_name} "
                        f"without raising an error."
                    )

                self._active_adapters[app_name] = (perception_adapter, action_adapter)
                logger.info("Successfully obtained adapters for '%s'.", app_name)
                return perception_adapter, action_adapter
            except ValueError as e:
                logger.error("Adapter not found for '%s': %s", app_name, e)
                self._state = EngineState.ERROR  # Potentially move to error state
                raise
            except Exception as e:
                # 捕获初始化错误等
                logger.error(
                    "Failed to get or load adapters for '%s': %s",
                    app_name,
                    e,
                    exc_info=True,
                )
                self._state = EngineState.ERROR  # Move to error state
                raise

    def run_task(self, task_description: str, target_app: str) -> None:
        """
        (示例方法) 运行一个简单的任务。
        后续会实现完整的 Perception-Cognition-Action 循环。
        """
        if self._state != EngineState.RUNNING:
            logger.error(
                "Cannot run task: Engine is not in RUNNING state (current: %s).",
                self._state.name,
            )
            return

        logger.info(
            "Starting task: '%s' on application '%s'",
            task_description,
            target_app,
        )
        try:
            perception_adapter, action_adapter = self._get_or_load_adapters(target_app)

            if not perception_adapter:
                logger.error(
                    "Cannot perform task: Perception adapter for '%s' "
                    "is missing or failed to load.",
                    target_app,
                )
                # Consider setting engine state to ERROR here?
                return
            if not action_adapter:
                logger.error(
                    "Cannot perform task: Action adapter for '%s' "
                    "is missing or failed to load.",
                    target_app,
                )
                # Consider setting engine state to ERROR here?
                return

            logger.info("Starting Perception-Cognition-Action loop (placeholder)...")

            # --- 1. 感知 (Perception) ---
            if self._state != EngineState.RUNNING:
                return  # Check state before long operation
            logger.debug("Step 1: Performing perception...")
            # snapshot = perception_adapter.get_ui_snapshot()
            # logger.debug(f"Got snapshot: {snapshot}") # 可能非常冗长
            logger.debug("Perception step placeholder completed.")

            # --- 2. 认知 (Cognition) ---
            if self._state != EngineState.RUNNING:
                return  # Check state before long operation
            logger.debug("Step 2: Performing cognition (planning)...")
            # action_plan = self.cognitive_module.plan(
            #    task_description, snapshot, memory_context, dkg_context)
            # logger.debug(f"Generated action plan: {action_plan}")
            logger.debug("Cognition step placeholder completed.")

            # --- 3. 行动 (Action) ---
            if self._state != EngineState.RUNNING:
                return  # Check state before long operation
            logger.debug("Step 3: Executing action...")
            # result = action_adapter.click(...) # 基于 action_plan
            # logger.debug(f"Action result: {result}")
            logger.debug("Action step placeholder completed.")

            # --- 循环、错误处理、反思等 ---
            if self._state != EngineState.RUNNING:
                return  # Final check

            logger.info("Task '%s' placeholder execution finished.", task_description)

        except Exception as e:
            logger.error("Error during task execution: %s", e, exc_info=True)
            self._state = EngineState.ERROR  # Move to error state on task failure
            # 可能需要进行错误恢复或反思

    def shutdown(self) -> None:
        """
        内部清理方法，由 stop() 调用或在初始化失败时调用。
        """
        logger.debug("Executing internal shutdown sequence...")
        # 卸载所有适配器
        if hasattr(self, "adapter_manager"):
            self.adapter_manager.unload_all_adapters()
        # 关闭其他模块 (如果需要)
        # if self.dkg_manager and hasattr(self.dkg_manager, 'close'):
        #    self.dkg_manager.close()
        logger.debug("Internal shutdown sequence completed.")
        # Note: The final state (STOPPED or ERROR) is typically set by the caller


# 示例用法 (用于测试)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    engine_config = {
        "adapters": {
            "mock_adapter": {
                "perception": {"config_key_p": "value_p"},
                "action": {"config_key_a": "value_a"},
            }
        }
    }

    # Example of dynamically adding an entry point (for testing)
    # This usually happens when a package is installed
    class MockPerception:
        def initialize(self, config):
            print(f"MockPerception Initialized with: {config}")

        def close(self):
            print("MockPerception Closed")

    class MockAction:
        def initialize(self, config):
            print(f"MockAction Initialized with: {config}")

        def close(self):
            print("MockAction Closed")

    def mock_entry_point():
        return {
            "perception": "__main__:MockPerception",
            "action": "__main__:MockAction",
        }

    # Simulate entry point registration (crude way for testing)
    import importlib.metadata as metadata  # Need metadata for patching
    import sys

    class MockEntryPoint:
        name = "mock_adapter"

        def load(self):
            return mock_entry_point()

    if "__main__" in sys.modules:
        # Ensure the mock classes are findable by _load_class_from_path
        setattr(sys.modules["__main__"], "MockPerception", MockPerception)
        setattr(sys.modules["__main__"], "MockAction", MockAction)
        # Simulate metadata.entry_points behavior
        original_entry_points = metadata.entry_points

        def mocked_entry_points(**kwargs):
            if kwargs.get("group") == "argus_adapters":
                return [MockEntryPoint()]
            return original_entry_points(**kwargs)

        metadata.entry_points = mocked_entry_points

    # --- End of mock setup ---

    engine = CoreEngine(config=engine_config)
    print(f"Available adapters: {engine.adapter_manager.list_available_adapters()}")

    engine.start()
    print(f"Engine status: {engine.get_status()}")

    try:
        engine.run_task("Perform a mock action", "mock_adapter")
    except Exception as e:
        print(f"Task failed: {e}")

    engine.stop()
    print(f"Engine status: {engine.get_status()}")

    # Restore original entry_points if mocked
    if "original_entry_points" in locals():
        metadata.entry_points = original_entry_points
