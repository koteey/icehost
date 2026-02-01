from lib.logger import logger

def process_all_messages(message_text, vk, peer_id, message_id, from_user_id, modules, settings, USER_ID):
    """
    Обрабатывает ВСЕ сообщения через модули (даже без префикса)
    """
    for module_name, module in modules.items():
        try:
            # Пытаемся вызвать on_message_received если он есть
            if hasattr(module, 'on_message_received'):
                import inspect
                sig = inspect.signature(module.on_message_received)
                param_count = len(sig.parameters)
                
                if param_count == 4:
                    result = module.on_message_received(message_text, vk, peer_id, USER_ID)
                elif param_count == 5:
                    result = module.on_message_received(message_text, vk, peer_id, USER_ID, settings)
                elif param_count == 7:
                    result = module.on_message_received(message_text, vk, peer_id, message_id, from_user_id, USER_ID, settings)
                else:
                    logger.warning(f"Модуль {module_name} имеет несовместимую сигнатуру on_message_received ({param_count} аргументов)")
                    continue
                
                if result is not None:
                    logger.debug(f"Модуль {module_name} обработал сообщение")
                    return result
        except Exception as e:
            logger.error(f"Ошибка в модуле {module_name} (on_message_received): {e}")
    
    return None

def process_reply_messages(event_data, vk, peer_id, message_id, from_user_id, modules, settings, USER_ID):
    """
    Обрабатывает ответы на сообщения
    """
    try:
        reply_message = event_data.get('reply_message', {})
        if not reply_message:
            return False
        
        original_message_text = event_data.get('text', '')
        replied_message_id = reply_message.get('conversation_message_id')
        replied_user_id = reply_message.get('from_id')
        replied_text = reply_message.get('text', '')
        
        attachments = reply_message.get('attachments', [])
        
        for module_name, module in modules.items():
            try:
                if hasattr(module, 'on_reply_received'):
                    import inspect
                    sig = inspect.signature(module.on_reply_received)
                    param_count = len(sig.parameters)
                    
                    if param_count == 11:
                        result = module.on_reply_received(
                            original_message_text, replied_text, vk, peer_id, message_id, 
                            from_user_id, replied_user_id, replied_message_id, attachments, 
                            USER_ID, settings
                        )
                    else:
                        logger.warning(f"Модуль {module_name} имеет несовместимую сигнатуру on_reply_received")
                        continue
                    
                    if result is not None:
                        logger.debug(f"Модуль {module_name} обработал ответ")
                        return True
            except Exception as e:
                logger.error(f"Ошибка в модуле {module_name} (on_reply_received): {e}")
        
        return False
    except Exception as e:
        logger.error(f"Ошибка обработки ответов: {e}")
        return False

def process_other_events(event, vk, modules, settings, USER_ID):
    """
    Обрабатывает другие события LongPoll
    """
    event_type = event.type
    event_data = event.raw
    
    for module_name, module in modules.items():
        try:
            if hasattr(module, 'on_event'):
                result = module.on_event(
                    event_type,
                    event_data,
                    vk,
                    USER_ID,
                    settings
                )
                if result is not None:
                    logger.debug(f"Модуль {module_name} обработал событие {event_type}")
        except Exception as e:
            logger.error(f"Ошибка в модуле {module_name} (on_event): {e}")