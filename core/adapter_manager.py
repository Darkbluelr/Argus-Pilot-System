import importlib
import importlib.metadata as metadata
import logging
from typing import Dict, Optional, Tuple, Type

# 假设接口定义在 interfaces 模块中 (实际应从那里导入)
# from interfaces.perception import PerceptionAdapterInterface
# from interfaces.action import ActionAdapterInterface
# from core.exceptions import InitializationError # 假设异常定义在 core.exceptions


# --- 临时定义，直到实际文件创建 --- START
class PerceptionAdapterInterface:
    def initialize(self, config: Dict) -> None:
        pass

    def close(self) -> None:
        pass  # Ensure close method exists for unload


class ActionAdapterInterface:
    def initialize(self, config: Dict) -> None:
        pass

    def close(self) -> None:
        pass  # Ensure close method exists for unload


class InitializationError(Exception):
    pass


# --- 临时定义，直到实际文件创建 --- END

logger = logging.getLogger(__name__)

# 定义适配器对的类型别名
AdapterPair = Tuple[
    Optional[PerceptionAdapterInterface], Optional[ActionAdapterInterface]
]
AdapterClassPair = Tuple[
    Optional[Type[PerceptionAdapterInterface]], Optional[Type[ActionAdapterInterface]]
]


class AdapterManager:
    """
    负责发现、加载和管理应用程序适配器 (插件)。
    使用 Python Entry Points (`argus_adapters`) 进行发现。
    """

    def __init__(self):
        self._registered_adapters: Dict[str, AdapterClassPair] = {}
        self._loaded_instances: Dict[str, AdapterPair] = {}
        self._discover_adapters()

    def _discover_adapters(self) -> None:
        """
        发现系统中所有可用的适配器。
        通过查找 `argus_adapters` entry point group 实现。
        期望 entry point value 是一个字典，包含 perception 和 action 类的路径字符串。
        例如: {
            'perception': 'my_adapter.perception:MyPerceptionAdapter',
            'action': 'my_adapter.action:MyActionAdapter'
        }
        """
        logger.info(
            "Discovering available adapters via 'argus_adapters' entry points..."
        )
        self._registered_adapters = {}
        try:
            entry_points = metadata.entry_points(group="argus_adapters")
            for entry_point in entry_points:
                adapter_name = entry_point.name
                logger.debug(f"Processing entry point: {adapter_name}")
                try:
                    adapter_config_dict = entry_point.load()
                    if not isinstance(adapter_config_dict, dict):
                        logger.warning(
                            f"Skipping adapter '{adapter_name}': Entry point "
                            f"value is not a dict ({type(adapter_config_dict)})."
                        )
                        continue

                    perception_cls_path = adapter_config_dict.get("perception")
                    action_cls_path = adapter_config_dict.get("action")

                    perception_cls: Optional[Type[PerceptionAdapterInterface]] = None
                    action_cls: Optional[Type[ActionAdapterInterface]] = None

                    if perception_cls_path:
                        logger.debug(
                            "Attempting to load Perception class from: %s",
                            perception_cls_path,
                        )
                        perception_cls = self._load_class_from_path(
                            perception_cls_path, PerceptionAdapterInterface
                        )
                        if not perception_cls:
                            logger.warning(
                                "Failed to load Perception class for adapter '%s' "
                                "from '%s'.",
                                adapter_name,
                                perception_cls_path,
                            )
                            # Decide if loading should continue without perception

                    if action_cls_path:
                        logger.debug(
                            "Attempting to load Action class from: %s", action_cls_path
                        )
                        action_cls = self._load_class_from_path(
                            action_cls_path, ActionAdapterInterface
                        )
                        if not action_cls:
                            logger.warning(
                                "Failed to load Action class for adapter '%s' "
                                "from '%s'.",
                                adapter_name,
                                action_cls_path,
                            )
                            # Decide if loading should continue without action

                    # 必须至少有一个适配器类被成功加载
                    if perception_cls or action_cls:
                        if adapter_name in self._registered_adapters:
                            logger.warning(
                                "Overwriting previously registered adapter: %s",
                                adapter_name,
                            )
                        self._registered_adapters[adapter_name] = (
                            perception_cls,
                            action_cls,
                        )
                        logger.info(
                            "Successfully registered adapter: '%s' "
                            "(Perception: %s, Action: %s)",
                            adapter_name,
                            bool(perception_cls),
                            bool(action_cls),
                        )
                    else:
                        logger.warning(
                            "Failed to load any class for adapter '%s'. "
                            "Skipping registration.",
                            adapter_name,
                        )

                except Exception as e:
                    logger.error(
                        "Failed to load or register adapter '%s' due to error: %s",
                        adapter_name,
                        e,
                        exc_info=True,
                    )

        except Exception as e:
            logger.error(
                "Error discovering adapters via entry points: %s", e, exc_info=True
            )

        if not self._registered_adapters:
            logger.warning(
                "No valid adapters discovered via 'argus_adapters' entry points."
            )
        else:
            logger.info(
                "Adapter discovery finished. Registered adapters: %s",
                list(self._registered_adapters.keys()),
            )

    def _load_class_from_path(
        self, class_path: str, expected_interface: Type
    ) -> Optional[Type]:
        """
        辅助函数：根据字符串路径加载类，并检查其是否实现了预期接口。
        :param class_path: 类的路径字符串 (例如 'module.submodule:ClassName').
        :param expected_interface: 期望该类实现的 ABC 接口。
        :return: 加载的类，如果失败或类型不匹配则返回 None。
        """
        try:
            module_path, class_name = class_path.rsplit(":", 1)
            module = importlib.import_module(module_path)
            loaded_class = getattr(module, class_name)

            if not issubclass(loaded_class, expected_interface):
                logger.error(
                    "Class '%s' does not implement the expected interface '%s'.",
                    class_path,
                    expected_interface.__name__,
                )
                return None

            return loaded_class
        except ModuleNotFoundError:
            logger.error(
                "Module not found for class path '%s'. Ensure the package is "
                "installed and path is correct.",
                class_path,
            )
            return None
        except AttributeError:
            logger.error(
                "Class '%s' not found in module '%s'.", class_name, module_path
            )
            return None
        except Exception as e:
            logger.error(
                "Failed to load class from path '%s': %s",
                class_path,
                e,
                exc_info=True,
            )
            return None

    def get_adapter(self, app_name: str, config: Optional[Dict] = None) -> AdapterPair:
        """
        获取指定应用程序的适配器实例。
        如果尚未加载，则尝试加载和初始化。
        :param app_name: 应用程序的名称 (应与适配器注册的名称匹配)。
        :param config: 传递给适配器 initialize 方法的配置字典。
        :return: 一个包含 Perception 和 Action 适配器实例的元组 (可能为 None)。
        :raises ValueError: 如果找不到已注册的适配器。
        :raises InitializationError: 如果适配器初始化失败。
        """
        if app_name in self._loaded_instances:
            logger.debug("Returning cached adapter instance for '%s'.", app_name)
            return self._loaded_instances[app_name]

        if app_name not in self._registered_adapters:
            logger.error("No registered adapter found for application: %s", app_name)
            # Consider fallback mechanisms or raising a more specific error
            raise ValueError(
                f"Adapter for '{app_name}' not registered or failed to load."
            )

        logger.info("Loading and initializing adapter for '%s'...", app_name)
        perception_cls, action_cls = self._registered_adapters[app_name]
        perception_instance: Optional[PerceptionAdapterInterface] = None
        action_instance: Optional[ActionAdapterInterface] = None
        adapter_config = config or {}

        try:
            # Initialize perception adapter if class exists
            if perception_cls:
                perception_instance = perception_cls()
                perception_config = adapter_config.get("perception", {})
                perception_instance.initialize(perception_config)
                logger.debug("Initialized PerceptionAdapter for %s", app_name)
            else:
                logger.debug("No PerceptionAdapter class registered for %s", app_name)

            # Initialize action adapter if class exists
            if action_cls:
                action_instance = action_cls()
                action_config = adapter_config.get("action", {})
                action_instance.initialize(action_config)
                logger.debug("Initialized ActionAdapter for %s", app_name)
            else:
                logger.debug("No ActionAdapter class registered for %s", app_name)

            # Store the pair (even if one is None)
            self._loaded_instances[app_name] = (perception_instance, action_instance)
            logger.info("Successfully loaded adapter pair for '%s'.", app_name)
            return perception_instance, action_instance

        except InitializationError as e:
            logger.error(
                "Initialization failed for adapter '%s': %s",
                app_name,
                e,
                exc_info=True,
            )
            if app_name in self._loaded_instances:
                del self._loaded_instances[app_name]
            raise  # Re-raise specific InitializationError
        except Exception as e:
            logger.error(
                "Unexpected error during adapter initialization for '%s': %s",
                app_name,
                e,
                exc_info=True,
            )
            if app_name in self._loaded_instances:
                del self._loaded_instances[app_name]
            # Consider raising a more generic error or returning None pair
            raise InitializationError(
                f"Unexpected error during adapter initialization for {app_name}"
            ) from e

    def list_available_adapters(self) -> list[str]:
        """返回所有已发现并成功注册的适配器名称列表。"""
        return list(self._registered_adapters.keys())

    def unload_adapter(self, app_name: str) -> None:
        """
        卸载指定应用程序的适配器实例。
        会调用适配器的 close 方法（如果存在）。
        :param app_name: 要卸载的适配器名称。
        :raises ValueError: 如果适配器未加载。
        """
        if app_name not in self._loaded_instances:
            logger.warning(
                "Attempted to unload adapter '%s', but it was not loaded.", app_name
            )
            return
            # Or raise ValueError(f"Adapter '{app_name}' is not currently loaded.")

        logger.info("Unloading adapter for '%s'...", app_name)
        perception_instance, action_instance = self._loaded_instances.pop(app_name)

        try:
            if perception_instance and hasattr(perception_instance, "close"):
                logger.debug("Closing PerceptionAdapter for %s...", app_name)
                perception_instance.close()
        except Exception as e:
            logger.error(
                "Error closing PerceptionAdapter for '%s': %s",
                app_name,
                e,
                exc_info=True,
            )

        try:
            if action_instance and hasattr(action_instance, "close"):
                logger.debug("Closing ActionAdapter for %s...", app_name)
                action_instance.close()
        except Exception as e:
            logger.error(
                "Error closing ActionAdapter for '%s': %s",
                app_name,
                e,
                exc_info=True,
            )

        logger.info("Successfully unloaded adapter for '%s'.", app_name)

    def unload_all_adapters(self) -> None:
        """卸载所有当前加载的适配器实例。"""
        logger.info("Unloading all loaded adapters...")
        # Create a copy of keys to avoid RuntimeError during iteration
        loaded_adapter_names = list(self._loaded_instances.keys())
        for app_name in loaded_adapter_names:
            self.unload_adapter(app_name)
        logger.info("Finished unloading all adapters.")

    def get_loaded_adapters(self) -> Dict[str, AdapterPair]:
        """返回当前加载的适配器实例字典。"""
        return self._loaded_instances.copy()

    def get_registered_adapters(self) -> Dict[str, AdapterClassPair]:
        """返回已注册的适配器类字典。"""
        return self._registered_adapters.copy()

    def is_adapter_loaded(self, app_name: str) -> bool:
        """检查指定名称的适配器当前是否已加载。"""
        return app_name in self._loaded_instances

    def is_adapter_registered(self, app_name: str) -> bool:
        """检查指定名称的适配器是否已被发现和注册。"""
        return app_name in self._registered_adapters

    # Potential enhancements:
    # - Add configuration validation logic (e.g., using Pydantic)
    # - Implement adapter lifecycle hooks (pre_init, post_init, pre_close, post_close)
    # - Add adapter dependency management
    # - Support for reloading adapters without restarting the application (complex)


