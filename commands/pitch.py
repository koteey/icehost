"""
Команды .pitch и .speed - изменение тона и скорости аудио
"""

import os
import tempfile
import time
import requests
import subprocess
from lib.audio_utils import download_file, get_attachment_info

def change_pitch_speed(input_path, output_path, pitch_factor=1.0, speed_factor=1.0):
    """Изменяет тон и скорость аудио через FFmpeg"""
    try:
        # Команда FFmpeg для изменения тона и скорости
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-filter:a',
            f'atempo={speed_factor},asetrate=44100*{pitch_factor},aresample=44100',
            '-y',  # Перезаписать если файл существует
            output_path
        ]
        
        # Запускаем FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        
    except Exception as e:
        print(f"Ошибка изменения аудио: {e}")
        return False

def process_pitch(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .pitch"""
    return process_audio_effect(clean_command, vk, message_id, peer_id, user_id, effect_type='pitch')

def process_speed(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .speed"""
    return process_audio_effect(clean_command, vk, message_id, peer_id, user_id, effect_type='speed')

def process_audio_effect(clean_command, vk, message_id, peer_id, user_id, effect_type='pitch'):
    """Общая обработка аудио эффектов"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Парсим команду
        parts = clean_command.split()
        if len(parts) < 2:
            return ""
        
        try:
            factor = float(parts[1])
            
            # Ограничения
            if effect_type == 'pitch':
                if factor < 0.5 or factor > 2.0:  # От половинной до двойной высоты
                    return ""
            elif effect_type == 'speed':
                if factor < 0.5 or factor > 3.0:  # От половинной до тройной скорости
                    return ""
        except:
            return ""
        
        # Получаем сообщение
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
        output_filename = os.path.join(temp_dir, f"{effect_type}_{timestamp}.{ext}")
        
        # Скачиваем
        if not download_file(url, input_filename):
            return ""
        
        # Применяем эффект
        if effect_type == 'pitch':
            success = change_pitch_speed(input_filename, output_filename, pitch_factor=factor, speed_factor=1.0)
        else:  # speed
            success = change_pitch_speed(input_filename, output_filename, pitch_factor=1.0, speed_factor=factor)
        
        if not success:
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
        
    except Exception as e:
        print(f"Ошибка в .{effect_type}: {e}")
        return ""