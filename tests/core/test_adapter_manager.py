# import importlib.metadata # F401 Unused import
from unittest.mock import MagicMock, patch

import pytest

# 模块相对于项目根目录的路径
from core.adapter_manager import (
    ActionAdapterInterface,
    AdapterManager,
    InitializationError,
    PerceptionAdapterInterface,
)


# --- Mock Adapters --- (可以放在 conftest.py 中共享)
class MockPerception(PerceptionAdapterInterface):
    def initialize(self, config: dict) -> None:
        print(f"MockPerception initialized with {config}")

    def close(self) -> None:
        print("MockPerception closed")

    # 实现其他必要方法...


class MockAction(ActionAdapterInterface):
    def initialize(self, config: dict) -> None:
        print(f"MockAction initialized with {config}")

    def close(self) -> None:
        print("MockAction closed")

    # 实现其他必要方法...


class MockAdapterSetValid:
    # 这个类用于模拟 entry_point.load() 的返回值
    # 它返回一个包含有效类路径的字典
    def load(self):
        # 使用类的实际可导入路径
        return {
            "perception": "tests.core.test_adapter_manager.MockPerception",
            "action": "tests.core.test_adapter_manager.MockAction",
        }


class MockAdapterSetOnlyPerception:
    def load(self):
        return {
            "perception": "tests.core.test_adapter_manager.MockPerception"
            # 'action' is missing
        }


class MockAdapterSetInvalidPath:
    def load(self):
        return {"perception": "non.existent.path.MockPerception"}


class MockEntryPoint:
    def __init__(self, name, value):
        self.name = name
        self.value = value  # value 现在是一个类，其实例有 load() 方法

    def load(self):
        # 直接返回模拟类的实例，模仿 importlib.metadata 返回 EntryPoint 对象
        # 但 AdapterManager 期望 self.value 是类路径字符串或字典
        # 为了适配 AdapterManager 的 _discover_adapters,
        # 我们让 value 是一个能 .load() 的类实例
        instance = self.value()
        return instance.load()


# --- Pytest Fixtures --- (可以放在 conftest.py 中共享)
@pytest.fixture
def manager():
    """Provides a fresh AdapterManager instance for each test."""
    # 使用 patch 来模拟 importlib.metadata.entry_points
    with patch("importlib.metadata.entry_points") as mock_ep:
        # 设置默认返回空列表，除非在测试中被覆盖
        mock_ep.return_value = []
        yield AdapterManager()  # Pass patched context to constructor if needed
        # No teardown needed for simple manager


# --- Test Cases ---
def test_adapter_manager_initialization(manager):
    """Test that AdapterManager initializes correctly."""
    assert manager is not None
    # Initial state after __init__ which calls _discover_adapters
    assert manager._registered_adapters == {}
    assert manager._loaded_instances == {}


def test_discovery_no_entry_points(manager):
    """Test discovery when no entry points are found (default fixture mock)."""
    # Fixture already mocks entry_points to return []
    manager._discover_adapters()  # Call again to ensure it handles empty state
    assert manager._registered_adapters == {}


def test_discovery_valid_entry_point(manager):
    """Test discovery with a valid entry point."""
    mock_entry_point = MockEntryPoint(name="valid_adapter", value=MockAdapterSetValid)
    # We need to patch entry_points within this test scope
    with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
        manager._discover_adapters()

    assert "valid_adapter" in manager._registered_adapters
    perception_cls, action_cls = manager._registered_adapters["valid_adapter"]
    assert perception_cls is MockPerception
    assert action_cls is MockAction


def test_discovery_entry_point_loads_dict(manager):
    """Test discovery when entry point value is a dict (as expected by code)."""
    # 这个测试更接近代码实际处理逻辑
    mock_ep_value = {
        "perception": "tests.core.test_adapter_manager.MockPerception",
        "action": "tests.core.test_adapter_manager.MockAction",
    }
    # 模拟 entry_points 返回一个 MagicMock EntryPoint，其 .load() 返回字典
    mock_ep = MagicMock(name="dict_adapter")
    mock_ep.load.return_value = mock_ep_value
    with patch("importlib.metadata.entry_points", return_value=[mock_ep]):
        manager._discover_adapters()

    assert "dict_adapter" in manager._registered_adapters
    perception_cls, action_cls = manager._registered_adapters["dict_adapter"]
    assert perception_cls is MockPerception
    assert action_cls is MockAction


