def get_message_sender(vk, peer_id, message_id, user_id):
    """Определяет отправителя сообщения"""
    try:
        # Если это беседа (peer_id > 2000000000)
        if peer_id > 2000000000:
            messages = vk.messages.getByConversationMessageId(
                peer_id=peer_id,
                conversation_message_ids=[message_id]
            )
            if messages['items']:
                from_id = messages['items'][0].get('from_id')
                # Проверяем, не является ли это ответом на сообщение
                if 'reply_message' in messages['items'][0]:
                    reply_from_id = messages['items'][0]['reply_message'].get('from_id')
                    if reply_from_id:
                        from_id = reply_from_id
                return from_id
        else:
            # Для личных сообщений
            if peer_id == user_id:
                # Избранное - сообщение от нас
                return user_id
            else:
                # Личное сообщение от другого пользователя
                messages = vk.messages.getById(message_ids=[message_id])
                if messages['items']:
                    return messages['items'][0]['from_id']
    except Exception as e:
        print(f"❌ Ошибка при определении отправителя: {e}")
    
    return None

def get_message_details(vk, peer_id, message_id):
    """Получает детали сообщения"""
    try:
        if peer_id > 2000000000:  # Беседа
            messages = vk.messages.getByConversationMessageId(
                peer_id=peer_id,
                conversation_message_ids=[message_id]
            )
            if messages['items']:
                return messages['items'][0]
        else:  # Личные сообщения
            messages = vk.messages.getById(message_ids=[message_id])
            if messages['items']:
                return messages['items'][0]
    except Exception as e:
        print(f"❌ Ошибка получения деталей сообщения: {e}")
    
    return None

def is_own_message(vk, peer_id, message_id, user_id):
    """Проверяет, является ли сообщение своим"""
    from_id = get_message_sender(vk, peer_id, message_id, user_id)
    return from_id == user_id

def measure_network_latency(vk):
    """Измеряет сетевую задержку до API VK"""
    import time
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