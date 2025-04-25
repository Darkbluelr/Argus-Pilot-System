# Argus Pilot System

构建一个模块化、可扩展的通用计算机控制框架，实现通过适配器控制不同应用程序。

## 项目目标

(在此处详细描述项目目标和愿景)

## 主要特性

*   模块化设计
*   适配器架构
*   gRPC 通信
*   ...

## 安装与运行

### 环境设置

1.  **创建 Conda 环境 (推荐):**
    ```bash
    conda create -n aps python=3.12 # 或者 >= 3.10
    conda activate aps
    ```
2.  **安装依赖:**
    ```bash
    # 进入项目根目录
    cd path/to/OzBomboR
    # 安装核心依赖和开发工具 (包括 CLI)
    pip install -e .
    # 如果有额外的开发依赖，可以安装
    # pip install -e '.[development]'
    ```

### 运行

1.  **生成 Protobuf 代码 (如果 .proto 文件有改动):**
    ```bash
    python -m grpc_tools.protoc -I./protos --python_out=./generated_protobuf --pyi_out=./generated_protobuf --grpc_python_out=./generated_protobuf protos/*.proto
    ```
2.  **通过命令行接口 (CLI):**
    *   **启动 gRPC 服务器:**
        ```bash
        argus-cli start-server
        ```
    *   **列出已注册的适配器:**
        ```bash
        argus-cli list-adapters
        ```
    *   **获取帮助:**
        ```bash
        argus-cli --help
        ```
3.  **(旧方式/备用) 直接运行脚本:**
    ```bash
    # 运行服务端
    # python core/grpc_server.py
    # 运行客户端示例 (需要先启动服务端)
    # python core/grpc_client.py
    ```

## 目录结构

(在此处简要说明项目目录结构)

```bash
# 示例
conda create -n aps python=3.12
conda activate aps
pip install -r requirements.txt
# 运行服务端
python core/grpc_server.py
# 运行客户端示例
python core/grpc_client.py
```

## 贡献指南

请参考 `CONTRIBUTING.md` (如果适用)。

## 许可证

(在此处说明项目使用的许可证, 例如 MIT License)
