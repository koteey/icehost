import vk_api
import sys
import io
from vk_api.longpoll import VkLongPoll, VkEventType
import warnings
warnings.filterwarnings("ignore")

# Импорты
from lib import config, settings, modules as mod_utils, system_utils
from lib.logger import logger
from commands import process_command, process_all_messages, process_reply_messages, process_other_events

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def get_message_details(vk, message_id):
    """Получает детали сообщения"""
    try:
        messages = vk.messages.getById(message_ids=[message_id])
        if messages['items']:
            return messages['items'][0]
    except:
        return None
    return None

def get_user_info(vk, user_id):
    """Получает информацию о пользователе"""
    try:
        if user_id > 0:
            user_info = vk.users.get(user_ids=user_id, fields='first_name,last_name')[0]
            return {
                'first_name': user_info['first_name'],
                'last_name': user_info.get('last_name', ''),
                'id': user_id
            }
        else:
            group_info = vk.groups.getById(group_id=abs(user_id))[0]
            return {
                'first_name': group_info['name'],
                'last_name': '',
                'id': user_id
            }
    except:
        return {
            'first_name': 'Неизвестно',
            'last_name': '',
            'id': user_id
        }

def main():
    logger.startup("Icers", "4.0")
    
    # Загружаем конфигурацию
    VK_TOKEN, USER_ID = config.load_config()
    
    # Загружаем настройки
    settings_data = settings.load_settings()
    prefix = settings_data['prefix']
    
    # Загружаем хоткеи
    hotkeys = settings.load_hotkeys()
    
    # Загружаем модули
    modules = mod_utils.load_modules()
    
    # Авторизация
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        
        # Получаем информацию о боте
        bot_info = get_user_info(vk, USER_ID)
        bot_first_name = bot_info['first_name']
        bot_last_name = bot_info['last_name']
        
        logger.info(f"Бот: {bot_first_name} {bot_last_name}")
        logger.info(f"Префикс: '{prefix}'")
        
        longpoll = VkLongPoll(vk_session)
        
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        return
    
    logger.info("✅ Бот активен")
    
    # Передаем утилиты
    settings_data['_utils'] = system_utils.get_module_utils()
    
    # Основной цикл
    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW:
            continue
            
        msg_text = event.text
        peer_id = event.peer_id
        message_id = event.message_id
        
        # Получаем детали сообщения
        msg_details = get_message_details(vk, message_id)
        if not msg_details:
            continue
        
        from_user_id = msg_details.get('from_id')
        
        # Определяем тип диалога
        if peer_id > 2000000000:
            dialog_type = "беседа"
        elif peer_id == USER_ID:
            dialog_type = "избранное"
        else:
            dialog_type = "лс"
        
        # Определяем, чье это сообщение
        is_own_message = (from_user_id == USER_ID)
        
        # Получаем информацию об отправителе
        sender_info = get_user_info(vk, from_user_id)
        
        # Определяем информацию о собеседнике для логирования
        if not is_own_message:
            # Сообщение от другого пользователя
            interlocutor_info = sender_info
        else:
            # Наше сообщение
            if dialog_type == "лс":
                # В ЛС: мы пишем кому-то
                interlocutor_info = get_user_info(vk, peer_id)
            else:
                # В избранном или беседе: собеседник = мы же
                interlocutor_info = bot_info
        
        # Логируем полученное сообщение
        logger.message_received(
            dialog_type,
            {'first_name': interlocutor_info['first_name'], 'last_name': interlocutor_info['last_name']},
            {'first_name': bot_first_name, 'last_name': bot_last_name},
            msg_text,
            is_own_message
        )
        
        # Обработка через модули
        processed_message = process_all_messages(msg_text, vk, peer_id, message_id, from_user_id, modules, settings_data, USER_ID)
        if processed_message is not None:
            msg_text = processed_message
        
        # Обработка ответов
        if hasattr(event, 'raw') and 'reply_message' in event.raw:
            reply_processed = process_reply_messages(event.raw, vk, peer_id, message_id, from_user_id, modules, settings_data, USER_ID)
            if reply_processed:
                logger.message_processed(dialog_type, True)
                continue
        
        # Обработка команд (только если сообщение от бота и начинается с префикса)
        if is_own_message and msg_text.startswith(prefix):
            # Хоткеи
            original_command = msg_text
            if len(msg_text) > len(prefix):
                command_without_prefix = msg_text[len(prefix):]
                command_parts = command_without_prefix.split()
                command = command_parts[0] if command_parts else ""
                
                if command in hotkeys:
                    new_text = hotkeys[command]
                    if len(command_parts) > 1:
                        new_text += " " + " ".join(command_parts[1:])
                    msg_text = new_text
                    logger.hotkey_used(original_command, msg_text)
            
            # Выполняем команду
            result_message = process_command(vk, peer_id, message_id, msg_text, hotkeys, modules, settings_data, USER_ID)
            
            # Обработка результата - БЕЗ ФИЛЬТРОВ
            if result_message and result_message.strip():
                try:
                    vk.messages.edit(
                        peer_id=peer_id,
                        message_id=message_id,
                        message=result_message
                    )
                    logger.message_processed(dialog_type, True)
                except Exception as e:
                    logger.error(f"Ошибка редактирования: {e}")
            else:
                # Если команда вернула пустую строку или None - просто логируем
                logger.message_processed(dialog_type, True)
        
        # Обработка сообщений от любого пользователя через модули
        message_handled = False
        for module_name, module in modules.items():
            try:
                if hasattr(module, 'on_any_message'):
                    result = module.on_any_message(msg_text, vk, peer_id, message_id, from_user_id, USER_ID, settings_data)
                    if result is not None:
                        message_handled = True
                        break
            except Exception as e:
                pass  # Молча игнорируем ошибки в модулях
        
        if message_handled:
            logger.message_processed(dialog_type, True)

if __name__ == '__main__':
    main()