def test_discovery_invalid_class_path(manager, caplog):
    """Test discovery when class path is invalid."""
    mock_entry_point = MockEntryPoint(
        name="invalid_path", value=MockAdapterSetInvalidPath
    )
    with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
        manager._discover_adapters()

    assert "invalid_path" not in manager._registered_adapters  # 应该加载失败
    assert "Module not found" in caplog.text  # Check for specific log message


def test_get_adapter_not_discovered(manager):
    """Test getting an adapter that hasn't been discovered."""
    with pytest.raises(ValueError, match=r"Adapter for 'non_existent' not registered"):
        manager.get_adapter("non_existent")


def test_get_adapter_successful_instantiation(manager):
    """Test successfully getting and instantiating an adapter."""
    mock_entry_point = MockEntryPoint(name="valid_adapter", value=MockAdapterSetValid)
    with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
        manager._discover_adapters()  # Discover first

    config = {"key": "value"}
    perception_instance, action_instance = manager.get_adapter(
        "valid_adapter", config=config
    )

    assert isinstance(perception_instance, MockPerception)
    assert isinstance(action_instance, MockAction)
    # Check internal state for loaded instances
    assert manager._loaded_instances["valid_adapter"] == (
        perception_instance,
        action_instance,
    )

    # Test caching - getting the same adapter again should return the same instances
    perception_instance_2, action_instance_2 = manager.get_adapter(
        "valid_adapter", config=config
    )
    assert perception_instance is perception_instance_2
    assert action_instance is action_instance_2


def test_get_adapter_instantiation_failure(manager):
    """Test adapter instantiation failure during get_adapter."""
    # Mock the initialize method to raise an error
    with patch(
        "tests.core.test_adapter_manager.MockPerception.initialize",
        side_effect=InitializationError("Init failed"),  # Use specific error type
    ):
        mock_entry_point = MockEntryPoint(
            name="fail_adapter", value=MockAdapterSetValid
        )
        with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
            manager._discover_adapters()

        with pytest.raises(
            InitializationError,
            match=r"Initialization failed for adapter 'fail_adapter'",
        ):
            manager.get_adapter("fail_adapter")

    # Ensure failed instance is not cached
    assert "fail_adapter" not in manager._loaded_instances


def test_unload_adapter(manager):
    """Test unloading an adapter."""
    mock_entry_point = MockEntryPoint(name="unload_test", value=MockAdapterSetValid)
    with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
        manager._discover_adapters()

        # Get adapter to create instances
        p_inst, a_inst = manager.get_adapter("unload_test")
        assert "unload_test" in manager._loaded_instances

        # Mock the close methods to check they are called
        p_inst.close = MagicMock()
        a_inst.close = MagicMock()

        manager.unload_adapter("unload_test")

        p_inst.close.assert_called_once()
        a_inst.close.assert_called_once()
        assert "unload_test" not in manager._loaded_instances


def test_unload_non_existent_adapter(manager, caplog):
    """Test unloading an adapter that was never loaded."""
    # Should not raise an error, but log a warning
    manager.unload_adapter("non_existent")
    assert "Attempted to unload adapter 'non_existent'" in caplog.text
    assert "non_existent" not in manager._loaded_instances


def test_unload_adapter_close_failure(manager, caplog):
    """Test unloading when an adapter's close method fails."""
    mock_entry_point = MockEntryPoint(name="close_fail", value=MockAdapterSetValid)
    with patch("importlib.metadata.entry_points", return_value=[mock_entry_point]):
        manager._discover_adapters()
        p_inst, a_inst = manager.get_adapter("close_fail")

        # Mock close methods to raise errors
        error_msg_p = "Perception close failed"
        error_msg_a = "Action close failed"
        p_inst.close = MagicMock(side_effect=Exception(error_msg_p))
        a_inst.close = MagicMock(side_effect=Exception(error_msg_a))

        manager.unload_adapter("close_fail")

        # Check that close was called despite errors
        p_inst.close.assert_called_once()
        a_inst.close.assert_called_once()
        # Check that errors were logged
        assert (
            f"Error closing PerceptionAdapter for 'close_fail': {error_msg_p}"
            in caplog.text
        )
        assert (
            f"Error closing ActionAdapter for 'close_fail': {error_msg_a}"
            in caplog.text
        )
        # Check instance was still removed from cache
        assert "close_fail" not in manager._loaded_instances
