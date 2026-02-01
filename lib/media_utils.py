"""
Утилиты для работы с медиа
"""

import os
import requests
import tempfile
import time
from .file_utils import download_file

def get_attachment_info(attachment):
    """Получает информацию о вложении"""
    att_type = attachment['type']
    
    if att_type == 'photo':
        photo = attachment['photo']
        # Берем самую большую доступную фотографию
        sizes = photo.get('sizes', [])
        if sizes:
            # Ищем размер type='z' или 'y' или 'x' или 'm'
            for size_type in ['z', 'y', 'x', 'm', 's']:
                for size in sizes:
                    if size.get('type') == size_type:
                        return {
                            'type': 'photo',
                            'url': size['url'],
                            'width': size.get('width'),
                            'height': size.get('height')
                        }
    
    elif att_type == 'video':
        video = attachment['video']
        return {
            'type': 'video',
            'title': video.get('title', ''),
            'duration': video.get('duration', 0),
            'owner_id': video['owner_id'],
            'id': video['id'],
            'access_key': video.get('access_key', '')
        }
    
    elif att_type == 'audio':
        audio = attachment['audio']
        return {
            'type': 'audio',
            'artist': audio.get('artist', ''),
            'title': audio.get('title', ''),
            'url': audio.get('url', ''),
            'duration': audio.get('duration', 0)
        }
    
    elif att_type == 'doc':
        doc = attachment['doc']
        return {
            'type': 'doc',
            'title': doc.get('title', ''),
            'ext': doc.get('ext', ''),
            'url': doc.get('url', ''),
            'size': doc.get('size', 0)
        }
    
    elif att_type == 'audio_message':
        audio_msg = attachment['audio_message']
        return {
            'type': 'audio_message',
            'duration': audio_msg.get('duration', 0),
            'link_mp3': audio_msg.get('link_mp3', ''),
            'link_ogg': audio_msg.get('link_ogg', '')
        }
    
    return {'type': att_type}

def download_attachment(attachment_info, filename=None):
    """Скачивает вложение"""
    try:
        if not filename:
            # Создаем временный файл
            ext = ''
            if 'ext' in attachment_info:
                ext = attachment_info['ext']
            elif attachment_info['type'] == 'photo':
                ext = 'jpg'
            elif attachment_info['type'] == 'audio_message':
                ext = 'mp3'
            
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f"attachment_{int(time.time())}.{ext}")
        
        url = None
        if 'url' in attachment_info:
            url = attachment_info['url']
        elif 'link_mp3' in attachment_info:
            url = attachment_info['link_mp3']
        
        if url and download_file(url, filename):
            return filename
        
    except Exception as e:
        print(f"❌ Ошибка скачивания вложения: {e}")
    
    return None