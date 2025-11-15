import vk_api
import platform
import configparser
import os
import json
import time
import importlib.util
import sys
import requests
import subprocess
import io
import contextlib
from vk_api.longpoll import VkLongPoll, VkEventType

# Глобальные переменные для отслеживания времени запуска
START_TIME = time.time()

def load_config():
    """Загружает конфигурацию из файла"""
    config = configparser.ConfigParser()
    
    if not os.path.exists('icehostdata.ini'):
        print("❌ Файл конфигурации 'icehostdata.ini' не найден!")
        print("📝 Создайте файл со следующим содержимым:")
        print("""
[VK]
token = ваш_токен_доступа
user_id = ваш_user_id
        """)
        exit(1)
    
    config.read('icehostdata.ini', encoding='utf-8')
    
    try:
        token = config.get('VK', 'token')
        user_id = config.getint('VK', 'user_id')
        
        if token == 'ваш_токен_доступа' or user_id == 0:
            print("❌ Заполните данные в файле 'icehostdata.ini'!")
            exit(1)
            
        return token, user_id
    except Exception as e:
        print(f"❌ Ошибка чтения конфигурации: {e}")
        exit(1)

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

🤖 **IceHost**
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
                # Объединяем с настройками по умолчанию
                return {**default_settings, **saved_settings}
    except Exception as e:
        print(f"❌ Ошибка загрузки настроек: {e}")
    
    return default_settings

def save_settings(settings):
    """Сохраняет настройки в файл"""
    try:
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения настроек: {e}")
        return False

