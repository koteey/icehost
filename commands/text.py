"""
Команда .text - добавляет текст на фотографию (увеличенный шрифт)
"""

import os
import tempfile
import time
import requests
from lib.image_utils import download_image, add_text_to_image
from lib.media_utils import get_attachment_info

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает команду .text"""
    
    # Парсим команду: .text [1/2] [текст]
    parts = clean_command.split(maxsplit=2)
    if len(parts) < 3:
        # Удаляем сообщение с командой
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        return ""
    
    position = parts[1]  # 1 или 2
    text = parts[2]
    
    # Преобразуем 1/2 в top/bottom
    if position == '1':
        position = 'top'
    elif position == '2':
        position = 'bottom'
    else:
        # Удаляем сообщение с командой
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        return ""
    
    try:
        # УДАЛЯЕМ СООБЩЕНИЕ С КОМАНДОЙ ПЕРЕД ОБРАБОТКОЙ
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        if 'reply_message' not in message:
            return ""
        
        reply_message = message['reply_message']
        reply_attachments = reply_message.get('attachments', [])
        
        # Ищем фотографии
        photo_attachments = []
        for att in reply_attachments:
            if att['type'] == 'photo':
                photo_attachments.append(att)
        
        if not photo_attachments:
            return ""
        
        # Берем первую фотографию
        photo_att = photo_attachments[0]
        att_info = get_attachment_info(photo_att)
        
        if 'url' not in att_info:
            return ""
        
        # Создаем временные файлы
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        
        input_filename = os.path.join(temp_dir, f"photo_{timestamp}.jpg")
        output_filename = os.path.join(temp_dir, f"text_{timestamp}.jpg")
        
        # Скачиваем фотографию
        if not download_image(att_info['url'], input_filename):
            return ""
        
        # Добавляем текст с УВЕЛИЧЕННЫМ размером шрифта (60 вместо 40)
        if not add_text_to_image(input_filename, output_filename, text, position, font_size=80):
            # Удаляем временные файлы
            if os.path.exists(input_filename):
                try:
                    os.remove(input_filename)
                except:
                    pass
            return ""
        
        # Загружаем на сервер VK
        upload_server = vk.photos.getMessagesUploadServer(peer_id=peer_id)
        upload_url = upload_server['upload_url']
        
        with open(output_filename, 'rb') as f:
            files = {'photo': f}
            response = requests.post(upload_url, files=files, timeout=120)
            
            if response.status_code != 200:
                return ""
            
            result = response.json()
            
            if 'error' in result:
                return ""
            
            # Сохраняем фото
            save_result = vk.photos.saveMessagesPhoto(
                server=result['server'],
                photo=result['photo'],
                hash=result['hash']
            )
            
            if not save_result or len(save_result) == 0:
                return ""
            
            saved_photo = save_result[0]
            attachment = f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
            
            # Отправляем фото с текстом
            vk.messages.send(
                peer_id=peer_id,
                attachment=attachment,
                random_id=0
            )
        
        # Удаляем временные файлы
        for f in [input_filename, output_filename]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .text: {e}")
        # Удаляем сообщение с командой даже при ошибке
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        return ""