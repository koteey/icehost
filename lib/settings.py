import json
import os
import time
from .logger import logger

START_TIME = time.time()

def load_settings():
    """Загружает настройки из файла"""
    default_settings = {
        'prefix': '.',
        'custom_messages': {
            'info': """👤 **Информация о профиле**
• Имя: {user_name}
• ID: {user_id}
• Онлайн: {online_status}

⚙️ **Системная информация**
• ОС: {os_info}
• Python: {python_version}
• Архитектура: {architecture}

🤖 **Icers**
• Разработчик: SnowCode
• Версия: 2.0
• Аптайм: {uptime}
• Статус: Активен ✅""",
            'ping': """🏓 **Пинг**

🌐 Сетевая задержка: {ping}ms
⏱️ Аптайм: {uptime}
✅ Статус: Бот активен

💫 Качество соединения: {quality}"""
        },
        'info_style': 'custom',  # custom, full, minimal, system, user, bot
        'ping_style': 'custom',  # custom, detailed, simple, network
        'modules': {}
    }
    
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as f:
                saved_settings = json.load(f)
                # Объединяем с настройки по умолчанию
                return {**default_settings, **saved_settings}
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
    
    return default_settings

def save_settings(settings):
    """Сохраняет настройки в файл"""
    try:
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек: {e}")
        return False

def load_hotkeys():
    """Загружает хоткеи из файла"""
    try:
        if os.path.exists('hotkeys.json'):
            with open('hotkeys.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки хоткеев: {e}")
    return {}

def save_hotkeys(hotkeys):
    """Сохраняет хоткеи в файл"""
    try:
        with open('hotkeys.json', 'w', encoding='utf-8') as f:
            json.dump(hotkeys, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения хоткеев: {e}")