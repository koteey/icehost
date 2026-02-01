import json
from lib.settings import save_settings, save_hotkeys, load_settings
from .set_cmd import process_set_command

def process(command, settings, hotkeys, vk, message_id, peer_id):
    """Обрабатывает команды настроек"""
    parts = command.split()
    
    if len(parts) == 1:
        # Показать текущие настройки
        return show_current_settings(settings)
    
    elif len(parts) >= 2:
        action = parts[1]
        
        if action == 'prefix' and len(parts) == 3:
            new_prefix = parts[2]
            if len(new_prefix) == 1 and new_prefix not in [' ', '\n', '\t']:
                old_prefix = settings['prefix']
                settings['prefix'] = new_prefix
                if save_settings(settings):
                    # Обновляем хоткеи с новым префиксом
                    updated_hotkeys = {}
                    for alias, cmd in hotkeys.items():
                        if cmd.startswith(old_prefix):
                            updated_hotkeys[alias] = new_prefix + cmd[1:]
                        else:
                            updated_hotkeys[alias] = cmd
                    hotkeys.clear()
                    hotkeys.update(updated_hotkeys)
                    save_hotkeys(hotkeys)
                    
                    return f"✅ Префикс изменен: '{old_prefix}' → '{new_prefix}'"
                else:
                    return "❌ Ошибка сохранения настроек"
            else:
                return "❌ Префикс должен быть одним символом (не пробел или табуляция)"
        
        elif action == 'info' and len(parts) == 3:
            style = parts[2]
            valid_styles = ['custom', 'full', 'minimal', 'system', 'user', 'bot']
            if style in valid_styles:
                settings['info_style'] = style
                if save_settings(settings):
                    return f"✅ Стиль .info изменен на: {style}"
                else:
                    return "❌ Ошибка сохранения настроек"
            else:
                return f"❌ Неверный стиль. Доступно: {', '.join(valid_styles)}"
        
        elif action == 'ping' and len(parts) == 3:
            style = parts[2]
            valid_styles = ['custom', 'detailed', 'simple', 'network']
            if style in valid_styles:
                settings['ping_style'] = style
                if save_settings(settings):
                    return f"✅ Стиль .ping изменен на: {style}"
                else:
                    return "❌ Ошибка сохранения настроек"
            else:
                return f"❌ Неверный стиль. Доступно: {', '.join(valid_styles)}"
        
        elif action == 'set':
            return process_set_command(vk, message_id, peer_id, settings)
        
        elif action == 'vars':
            return show_available_variables()
        
        elif action == 'reset':
            return reset_settings(settings, hotkeys)
        
        else:
            return show_settings_help()
    
    return show_settings_help()

def show_current_settings(settings):
    """Показывает текущие настройки"""
    prefix = settings['prefix']
    info_style = settings['info_style']
    ping_style = settings['ping_style']
    
    # Описания стилей
    info_styles_desc = {
        'custom': '🎨 Кастомное сообщение',
        'full': '📊 Полная информация',
        'minimal': '📱 Минимальная',
        'system': '⚙️ Только система',
        'user': '👤 Только пользователь',
        'bot': '🤖 Только бот'
    }
    
    ping_styles_desc = {
        'custom': '🎨 Кастомное сообщение',
        'detailed': '📈 Детальный',
        'simple': '🔄 Простой',
        'network': '🌐 Сетевой'
    }
    
    settings_text = f"""⚙️ **Текущие настройки Icers**

**📝 Основные**
• Префикс команд: `{prefix}`

**ℹ️ Команда .info**
• Стиль: {info_styles_desc[info_style]}

**🏓 Команда .ping**  
• Стиль: {ping_styles_desc[ping_style]}

**💡 Быстрые команды**
`{prefix}settings prefix <символ>` - изменить префикс
`{prefix}settings info <стиль>` - изменить стиль .info
`{prefix}settings ping <стиль>` - изменить стиль .ping
`{prefix}settings set <команда> <текст>` - кастомное сообщение
`{prefix}settings vars` - доступные переменные
`{prefix}settings reset` - сбросить настройки"""
    return settings_text.strip()

def reset_settings(settings, hotkeys):
    """Сбрасывает настройки к значениям по умолчанию"""
    import os
    try:
        if os.path.exists('settings.json'):
            os.remove('settings.json')
        if os.path.exists('hotkeys.json'):
            os.remove('hotkeys.json')
        
        # Сбрасываем в памяти
        settings.update(load_settings())
        hotkeys.clear()
        
        return "✅ Все настройки сброшены к значениям по умолчанию!"
    except Exception as e:
        return f"❌ Ошибка сброса настроек: {str(e)}"

def show_settings_help():
    """Показывает справку по настройкам"""
    help_text = """⚙️ **Справка по настройкам**

**📝 Основные команды**
`.settings` - показать текущие настройки
`.settings prefix <символ>` - изменить префикс команд
`.settings info <стиль>` - изменить стиль .info
`.settings ping <стиль>` - изменить стиль .ping  
`.settings set <команда> <текст>` - установить кастомное сообщение
`.settings vars` - показать доступные переменные
`.settings reset` - сбросить все настройки

**🎨 Стили .info**
• `custom` - кастомное сообщение
• `full` - полная информация
• `minimal` - минимальная
• `system` - только система
• `user` - только пользователь
• `bot` - только бот

**🌐 Стили .ping**
• `custom` - кастомное сообщение
• `detailed` - детальный
• `simple` - простой
• `network` - сетевой

**💡 Примеры кастомных сообщений**
`.set ping Понг! 🏓
Задержка: {ping}ms
Аптайм: {uptime}`
`.set info 👤 {user_name}
🆔 {user_id}
⏱️ {uptime}`"""
    return help_text.strip()

def show_available_variables():
    """Показывает все доступные переменные"""
    variables_text = """📋 **Доступные переменные для кастомных сообщений**

**🔄 Для .info:**
{user_name} - Имя и фамилия пользователя
{user_id} - ID пользователя  
{online_status} - Статус онлайн (✅/❌)
{os_info} - Информация об ОС
{python_version} - Версия Python
{architecture} - Архитектура системы
{uptime} - Время работы бота
{platform} - Платформа системы
{processor} - Процессор

**🏓 Для .ping:**
{ping} - Сетевая задержка в ms
{uptime} - Время работы бота
{quality} - Качество соединения
{timestamp} - Текущее время
{status} - Статус бота

**💡 Пример использования:**
.set ping Понг! 🏓
Задержка: {ping}ms
Аптайм: {uptime}
Качество: {quality}"""
    return variables_text.strip()