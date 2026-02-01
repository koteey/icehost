"""
Команда .ubac - управление доступом к юзерботу
"""

import json
import os

# Файл с правами доступа
ACCESS_FILE = 'user_access.json'

# Уровни доступа
ACCESS_LEVELS = {
    0: "❌ Нет доступа",
    1: "✅ Полный доступ (все команды и модули)",
    2: "🔧 Только команды (все системные команды)",
    3: "🎮 Только развлечения (медиа, игры, утилиты)",
    "module": "📦 Доступ только к модулю"
}

def load_access():
    """Загружает права доступа"""
    try:
        if os.path.exists(ACCESS_FILE):
            with open(ACCESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_access(access_data):
    """Сохраняет права доступа"""
    try:
        with open(ACCESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(access_data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def check_access(user_id, command_name, module_name=None):
    """Проверяет доступ пользователя к команде"""
    access_data = load_access()
    
    # Владелец всегда имеет доступ
    owner_id = None
    try:
        with open('icersdata.ini', 'r') as f:
            for line in f:
                if 'user_id' in line:
                    owner_id = int(line.split('=')[1].strip())
                    break
    except:
        pass
    
    if user_id == owner_id:
        return True
    
    # Проверяем права
    if str(user_id) not in access_data:
        return False
    
    user_access = access_data[str(user_id)]
    access_level = user_access.get('level', 0)
    
    # Уровень 0 - нет доступа
    if access_level == 0:
        return False
    
    # Уровень 1 - полный доступ
    if access_level == 1:
        return True
    
    # Уровень 2 - все команды
    if access_level == 2:
        # Разрешаем все команды кроме управления доступом и опасных
        dangerous_commands = ['ubac', 'terminal', 'python', 'vkapi', 
                            'setname', 'setphoto', 'post', 'restart']
        return command_name not in dangerous_commands
    
    # Уровень 3 - только развлечения
    if access_level == 3:
        entertainment_commands = ['info', 'ping', 'copy', 'spam', 'negative',
                                'demot', 'text', 'dist', 'boost', 'av',
                                'random', 'dice', 'coin', 'chance', 'kto',
                                'vos', 'meme', 'filter', 'pitch', 'speed',
                                'qr', 'qrscan', 'tts']
        return command_name in entertainment_commands
    
    # Доступ к конкретному модулю
    if user_access.get('type') == 'module':
        allowed_modules = user_access.get('modules', [])
        if module_name in allowed_modules:
            return True
    
    return False

def process_ubac(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .ubac"""
    
    try:
        # Только владелец может управлять доступом
        owner_id = None
        try:
            with open('icersdata.ini', 'r') as f:
                for line in f:
                    if 'user_id' in line:
                        owner_id = int(line.split('=')[1].strip())
                        break
        except:
            pass
        
        if user_id != owner_id:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Только владелец бота может управлять доступом!",
                random_id=0
            )
            return ""
        
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Парсим команду
        parts = clean_command.split()
        if len(parts) < 3:
            # Показываем текущие права
            access_data = load_access()
            
            if not access_data:
                response = "📋 Список прав доступа пуст."
            else:
                response = "📋 **Текущие права доступа:**\n\n"
                for user_id_str, data in access_data.items():
                    user_id_int = int(user_id_str)
                    try:
                        user_info = vk.users.get(user_ids=user_id_int)[0]
                        username = f"{user_info['first_name']} {user_info['last_name']}"
                    except:
                        username = f"ID{user_id_int}"
                    
                    level = data.get('level', 0)
                    if data.get('type') == 'module':
                        modules = ', '.join(data.get('modules', []))
                        response += f"👤 {username} ({user_id_int}): 📦 Модули: {modules}\n"
                    else:
                        response += f"👤 {username} ({user_id_int}): {ACCESS_LEVELS.get(level, 'Неизвестно')}\n"
            
            vk.messages.send(
                peer_id=peer_id,
                message=response,
                random_id=0
            )
            return ""
        
        # Определяем пользователя
        target_user_id = None
        
        # Проверяем ответ на сообщение
        messages = vk.messages.getById(message_ids=[message_id])
        if messages['items']:
            message = messages['items'][0]
            
            if 'reply_message' in message:
                reply_message = message['reply_message']
                target_user_id = reply_message.get('from_id')
            elif 'fwd_messages' in message and message['fwd_messages']:
                target_user_id = message['fwd_messages'][0].get('from_id')
        
        if not target_user_id:
            # Пробуем из текста команды
            try:
                # Может быть упоминание @id123456
                if 'id' in parts[1]:
                    target_user_id = int(parts[1].replace('id', ''))
                else:
                    # Или просто ID
                    target_user_id = int(parts[1])
            except:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ Укажите пользователя (ответьте на сообщение или укажите ID)",
                    random_id=0
                )
                return ""
        
        # Уровень доступа
        access_level = parts[2]
        
        # Загружаем текущие права
        access_data = load_access()
        
        # Получаем имя пользователя
        try:
            user_info = vk.users.get(user_ids=target_user_id)[0]
            username = f"{user_info['first_name']} {user_info['last_name']}"
        except:
            username = f"ID{target_user_id}"
        
        # Обрабатываем уровень доступа
        if access_level == '0':
            # Отобрать все права
            if str(target_user_id) in access_data:
                del access_data[str(target_user_id)]
                response = f"✅ У пользователя {username} отобраны все права!"
            else:
                response = f"ℹ️ У пользователя {username} и так нет прав."
        
        elif access_level in ['1', '2', '3']:
            # Установить уровень доступа
            level = int(access_level)
            access_data[str(target_user_id)] = {
                'level': level,
                'type': 'level'
            }
            response = f"✅ Пользователю {username} установлен уровень доступа: {ACCESS_LEVELS[level]}"
        
        elif access_level.startswith('module:'):
            # Доступ к конкретному модулю
            module_name = access_level[7:]  # Убираем "module:"
            access_data[str(target_user_id)] = {
                'type': 'module',
                'modules': [module_name],
                'level': 0
            }
            response = f"✅ Пользователю {username} предоставлен доступ к модулю: {module_name}"
        
        else:
            # Проверяем, существует ли такой модуль
            modules_dir = 'modules'
            if os.path.exists(modules_dir):
                module_file = f"{modules_dir}/{access_level}.py"
                if os.path.exists(module_file):
                    access_data[str(target_user_id)] = {
                        'type': 'module',
                        'modules': [access_level],
                        'level': 0
                    }
                    response = f"✅ Пользователю {username} предоставлен доступ к модулю: {access_level}"
                else:
                    response = f"❌ Модуль '{access_level}' не найден!"
            else:
                response = f"❌ Папка с модулями не существует!"
        
        # Сохраняем изменения
        if save_access(access_data):
            vk.messages.send(
                peer_id=peer_id,
                message=response,
                random_id=0
            )
        else:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Ошибка сохранения прав доступа!",
                random_id=0
            )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .ubac: {e}")
        return ""