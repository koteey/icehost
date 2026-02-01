import platform
import time
from .logger import logger

START_TIME = time.time()

def get_uptime():
    """Возвращает время работы бота в читаемом формате"""
    uptime_seconds = time.time() - START_TIME
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    if hours > 0:
        return f"{hours}ч {minutes}м {seconds}с"
    elif minutes > 0:
        return f"{minutes}м {seconds}с"
    else:
        return f"{seconds}с"

def get_connection_quality(latency):
    """Определяет качество соединения по задержке"""
    if latency < 100:
        return "Отличное 🟢"
    elif latency < 300:
        return "Хорошее 🟡"
    elif latency < 500:
        return "Удовлетворительное 🟠"
    else:
        return "Медленное 🔴"

def get_module_utils():
    """
    Возвращает утилиты для использования в модулях
    """
    from .vk_utils import measure_network_latency
    from .file_utils import download_file
    from .settings import save_settings, load_settings
    from .backup_utils import create_backup, restore_backup
    
    return {
        'get_uptime': get_uptime,
        'measure_network_latency': measure_network_latency,
        'get_connection_quality': get_connection_quality,
        'download_file': download_file,
        'save_settings': save_settings,
        'load_settings': load_settings,
        'module_log': module_log,
        'create_backup': create_backup,
        'restore_backup': restore_backup,
        'logger': logger
    }

def module_log(module_name, message):
    """
    Логирование для модулей
    """
    logger.info(f"[{module_name}] {message}")