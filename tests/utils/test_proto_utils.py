# tests/utils/test_proto_utils.py
import pytest
from google.protobuf.struct_pb2 import Struct

from utils.proto_utils import proto_struct_to_python_dict, python_dict_to_proto_struct

# --- Test Data ---
TEST_CASES = [
    ("empty", {}, {}),
    ("simple", {"a": 1, "b": "hello"}, {"a": 1, "b": "hello"}),
    (
        "types",
        {
            "string": "world",
            "integer": 100,
            "floating": 12.34,
            "boolean_true": True,
            "boolean_false": False,
            "null_value": None,
        },
        {
            "string": "world",
            "integer": 100,
            "floating": 12.34,
            "boolean_true": True,
            "boolean_false": False,
            "null_value": None,
        },
    ),
    (
        "list",
        {"my_list": [1, "a", True, None, 3.14]},
        {"my_list": [1, "a", True, None, 3.14]},
    ),
    (
        "nested_dict",
        {
            "level1": {"str": "nested", "int": 5, "list": [False, None]},
            "top_level": True,
        },
        {
            "level1": {"str": "nested", "int": 5, "list": [False, None]},
            "top_level": True,
        },
    ),
    (
        "list_with_dict",
        {"items": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]},
        {"items": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]},
    ),
]


@pytest.mark.parametrize("name, py_dict, expected_dict", TEST_CASES)
def test_dict_to_struct_and_back(name, py_dict, expected_dict):
    """Test converting dict to struct and back to dict matches expected."""
    # Convert to Struct
    proto_struct = python_dict_to_proto_struct(py_dict)

    # Convert back to Dict
    result_dict = proto_struct_to_python_dict(proto_struct)

    # Assert deep equality
    assert result_dict == expected_dict, f"Test case '{name}' failed."


def test_struct_to_dict_empty():
    """Test converting an empty Struct."""
    empty_struct = Struct()
    result = proto_struct_to_python_dict(empty_struct)
    assert result == {}


# 可以添加更多针对无效输入的测试，但 json_format 库已处理大部分情况
