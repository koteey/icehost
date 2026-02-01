"""
Система цветного логирования для Icers
"""

import sys
import os

# ANSI цветовые коды
COLORS = {
    'к': '\033[91m',      # красный
    'о': '\033[38;5;214m', # оранжевый
    'зл': '\033[38;5;220m', # золотой
    'ж': '\033[93m',      # желтый
    'з': '\033[92m',      # зеленый
    'г': '\033[96m',      # голубой
    'с': '\033[94m',      # синий
    'ф': '\033[95m',      # фиолетовый
    'б': '\033[97m',      # белый
    'ср': '\033[90m',     # серый
    'сс': '\033[37m',     # светлосерый
    'reset': '\033[0m',
}

class ColorLogger:
    def __init__(self, use_colors=True):
        self.use_colors = use_colors
        self.colors = COLORS if self.use_colors else {k: '' for k in COLORS.keys()}
        
        # Для Windows
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
    
    def _colorize(self, text, color_code):
        """Применяет цвет к тексту"""
        if not self.use_colors or not color_code:
            return text
        return f"{color_code}{text}{self.colors['reset']}"
    
    def log(self, message, *args, **kwargs):
        """Основной метод логирования"""
        print(message, flush=True)
    
    def startup(self, bot_name, bot_last_name):
        """Логирование запуска бота"""
        icers = self._colorize("Icers", self.colors['г'])
        success = self._colorize("запущен успешно.", self.colors['з'])
        self.log(f"{icers} {success}")
        
        auth = self._colorize("Авторизован успешно.", self.colors['ср'])
        self.log(f"{auth}")
    
    def message_received(self, msg_type, user_info, bot_info, message_text, is_own_message=False):
        """Логирование полученного сообщения"""
        # Определяем цвет сообщения
        if is_own_message:
            msg_color = self.colors['г']  # голубой для своих
        else:
            msg_color = self.colors['о']  # оранжевый для чужих
        
        # Берем первые 5 символов сообщения
        if message_text:
            display_text = message_text[:5]
            if len(message_text) > 5:
                display_text += "..."
        else:
            display_text = ""
        
        # Форматируем имена
        user_display = f"{user_info.get('first_name', '?')} {user_info.get('last_name', '')}".strip()
        bot_display = f"{bot_info.get('first_name', '?')} {bot_info.get('last_name', '')}".strip()
        
        # Цвета имен
        user_color = self.colors['о']  # голубой для собеседника
        bot_color = self.colors['г']   # оранжевый для бота
        
        # Собираем сообщение
        if msg_type == "лс":
            prefix = self._colorize("[лс]", self.colors['ж'])
        else:
            prefix = self._colorize("[беседа]", self.colors['с'])
        
        separator = self._colorize("|", self.colors['б'])
        user_colored = self._colorize(user_display, user_color)
        slash = self._colorize("/", self.colors['б'])
        bot_colored = self._colorize(bot_display, bot_color)
        msg_colored = self._colorize(display_text, msg_color)
        
        # Выводим
        self.log(f"{prefix} {separator} ({user_colored} {slash} {bot_colored}) {msg_colored}")
    
    def message_processed(self, msg_type, success=True, error=None):
        """Логирование обработки сообщения"""
        if success:
            processed = self._colorize(f"Обработано ({msg_type})", self.colors['сс'])
            self.log(processed)
        else:
            error_msg = self._colorize(f"Ошибка ({msg_type}): {error}", self.colors['к'])
            self.log(error_msg)
    
    def error(self, error_message):
        """Только критические ошибки"""
        if "Ошибка редактирования" not in error_message:  # Фильтруем обычные ошибки редактирования
            error_msg = self._colorize(f"Ошибка: {error_message}", self.colors['к'])
            self.log(error_msg)
    
    def warning(self, warning_message):
        """Предупреждения - не выводим"""
        pass
    
    def info(self, info_message):
        """Информационные сообщения - не выводим"""
        pass
    
    def debug(self, debug_message):
        """Отладочные сообщения - не выводим"""
        pass
    
    def module_loaded(self, module_name, description):
        """Загрузка модулей - не выводим"""
        pass
    
    def hotkey_used(self, original, transformed):
        """Использование хоткеев - не выводим"""
        pass

# Глобальный экземпляр логгера
logger = ColorLogger(use_colors=True)