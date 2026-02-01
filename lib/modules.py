import importlib.util
import os
import sys
from .logger import logger

def load_modules():
    """Загружает модули из папки modules с проверкой безопасности"""
    modules = {}
    modules_dir = 'modules'
    
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir, exist_ok=True)
        logger.info("Создана папка modules для модулей")
        return modules
    
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            module_name = filename[:-3]  # Убираем .py
            
            try:
                module_path = os.path.join(modules_dir, filename)
                
                # Проверяем безопасность модуля
                if not is_module_safe(module_path):
                    logger.error(f"Модуль {filename} не прошел проверку безопасности")
                    continue
                
                # Загружаем модуль
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                
                # Ограничиваем доступ модуля
                restrict_module_access(module, module_name)
                
                spec.loader.exec_module(module)
                
                # Проверяем, что модуль имеет необходимые атрибуты
                if hasattr(module, 'MODULE_INFO') and hasattr(module, 'process_command'):
                    modules[module_name] = module
                    description = module.MODULE_INFO.get('description', 'No description')
                    logger.module_loaded(module_name, description)
                else:
                    logger.error(f"Модуль {module_name} не имеет необходимых атрибутов")
                    
            except Exception as e:
                logger.error(f"Ошибка загрузки модуля {filename}: {e}")
    
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
        from .file_utils import download_file
        
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
                    return "❌ Файл не является валидным модулем Icers (отсутствуют MODULE_INFO или process_command)"
                    
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

def is_module_safe(module_path):
    """Проверяет безопасность модуля"""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Список запрещенных операций
        dangerous_patterns = [
            '__import__', 'eval', 'exec', 'compile',
            'open', 'os.system', 'subprocess', 'shutil',
            'sys.exit', 'quit', 'exit',
            'os.chdir', 'os.chroot', 'os.remove',
            'rm ', 'del ', 'format',
            'pickle', 'marshal', 'yaml'
        ]
        
        # Проверяем наличие опасных операций
        for pattern in dangerous_patterns:
            if pattern in content:
                # Исключаем разрешенные случаи
                safe_patterns = [
                    'os.path',  # Разрешено
                    'from os import',  # Разрешено
                    'import os',  # Разрешено
                    'safe_',  # Разрешено если начинается с safe_
                    'logger.',  # Разрешено использование логгера
                    '#',  # Комментарий
                ]
                
                # Проверяем не является ли это безопасным использованием
                is_safe = False
                for safe_pattern in safe_patterns:
                    if safe_pattern in content:
                        # Находим контекст использования
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            if pattern in line:
                                # Проверяем контекст строки
                                if any(safe_pattern in line for safe_pattern in safe_patterns):
                                    is_safe = True
                                    break
                
                if not is_safe:
                    logger.warning(f"Модуль содержит потенциально опасный код: {pattern}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка проверки безопасности модуля: {e}")
        return False

def restrict_module_access(module, module_name):
    """Ограничивает доступ модуля к системе"""
    # Создаем безопасное пространство имен
    safe_globals = {
        '__name__': module_name,
        '__file__': f"modules/{module_name}.py",
        '__doc__': None,
        '__package__': None,
        '__builtins__': {
            # Разрешаем только безопасные встроенные функции
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'isinstance': isinstance,
            'type': type,
            'repr': repr,
            'format': format,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'chr': chr,
            'ord': ord,
        }
    }
    
    # Устанавливаем глобальные переменные модуля
    module.__dict__.update(safe_globals)