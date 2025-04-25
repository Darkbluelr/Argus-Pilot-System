# config/settings.py

import logging
import os

# --- Core Settings ---
PROJECT_NAME = "Argus Pilot System"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- gRPC Settings ---
GRPC_SERVER_ADDRESS = "[::]"  # 监听所有接口
GRPC_PORT = 50051
GRPC_MAX_WORKERS = 10

# --- Logging Settings ---
# LOG_LEVEL = logging.DEBUG # 更详细的日志
LOG_LEVEL = logging.INFO
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "argus_pilot.log")
LOG_CONSOLE_ENABLED = True
LOG_FILE_ENABLED = True
# LOG_ROTATING_FILE = False # 是否启用日志滚动
# LOG_MAX_BYTES = 10 * 1024 * 1024 # 10 MB
# LOG_BACKUP_COUNT = 5

# --- Adapter Settings ---
# ADAPTER_DISCOVERY_ENTRY_POINT = "argus_adapters"

# --- Environment Specific Settings (Example) ---
# ENVIRONMENT = os.environ.get('ARGUS_ENV', 'development')
# if ENVIRONMENT == 'production':
#     LOG_LEVEL = logging.WARNING
#     GRPC_PORT = 50050
#     # ... other production overrides

# --- Add other configurations as needed ---

# Optional: Validate settings (e.g., using Pydantic)
# from pydantic_settings import BaseSettings
# class AppSettings(BaseSettings):
#     grpc_port: int = GRPC_PORT
#     log_level: str | int = LOG_LEVEL
#     # ... define other settings
# settings = AppSettings()
# GRPC_PORT = settings.grpc_port
# LOG_LEVEL = settings.log_level