# 示例用法 (用于测试)
if __name__ == "__main__":
    # 配置基本日志记录
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("\n--- Initializing Adapter Manager (will discover installed adapters) ---")
    manager = AdapterManager()
    print(f"Available registered adapters: {manager.list_available_adapters()}")
    print("--- Adapter Manager Initialized ---\n")

    # --- 模拟获取适配器 (你需要安装一个提供 'argus_adapters' 入口点的包才能成功) ---
    MOCK_APP_NAME = (
        "example_adapter"  # 假设你有一个叫这个名字的适配器通过 entry point 注册了
    )
    print(f"--- Attempting to get adapter: {MOCK_APP_NAME} ---")
    try:
        perception_adapter, action_adapter = manager.get_adapter(
            MOCK_APP_NAME, config={"perception": {"api_key": "123"}}
        )
        if perception_adapter or action_adapter:
            print(f"Adapter '{MOCK_APP_NAME}' loaded successfully.")
            # 提取表达式到临时变量以满足行长限制
            perception_type_name = (
                type(perception_adapter).__name__ if perception_adapter else "None"
            )
            print(f"Perception Adapter Type: {perception_type_name}")
            action_type_name = (
                type(action_adapter).__name__ if action_adapter else "None"
            )
            print(f"  Action Adapter Type: {action_type_name}")
        else:
            # 提取 f-string 的内容以满足行长限制
            log_message_part1 = f"Adapter '{MOCK_APP_NAME}' entry point found,"
            log_message_part2 = " but no classes loaded (check logs)."
            print(log_message_part1 + log_message_part2)

        # 尝试再次获取，应从缓存返回
        # 提取 f-string 的内容以满足行长限制
        log_message_again_part1 = f"\n--- Attempting to get adapter '{MOCK_APP_NAME}'"
        log_message_again_part2 = " again (should be cached) ---"
        print(log_message_again_part1 + log_message_again_part2)
        manager.get_adapter(MOCK_APP_NAME)

    except ValueError as e:
        # 提取 f-string 的内容以满足行长限制
        error_message_part1 = "Caught expected ValueError"
        error_message_part2 = " (Adapter probably not installed or registered):"
        print(f"{error_message_part1}{error_message_part2} {e}")
    except InitializationError as e:
        print(f"Caught InitializationError for '{MOCK_APP_NAME}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred getting '{MOCK_APP_NAME}': {e}")
    print("--- Adapter Get Attempt Finished ---\n")

    # --- 尝试获取不存在的适配器 ---
    NON_EXISTENT_APP = "non_existent_adapter"
    print(f"--- Attempting to get non-existent adapter: {NON_EXISTENT_APP} ---")
    try:
        manager.get_adapter(NON_EXISTENT_APP)
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    print("--- Non-existent Adapter Get Attempt Finished ---\n")

    # --- 清理 ---
    print("--- Unloading Adapters ---")
    manager.unload_all_adapters()
    print("--- Adapters Unloaded ---")
