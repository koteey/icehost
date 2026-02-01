"""
Команда .copy - копирует сообщения с вложениями
"""

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает команду .copy"""
    
    try:
        # Сразу удаляем сообщение с командой
        try:
            vk.messages.delete(
                message_ids=message_id,
                delete_for_all=1
            )
        except:
            pass
        
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        if 'reply_message' not in message:
            return ""
        
        reply_message = message['reply_message']
        reply_text = reply_message.get('text', '')
        reply_attachments = reply_message.get('attachments', [])
        
        # Если нет ничего для копирования
        if not reply_text and not reply_attachments:
            return ""
        
        # Подготавливаем параметры
        params = {
            'peer_id': peer_id,
            'random_id': 0
        }
        
        # Добавляем текст
        if reply_text:
            params['message'] = reply_text
        
        # Добавляем вложения
        attachments = []
        for att in reply_attachments:
            att_type = att['type']
            
            if att_type == 'photo':
                photo = att['photo']
                attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
            
            elif att_type == 'video':
                video = att['video']
                attachments.append(f"video{video['owner_id']}_{video['id']}_{video.get('access_key', '')}")
            
            elif att_type == 'audio':
                audio = att['audio']
                attachments.append(f"audio{audio['owner_id']}_{audio['id']}")
            
            elif att_type == 'doc':
                doc = att['doc']
                attachments.append(f"doc{doc['owner_id']}_{doc['id']}")
            
            elif att_type == 'audio_message':
                audio_msg = att['audio_message']
                attachments.append(f"audio_message{audio_msg['owner_id']}_{audio_msg['id']}")
            
            elif att_type == 'sticker':
                sticker = att['sticker']
                attachments.append(f"sticker{sticker['product_id']}_{sticker['sticker_id']}")
        
        if attachments:
            params['attachment'] = ','.join(attachments)
        
        # Отправляем скопированное сообщение
        vk.messages.send(**params)
        
        return ""
        
    except Exception as e:
        return ""