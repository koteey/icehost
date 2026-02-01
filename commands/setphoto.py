"""
Команда .setphoto - установить новую фотографию профиля
"""

import os
import tempfile
import time
import requests
from lib.image_utils import download_image
from lib.media_utils import get_attachment_info

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает команду .setphoto"""
    
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
        
        # Проверяем есть ли фото в сообщении или в ответе
        photo_attachments = []
        
        # Ищем фото в самом сообщении
        if 'attachments' in message:
            for att in message['attachments']:
                if att['type'] == 'photo':
                    photo_attachments.append(att)
        
        # Ищем фото в ответе
        if 'reply_message' in message:
            reply_message = message['reply_message']
            if 'attachments' in reply_message:
                for att in reply_message['attachments']:
                    if att['type'] == 'photo':
                        photo_attachments.append(att)
        
        if not photo_attachments:
            return ""
        
        # Берем первую фотографию
        photo_att = photo_attachments[0]
        att_info = get_attachment_info(photo_att)
        
        if 'url' not in att_info:
            return ""
        
        # Создаем временный файл
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        
        photo_filename = os.path.join(temp_dir, f"profile_photo_{timestamp}.jpg")
        
        # Скачиваем фотографию
        if not download_image(att_info['url'], photo_filename):
            return ""
        
        # Загружаем фото для профиля
        upload_server = vk.photos.getOwnerPhotoUploadServer(owner_id=user_id)
        upload_url = upload_server['upload_url']
        
        with open(photo_filename, 'rb') as f:
            files = {'photo': f}
            response = requests.post(upload_url, files=files, timeout=120)
            
            if response.status_code != 200:
                return ""
            
            result = response.json()
            
            if 'error' in result:
                return ""
            
            # Сохраняем фото профиля
            save_result = vk.photos.saveOwnerPhoto(
                server=result['server'],
                photo=result['photo'],
                hash=result['hash']
            )
            
            if not save_result:
                return ""
            
        # Удаляем временный файл
        if os.path.exists(photo_filename):
            try:
                os.remove(photo_filename)
            except:
                pass
        
        return ""
        
    except:
        return ""