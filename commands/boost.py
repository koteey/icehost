"""
Команда .boost / .bu - усиление громкости через pydub
"""

import os
import tempfile
import time
import requests
from lib.audio_utils import download_file, boost_audio, get_attachment_info

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .boost и .bu"""
    
    try:
        # Проверяем наличие FFmpeg
        try:
            from pydub import AudioSegment
            if not hasattr(AudioSegment, 'converter') or not AudioSegment.converter:
                vk.messages.send(
                    peer_id=peer_id,
                    message="❌ FFmpeg не настроен!",
                    random_id=0
                )
                return ""
        except ImportError:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Не установлен pydub!",
                random_id=0
            )
            return ""
        
        parts = clean_command.split()
        if len(parts) < 2:
            # Удаляем сообщение команды
            try:
                vk.messages.delete(message_ids=message_id, delete_for_all=1)
            except:
                pass
            return ""
        
        try:
            boost_factor = float(parts[1])
            if boost_factor < 1.0 or boost_factor > 5000.0:
                # Удаляем сообщение команды
                try:
                    vk.messages.delete(message_ids=message_id, delete_for_all=1)
                except:
                    pass
                return ""
        except:
            # Удаляем сообщение команды
            try:
                vk.messages.delete(message_ids=message_id, delete_for_all=1)
            except:
                pass
            return ""
        
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        # Ищем аудио
        audio_attachments = []
        
        if 'attachments' in message:
            for att in message['attachments']:
                if att['type'] in ['audio', 'audio_message', 'doc']:
                    audio_attachments.append(att)
        
        if 'reply_message' in message:
            reply_message = message['reply_message']
            if 'attachments' in reply_message:
                for att in reply_message['attachments']:
                    if att['type'] in ['audio', 'audio_message', 'doc']:
                        audio_attachments.append(att)
        
        if not audio_attachments:
            return ""
        
        # Берем первое
        audio_att = audio_attachments[0]
        att_info = get_attachment_info(audio_att)
        
        # URL для скачивания
        url = ''
        if 'url' in att_info:
            url = att_info['url']
        elif 'link_ogg' in att_info:
            url = att_info['link_ogg']
        
        if not url:
            return ""
        
        # Временные файлы
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        
        # Определяем расширение
        if att_info['type'] == 'audio_message':
            ext = 'ogg'
        elif att_info['type'] == 'doc':
            ext = att_info.get('ext', 'mp3')
            if not ext:
                ext = 'mp3'
        else:
            ext = 'mp3'
        
        input_filename = os.path.join(temp_dir, f"input_{timestamp}.{ext}")
        output_filename = os.path.join(temp_dir, f"boosted_{timestamp}.{ext}")
        
        # Скачиваем
        if not download_file(url, input_filename):
            return ""
        
        # Усиливаем
        if not boost_audio(input_filename, output_filename, boost_factor):
            for f in [input_filename, output_filename]:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass
            return ""
        
        # Загружаем обратно
        if att_info['type'] == 'audio_message':
            # Голосовое сообщение
            upload_server = vk.docs.getMessagesUploadServer(
                type='audio_message',
                peer_id=peer_id
            )
            
            with open(output_filename, 'rb') as f:
                files = {'file': ('voice.ogg', f, 'audio/ogg')}
                response = requests.post(upload_server['upload_url'], files=files, timeout=120)
                
                if response.status_code != 200:
                    return ""
                
                result = response.json()
                
                if 'file' not in result:
                    return ""
                
                save_result = vk.docs.save(file=result['file'], title='voice.ogg')
                
                if not save_result:
                    return ""
                
                uploaded_doc = save_result['audio_message']
                attachment = f"audio_message{uploaded_doc['owner_id']}_{uploaded_doc['id']}"
        else:
            # Обычный файл
            upload_server = vk.docs.getMessagesUploadServer(
                type='doc',
                peer_id=peer_id
            )
            
            with open(output_filename, 'rb') as f:
                files = {'file': (f'audio.{ext}', f)}
                response = requests.post(upload_server['upload_url'], files=files, timeout=120)
                
                if response.status_code != 200:
                    return ""
                
                result = response.json()
                
                if 'file' not in result:
                    return ""
                
                save_result = vk.docs.save(file=result['file'], title=f'audio.{ext}')
                
                if not save_result:
                    return ""
                
                docs = vk.docs.get(count=10)
                
                if not docs or 'items' not in docs or len(docs['items']) == 0:
                    return ""
                
                uploaded_doc = docs['items'][0]
                attachment = f"doc{uploaded_doc['owner_id']}_{uploaded_doc['id']}"
        
        # Отправляем
        vk.messages.send(
            peer_id=peer_id,
            attachment=attachment,
            random_id=0
        )
        
        # Чистим
        for f in [input_filename, output_filename]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        
        return ""
        
    except:
        return ""