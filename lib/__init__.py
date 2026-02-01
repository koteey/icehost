# Библиотека Icers

# Конфигурация
from .config import load_config

# Настройки
from .settings import (
    load_settings, save_settings, 
    load_hotkeys, save_hotkeys
)

# Модули
from .modules import (
    load_modules, get_module_commands,
    install_module_from_file, delete_module
)

# ВК утилиты
from .vk_utils import (
    get_message_sender, measure_network_latency
)

# Системные утилиты
from .system_utils import (
    get_uptime, get_connection_quality,
    get_module_utils, module_log
)

# Файловые утилиты
from .file_utils import download_file

# Бэкапы
from .backup_utils import create_backup, restore_backup

# Логгер
from .logger import logger

__version__ = '2.0'
__author__ = 'SnowCode'

__all__ = [
    # Конфигурация
    'load_config',
    
    # Настройки
    'load_settings', 'save_settings',
    'load_hotkeys', 'save_hotkeys',
    
    # Модули
    'load_modules', 'get_module_commands',
    'install_module_from_file', 'delete_module',
    
    # ВК утилиты
    'get_message_sender', 'measure_network_latency',
    
    # Системные утилиты
    'get_uptime', 'get_connection_quality',
    'get_module_utils', 'module_log',
    
    # Файловые утилиты
    'download_file',
    
    # Бэкапы
    'create_backup', 'restore_backup',
    
    # Логгер
    'logger'
]