def load_hotkeys():
    """Загружает хоткеи из файла"""
    try:
        if os.path.exists('hotkeys.json'):
            with open('hotkeys.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки хоткеев: {e}")
    return {}

def save_hotkeys(hotkeys):
    """Сохраняет хоткеи в файл"""
    try:
        with open('hotkeys.json', 'w', encoding='utf-8') as f:
            json.dump(hotkeys, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения хоткеев: {e}")

def load_modules():
    """Загружает модули из папки modules"""
    modules = {}
    modules_dir = 'modules'
    
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
        print("📁 Создана папка modules для модулей")
        return modules
    
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            module_name = filename[:-3]  # Убираем .py
            try:
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(modules_dir, filename))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Проверяем, что модуль имеет необходимые атрибуты
                if hasattr(module, 'MODULE_INFO') and hasattr(module, 'process_command'):
                    modules[module_name] = module
                    print(f"✅ Загружен модуль: {module_name} - {module.MODULE_INFO.get('description', 'No description')}")
                else:
                    print(f"❌ Модуль {module_name} не имеет необходимых атрибутов")
            except Exception as e:
                print(f"❌ Ошибка загрузки модуля {filename}: {e}")
    
    return modules

def get_module_commands(module):
    """Получает список команд из модуля"""
    commands = []
    try:
        # Проверяем наличие атрибута с командами
        if hasattr(module, 'MODULE_COMMANDS'):
            commands.extend(module.MODULE_COMMANDS)
        else:
            # Альтернативно, можно анализировать process_command
            commands.append("команды модуля")
    except:
        pass
    return commands

def get_message_sender(vk, peer_id, message_id, user_id):
    """Определяет отправителя сообщения"""
    try:
        # Если это беседа, используем специальный метод
        if peer_id > 2000000000:
            messages = vk.messages.getByConversationMessageId(
                peer_id=peer_id,
                conversation_message_ids=[message_id]
            )
            if messages['items']:
                return messages['items'][0]['from_id']
        else:
            # Для личных сообщений проверяем, от кого сообщение
            # Если peer_id равен нашему user_id - это избранное (сообщение от нас)
            if peer_id == user_id:
                return user_id
            else:
                # В личной переписке с другим человеком
                # Нужно проверить, кто отправил сообщение
                messages = vk.messages.getById(message_ids=[message_id])
                if messages['items']:
                    return messages['items'][0]['from_id']
    except Exception as e:
        print(f"❌ Ошибка при определении отправителя: {e}")
    
    return None

def download_file(url, filename):
    """Скачивает файл по URL"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"❌ Ошибка скачивания файла: {e}")
    return False

def install_module_from_file(vk, message_id, peer_id):
    """Устанавливает модуль из файла, на который ответили"""
    try:
        # Получаем информацию о сообщении
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return "❌ Не удалось получить информацию о сообщении"
        
        message = messages['items'][0]
        
        # Проверяем, что это ответ на сообщение с файлом
        if 'reply_message' not in message:
            return "❌ Это не ответ на сообщение! Ответьте на сообщение с файлом .py"
        
        reply_message = message['reply_message']
        
        # Ищем прикрепленный файл .py
        python_file = None
        if 'attachments' in reply_message:
            for attachment in reply_message['attachments']:
                if attachment['type'] == 'doc' and attachment['doc']['ext'] == 'py':
                    python_file = attachment['doc']
                    break
        
        if not python_file:
            return "❌ В сообщении нет прикрепленного .py файла"
        
        # Скачиваем файл
        file_url = python_file['url']
        file_name = python_file['title']
        modules_dir = 'modules'
        
        if not os.path.exists(modules_dir):
            os.makedirs(modules_dir)
        
        file_path = os.path.join(modules_dir, file_name)
        
        if download_file(file_url, file_path):
            # Пытаемся загрузить модуль для проверки
            try:
                module_name = file_name[:-3]  # Убираем .py
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Проверяем, что это валидный модуль
                if hasattr(module, 'MODULE_INFO') and hasattr(module, 'process_command'):
                    return f"✅ Модуль '{module_name}' успешно установлен!\n📝 Описание: {module.MODULE_INFO.get('description', 'Нет описания')}"
                else:
                    os.remove(file_path)  # Удаляем невалидный файл
                    return "❌ Файл не является валидным модулем IceHost (отсутствуют MODULE_INFO или process_command)"
                    
            except Exception as e:
                os.remove(file_path)  # Удаляем файл с ошибками
                return f"❌ Ошибка загрузки модуля: {str(e)}"
        else:
            return "❌ Не удалось скачать файл"
            
    except Exception as e:
        return f"❌ Ошибка установки модуля: {str(e)}"

def delete_module(module_name, modules):
    """Удаляет модуль"""
    try:
        modules_dir = 'modules'
        file_path = os.path.join(modules_dir, f"{module_name}.py")
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
            # Удаляем из загруженных модулей
            if module_name in modules:
                del modules[module_name]
            
            return f"✅ Модуль '{module_name}' успешно удален!"
        else:
            return f"❌ Модуль '{module_name}' не найден!"
            
    except Exception as e:
        return f"❌ Ошибка удаления модуля: {str(e)}"

def measure_network_latency(vk):
    """Измеряет сетевую задержку до API VK"""
    try:
        start_time = time.time()
        # Выполняем простой запрос к API
        vk.users.get(user_ids=1)
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # в миллисекундах
        return latency
    except Exception as e:
        print(f"❌ Ошибка измерения задержки: {e}")
        return None

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

def process_settings_command(command, settings, hotkeys, vk, message_id, peer_id):
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

def process_set_command(vk, message_id, peer_id, settings, command_text=None):
    """Обрабатывает команду set для установки кастомных сообщений"""
    try:
        if command_text:
            # Если команда пришла как .set ping текст
            parts = command_text.split(' ', 2)  # Разделяем на 3 части: set, ping, текст
            if len(parts) < 3:
                return "❌ Неправильный формат. Используйте: .set <команда> <текст>"
            
            command_type = parts[1]
            message_text = parts[2]
        else:
            # Если команда пришла как .settings set (многострочное сообщение)
            messages = vk.messages.getById(message_ids=[message_id])
            if not messages['items']:
                return "❌ Не удалось получить информацию о сообщении"
            
            original_message = messages['items'][0]['text']
            
            # Проверяем, что это команда .settings set
            if not original_message.startswith('.settings set'):
                return "❌ Это не команда .settings set"
            
            # Разбираем команду - берем первую строку для определения типа
            first_line = original_message.split('\n')[0]
            parts = first_line.split()
            
            if len(parts) < 3:
                return "❌ Неправильный формат. Используйте: .settings set <команда> и текст на новых строках"
            
            command_type = parts[2]  # ping или info после .settings set
            
            # Извлекаем текст после ".settings set ping" 
            set_prefix = f".settings set {command_type}"
            set_pos = original_message.find(set_prefix)
            if set_pos == -1:
                return "❌ Ошибка парсинга команды"
            
            # Берем текст после команды
            message_text = original_message[set_pos + len(set_prefix):].strip()
        
        if command_type not in ['info', 'ping']:
            return "❌ Неверная команда. Доступно: info, ping"
        
        if not message_text:
            # Показать текущее сообщение и переменные
            current_message = settings['custom_messages'].get(command_type, '')
            variables = get_variables_for_command(command_type)
            
            response = f"📝 Текущее сообщение для .{command_type}:\n\n{current_message}\n\n"
            response += f"📋 Доступные переменные для .{command_type}:\n{variables}"
            response += f"\n\n💡 Чтобы изменить:\n• .set {command_type} ваш текст\n• Или: .settings set {command_type} и текст на новых строках"
            return response
        
        # Сохраняем сообщение
        settings['custom_messages'][command_type] = message_text
        
        if save_settings(settings):
            # Показываем как будет выглядеть сообщение
            preview = f"✅ Сообщение для .{command_type} обновлено!\n\n📝 Новый текст:\n{message_text}\n\n📋 Переменные будут заменены при выполнении команды"
            return preview
        else:
            return "❌ Ошибка сохранения настроек"
            
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"
    
def get_variables_for_command(command_type):
    """Возвращает список доступных переменных для команды"""
    if command_type == 'info':
        return """{user_name} - Имя и фамилия пользователя
{user_id} - ID пользователя
{online_status} - Статус онлайн (✅/❌)
{os_info} - Информация об ОС
{python_version} - Версия Python
{architecture} - Архитектура системы
{uptime} - Время работы бота
{platform} - Платформа системы
{processor} - Процессор"""
    elif command_type == 'ping':
        return """{ping} - Сетевая задержка в ms
{uptime} - Время работы бота
{quality} - Качество соединения
{timestamp} - Текущее время
{status} - Статус бота"""
    return ""

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
    
    settings_text = f"""⚙️ **Текущие настройки IceHost**

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

def generate_custom_info(vk, settings, USER_ID):
    """Генерирует кастомное сообщение .info"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        online_status = '✅' if user_info.get('online', 0) else '❌'
        
        template = settings['custom_messages']['info']
        
        # Заменяем переменные (исправлены названия)
        message = template.format(
            user_name=user_name,
            user_id=USER_ID,
            online_status=online_status,
            os_info=f"{platform.system()} {platform.release()}",
            python_version=platform.python_version(),  # ИСПРАВЛЕНО: было python_ersion
            architecture=platform.architecture()[0],
            uptime=get_uptime(),
            platform=platform.platform(),
            processor=platform.processor() or 'Не определен'
        )
        
        return message
    except KeyError as e:
        return f"❌ Неизвестная переменная в шаблоне: {e}\nИспользуйте .settings vars для списка переменных"
    except Exception as e:
        return f"❌ Ошибка в кастомном сообщении: {str(e)}"

def generate_custom_ping(vk, settings):
    """Генерирует кастомное сообщение .ping"""
    try:
        latency = measure_network_latency(vk)
        if latency is None:
            return "❌ Не удалось измерить задержку"
        
        template = settings['custom_messages']['ping']
        
        # Заменяем переменные
        message = template.format(
            ping=f"{latency:.2f}",
            uptime=get_uptime(),
            quality=get_connection_quality(latency),
            timestamp=time.strftime("%H:%M:%S"),
            status="Активен ✅"
        )
        
        return message
    except Exception as e:
        return f"❌ Ошибка в кастомном сообщении: {str(e)}"

def generate_info_message(vk, settings, USER_ID):
    """Генерирует сообщение .info в соответствии с настройками"""
    style = settings['info_style']
    
    if style == 'custom':
        return generate_custom_info(vk, settings, USER_ID)
    elif style == 'full':
        return generate_full_info(vk, USER_ID)
    elif style == 'minimal':
        return generate_minimal_info(vk, USER_ID)
    elif style == 'system':
        return generate_system_info()
    elif style == 'user':
        return generate_user_info(vk, USER_ID)
    elif style == 'bot':
        return generate_bot_info()
    else:
        return generate_custom_info(vk, settings, USER_ID)

def generate_full_info(vk, USER_ID):
    """Полная информация"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online,last_seen,status')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        info_text = f"""👤 **Профиль**
• Имя: {user_name}
• ID: {USER_ID}
• Онлайн: {'✅' if user_info.get('online', 0) else '❌'}

⚙️ **Система**
• ОС: {platform.system()} {platform.release()}
• Python: {platform.python_version()}
• Архитектура: {platform.architecture()[0]}

🤖 **IceHost**
• Разработчик: SnowCode
• Версия: 2.0
• Аптайм: {get_uptime()}
• Статус: Активен ✅"""
        return info_text
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def generate_minimal_info(vk, USER_ID):
    """Минимальная информация"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        info_text = f"""📱 **IceHost - Минимальная информация**

👤 {user_name} | ID: {USER_ID}
⚙️ {platform.system()} | Python {platform.python_version()}
⏱️ Аптайм: {get_uptime()}
🤖 Статус: {'🟢 Онлайн' if user_info.get('online', 0) else '🔴 Офлайн'}"""
        return info_text
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def generate_system_info():
    """Только системная информация"""
    info_text = f"""⚙️ **Системная информация**

• ОС: {platform.system()} {platform.release()}
• Платформа: {platform.platform()}
• Python: {platform.python_version()}
• Архитектура: {platform.architecture()[0]}
• Процессор: {platform.processor() or 'Не определен'}
• Аптайм: {get_uptime()}"""
    return info_text

def generate_user_info(vk, USER_ID):
    """Только информация о пользователе"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online,last_seen,status')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        info_text = f"""👤 **Информация о пользователе**

• Имя: {user_name}
• ID: {USER_ID}
• Онлайн: {'✅ Да' if user_info.get('online', 0) else '❌ Нет'}
• Статус: {user_info.get('status', 'Не установлен')}
• Ссылка: vk.com/id{USER_ID}
• Аптайм бота: {get_uptime()}"""
        return info_text
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def generate_bot_info():
    """Только информация о боте"""
    info_text = f"""🤖 **Информация о IceHost**

• Разработчик: SnowCode
• Версия: 2.0
• Платформа: VK UserBot
• Функции: Команды + Модули + Настройки
• Аптайм: {get_uptime()}
• Статус: Активен ✅"""
    return info_text

def generate_ping_message(vk, settings):
    """Генерирует сообщение .ping в соответствии с настройками"""
    style = settings['ping_style']
    
    if style == 'custom':
        return generate_custom_ping(vk, settings)
    elif style == 'detailed':
        return generate_detailed_ping(vk)
    elif style == 'simple':
        return generate_simple_ping()
    elif style == 'network':
        return generate_network_ping(vk)
    else:
        return generate_custom_ping(vk, settings)

def generate_detailed_ping(vk):
    """Детальный пинг"""
    latency = measure_network_latency(vk)
    if latency is not None:
        return f"""🏓 **Детальный пинг**

🌐 Сетевая задержка: `{latency:.2f}ms`
⏱️ Аптайм: {get_uptime()}
✅ Статус: Бот активен
📊 Качество: {get_connection_quality(latency)}"""
    else:
        return "❌ Не удалось измерить задержку"

def generate_simple_ping():
    """Простой пинг"""
    return f"""🔄 **Пинг**

✅ Бот активен
⏱️ Аптайм: {get_uptime()}"""

def generate_network_ping(vk):
    """Сетевой пинг"""
    latency = measure_network_latency(vk)
    if latency is not None:
        return f"""🌐 **Сетевой пинг**

Задержка до API VK: `{latency:.2f}ms`
Качество: {get_connection_quality(latency)}"""
    else:
        return "❌ Не удалось измерить задержку"
    
def execute_terminal_command(command):
    """Выполняет команду в терминале и возвращает результат"""
    try:
        # Выполняем команду без ограничений
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        output = ""
        if result.stdout:
            output += f"📤 STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"❌ STDERR:\n{result.stderr}\n"
        
        if output:
            # Обрезаем слишком длинный вывод
            if len(output) > 2000:
                output = output[:2000] + "\n... (вывод обрезан)"
            return f"💻 Команда: `{command}`\n\n{output}\n⏩ Код возврата: {result.returncode}"
        else:
            return f"💻 Команда: `{command}`\n\n✅ Выполнено успешно\n⏩ Код возврата: {result.returncode}"
            
    except subprocess.TimeoutExpired:
        return f"❌ Команда `{command}` превысила лимит времени (30 секунд)"
    except Exception as e:
        return f"❌ Ошибка выполнения команды: {str(e)}"

def execute_python_code(code):
    """Выполняет код Python и возвращает результат"""
    try:
        # Создаем контекст для перехвата вывода
        output = io.StringIO()
        
        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                try:
                    # Выполняем код с полным доступом
                    exec(code)
                    
                    # Если код выглядит как выражение, пытаемся его вычислить
                    if any(indicator in code for indicator in ['+', '-', '*', '/', '=', '==', '!=', '>', '<']):
                        try:
                            eval_result = eval(code)
                            if eval_result is not None and str(eval_result) not in output.getvalue():
                                print(f"📦 Результат: {eval_result}")
                        except:
                            pass  # Игнорируем ошибки eval, если exec уже сработал
                            
                except Exception as e:
                    print(f"❌ Ошибка выполнения: {type(e).__name__}: {e}")
        
        result_output = output.getvalue()
        
        if result_output:
            # Обрезаем слишком длинный вывод
            if len(result_output) > 2000:
                result_output = result_output[:2000] + "\n... (вывод обрезан)"
            return f"🐍 Код:\n```python\n{code}\n```\n\n📤 Вывод:\n{result_output}"
        else:
            return f"🐍 Код:\n```python\n{code}\n```\n\n✅ Выполнено без вывода"
            
    except Exception as e:
        return f"❌ Ошибка выполнения Python кода: {str(e)}"

def process_command(vk, peer_id, message_id, command, hotkeys, modules, settings, USER_ID):
    """Обрабатывает команды"""
    result_message = ""
    prefix = settings['prefix']
    
    # Проверяем префикс
    if not command.startswith(prefix):
        return ""
    
    # Убираем префикс для обработки
    clean_command = command[len(prefix):]
    
    # Обработка команды info
    if clean_command == 'info':
        result_message = generate_info_message(vk, settings, USER_ID)
    
    # Обработка команды ping
    elif clean_command == 'ping':
        result_message = generate_ping_message(vk, settings)
    
    # Обработка команды settings
    elif clean_command.startswith('settings'):
        result_message = process_settings_command(clean_command, settings, hotkeys, vk, message_id, peer_id)
    

    # Обработка команды terminal (добавить после других команд)
    elif clean_command.startswith('terminal '):
        if len(clean_command) > 9:
            cmd = clean_command[9:].strip()
            result_message = execute_terminal_command(cmd)
        else:
            result_message = "❌ Укажите команду для выполнения: .terminal <команда>"
    
    # Обработка команды python
    elif clean_command.startswith('python '):
        if len(clean_command) > 7:
            code = clean_command[7:].strip()
            # Декодируем HTML-сущности обратно в нормальные символы
            code = code.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            result_message = execute_python_code(code)
        else:
            result_message = "❌ Укажите код Python: .python <код>"

    # Обработка команды hotkey
    elif clean_command.startswith('hotkey '):
        parts = clean_command[7:].strip().split(' ', 1)
        if len(parts) == 2:
            alias, target_command = parts
            if not target_command.startswith(prefix):
                target_command = prefix + target_command
            # Проверяем, существует ли такая команда
            valid_commands = ['info', 'ping', 'hotkey', 'hotlist', 'delhotkey', 'dm', 'modules', 'delm', 'settings', 'set', 'terminal', 'python']
            if target_command[len(prefix):].split(' ')[0] not in valid_commands:
                result_message = f"❌ Команда {target_command} не существует!"
            elif alias in hotkeys:
                result_message = f"❌ Хоткей '{alias}' уже существует!"
            else:
                hotkeys[alias] = target_command
                save_hotkeys(hotkeys)
                result_message = f"✅ Хоткей создан!\n• Алиас: {prefix}{alias}\n• Команда: {target_command}\n\nИспользуй: {prefix}{alias}"
        else:
            result_message = f"❌ Неправильный формат команды.\nИспользуй: {prefix}hotkey алиас команда\nПример: {prefix}hotkey пинг ping"
    
    # Обработка команды hotlist
    elif clean_command == 'hotlist':
        if hotkeys:
            hotkey_list = "\n".join([f"• {prefix}{alias} → {cmd}" for alias, cmd in hotkeys.items()])
            result_message = f"📋 Список хоткеев:\n{hotkey_list}"
        else:
            result_message = f"📋 Список хоткеев пуст.\nСоздай хоткей: {prefix}hotkey алиас команда"
    
    # Обработка команды delhotkey
    elif clean_command.startswith('delhotkey '):
        alias = clean_command[10:].strip()
        if alias in hotkeys:
            del hotkeys[alias]
            save_hotkeys(hotkeys)
            result_message = f"✅ Хоткей '{alias}' удален!"
        else:
            result_message = f"❌ Хоткей '{alias}' не найден!"
    
    # Обработка команды modules
    elif clean_command == 'modules':
        if modules:
            module_list = []
            for name, mod in modules.items():
                commands = get_module_commands(mod)
                commands_text = ", ".join(commands) if commands else "команды модуля"
                module_list.append(f"• {name} - {mod.MODULE_INFO.get('description', 'Нет описания')}\n  📝 Команды: {commands_text}")
            
            result_message = f"📦 Загруженные модули ({len(modules)}):\n" + "\n\n".join(module_list)
        else:
            result_message = "📦 Модули не загружены.\nДля установки модуля ответьте на файл .py командой .dm"
    
    # Обработка команды dm (Download Module)
    elif clean_command == 'dm':
        result_message = install_module_from_file(vk, message_id, peer_id)
        # Перезагружаем модули после установки
        if result_message.startswith("✅"):
            modules.update(load_modules())
    
    # Обработка команды delm (Delete Module)
    elif clean_command.startswith('delm '):
        module_name = clean_command[5:].strip()
        result_message = delete_module(module_name, modules)
    
    # Проверяем модули
    else:
        for module_name, module in modules.items():
            try:
                module_result = module.process_command(clean_command, vk, peer_id, USER_ID, settings)
                if module_result:
                    result_message = module_result
                    break
            except TypeError:
                # Если модуль не поддерживает settings параметр
                try:
                    module_result = module.process_command(clean_command, vk, peer_id, USER_ID)
                    if module_result:
                        result_message = module_result
                        break
                except Exception as e:
                    print(f"❌ Ошибка в модуле {module_name}: {e}")
            except Exception as e:
                print(f"❌ Ошибка в модуле {module_name}: {e}")
    
    # Если команда не обработана
    if not result_message and clean_command:
        result_message = f"❌ Неизвестная команда: {command}\n\n📋 Доступные команды:\n• {prefix}info - информация\n• {prefix}ping - проверка сети\n• {prefix}hotkey - создать хоткей\n• {prefix}hotlist - список хоткеев\n• {prefix}delhotkey - удалить хоткей\n• {prefix}modules - список модулей\n• {prefix}dm - установить модуль\n• {prefix}delm имя - удалить модуль\n• {prefix}settings - настройки\n• {prefix}python код - выполнить код в python\n• {prefix}terminal команда - выполнить команду в терминале"
    
    return result_message

def main():
    # Загружаем конфигурацию
    VK_TOKEN, USER_ID = load_config()
    
    # Загружаем настройки
    settings = load_settings()
    prefix = settings['prefix']
    print(f"🔧 Загружены настройки, префикс: '{prefix}'")
    
    # Загружаем хоткеи
    hotkeys = load_hotkeys()
    print(f"🔧 Загружено хоткеев: {len(hotkeys)}")
    
    # Загружаем модули
    modules = load_modules()
    print(f"📦 Загружено модулей: {len(modules)}")
    
    print("🔧 Загружена конфигурация:")
    print(f"   User ID: {USER_ID}")
    print(f"   Token: {VK_TOKEN[:20]}...")

    # Авторизация
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        
        # Проверяем валидность токена
        user_info = vk.users.get(user_ids=USER_ID)
        print(f"✅ Успешная авторизация: {user_info[0]['first_name']} {user_info[0]['last_name']}")
        
        longpoll = VkLongPoll(vk_session)
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        print("🔧 Проверьте токен и User ID в файле icehostdata.ini")
        return

    print(f"❄️ IceHost запущен... (префикс: '{prefix}')")
    print("📝 Бот будет реагировать на команды во всех диалогах (только от вас)")
    
    # Основной цикл прослушивания
    for event in longpoll.listen():
        # Пропускаем события, которые не являются новыми сообщениями
        if event.type != VkEventType.MESSAGE_NEW:
            continue
            
        msg_text = event.text
        peer_id = event.peer_id
        message_id = event.message_id
        
        # Определяем отправителя
        from_user_id = get_message_sender(vk, peer_id, message_id, USER_ID)
        
        # Определяем тип диалога
        if peer_id > 2000000000:
            dialog_type = "беседа"
        elif peer_id == USER_ID:
            dialog_type = "избранное"
        else:
            dialog_type = "личные сообщения"
        
        print(f"📨 {dialog_type}: '{msg_text}' от {from_user_id}")
        
        # Проверяем, что сообщение от нужного пользователя
        if from_user_id == USER_ID:
            # Проверяем хоткеи
            original_command = msg_text
            if msg_text.startswith(prefix) and len(msg_text) > len(prefix):
                command_without_prefix = msg_text[len(prefix):]
                command = command_without_prefix.split()[0]  # Берем первую часть команды
                
                # Проверяем хоткеи
                alias = command
                if alias in hotkeys:
                    msg_text = hotkeys[alias] + msg_text[len(prefix) + len(command):]  # Заменяем команду, сохраняя аргументы
                    print(f"🎯 Хоткей: '{original_command}' → '{msg_text}'")
            
            # Обрабатываем команды
            if msg_text.startswith(prefix):
                result_message = process_command(vk, peer_id, message_id, msg_text, hotkeys, modules, settings, USER_ID)
                
                if result_message:
                    # Редактируем исходное сообщение
                    try:
                        vk.messages.edit(
                            peer_id=peer_id,
                            message_id=message_id,
                            message=result_message
                        )
                        print("✅ Сообщение успешно отредактировано")
                    except Exception as e:
                        print(f"❌ Ошибка редактирования сообщения: {e}")
                        
                        # Если редактирование не удалось, отправляем как новое сообщение
                        try:
                            vk.messages.send(
                                peer_id=peer_id,
                                message="❌ Не удалось отредактировать сообщение\n\n" + result_message,
                                random_id=0
                            )
                            print("📤 Отправлено новое сообщение с результатом")
                        except Exception as e2:
                            print(f"❌ Ошибка отправки сообщения: {e2}")
            
            # Проверяем модули для остальных команд
            elif msg_text.startswith(prefix):
                result_message = process_command(vk, peer_id, message_id, msg_text, hotkeys, modules, settings, USER_ID)
                if result_message:
                    try:
                        vk.messages.edit(
                            peer_id=peer_id,
                            message_id=message_id,
                            message=result_message
                        )
                        print("✅ Сообщение успешно отредактировано (модуль)")
                    except Exception as e:
                        print(f"❌ Ошибка редактирования сообщения: {e}")

if __name__ == '__main__':
    main()