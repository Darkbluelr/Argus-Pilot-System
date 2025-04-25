# utils/proto_utils.py

import logging

from google.protobuf.json_format import MessageToDict, ParseDict

# from google.protobuf.struct_pb2 import ListValue, Value # F401 Unused import
from google.protobuf.struct_pb2 import Struct

logger = logging.getLogger(__name__)


def python_dict_to_proto_struct(py_dict: dict) -> Struct:
    """将 Python 字典递归转换为 Protobuf Struct。

    Args:
        py_dict: 要转换的 Python 字典。

    Returns:
        转换后的 Protobuf Struct。
    """
    proto_struct = Struct()
    try:
        # google.protobuf.json_format.ParseDict handles nested structures and types
        ParseDict(py_dict, proto_struct)
    except Exception as e:
        logger.error(
            "Error converting Python dict to Protobuf Struct: %s", e, exc_info=True
        )
        # Return an empty struct or raise an error depending on desired behavior
        return Struct()
    return proto_struct


def proto_struct_to_python_dict(proto_struct: Struct) -> dict:
    """将 Protobuf Struct 递归转换为 Python 字典。

    Args:
        proto_struct: 要转换的 Protobuf Struct。

    Returns:
        转换后的 Python 字典。
    """
    try:
        # google.protobuf.json_format.MessageToDict handles nested structures and types
        # Use `preserving_proto_field_name=True` to keep original field names
        py_dict = MessageToDict(proto_struct, preserving_proto_field_name=True)
        return py_dict
    except Exception as e:
        logger.error(
            "Error converting Protobuf Struct to Python dict: %s", e, exc_info=True
        )
        # Return an empty dict or raise an error
        return {}


# --- 示例用法和简单测试 ---
if __name__ == "__main__":
    from utils.logging_config import setup_logging

    setup_logging(log_level=logging.DEBUG)

    test_dict = {
        "string_key": "hello_world",
        "int_key": 123,
        "float_key": 45.67,
        "bool_key_true": True,
        "bool_key_false": False,
        "null_key": None,
        "list_key": [1, "two", 3.0, True, None, {"nested_in_list": "yes"}],
        "nested_dict_key": {
            "nested_str": "I am nested",
            "nested_int": 999,
            "deeply_nested": {"deep_list": [10, 20]},
        },
    }

    logger.info("--- Testing python_dict_to_proto_struct ---")
    struct_result = python_dict_to_proto_struct(test_dict)
    logger.info(f"Original Dict: {test_dict}")
    logger.info(f"Converted Struct:\n{struct_result}")
    # Basic check
    assert struct_result.fields["string_key"].string_value == "hello_world"
    assert struct_result.fields["int_key"].number_value == 123
    assert len(struct_result.fields["list_key"].list_value.values) == 6
    assert (
        struct_result.fields["nested_dict_key"]
        .struct_value.fields["nested_int"]
        .number_value
        == 999
    )
    logger.info("python_dict_to_proto_struct basic checks passed.")

    logger.info("\n--- Testing proto_struct_to_python_dict ---")
    dict_result = proto_struct_to_python_dict(struct_result)
    logger.info(f"Converted back to Dict: {dict_result}")
    # Basic check (might have float precision differences)
    assert dict_result["string_key"] == "hello_world"
    assert dict_result["int_key"] == 123
    assert dict_result["bool_key_true"] is True
    assert dict_result["null_key"] is None
    assert len(dict_result["list_key"]) == 6
    assert dict_result["list_key"][5]["nested_in_list"] == "yes"
    assert dict_result["nested_dict_key"]["nested_str"] == "I am nested"
    assert dict_result["nested_dict_key"]["deeply_nested"]["deep_list"] == [10, 20]
    logger.info("proto_struct_to_python_dict basic checks passed.")

    # Test edge cases
    logger.info("\n--- Testing Edge Cases ---")
    empty_struct = python_dict_to_proto_struct({})
    assert proto_struct_to_python_dict(empty_struct) == {}
    logger.info("Empty dict conversion passed.")

    struct_from_empty = Struct()
    assert proto_struct_to_python_dict(struct_from_empty) == {}
    logger.info("Empty struct conversion passed.")
