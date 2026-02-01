"""
Утилиты для работы с аудио через pydub
"""

import os
import sys
import tempfile
import requests
import subprocess
import time
from pydub import AudioSegment
from pydub.effects import normalize

def setup_pydub():
    """Настраивает pydub для работы с FFmpeg"""
    try:
        current_dir = os.getcwd()
        
        # Проверяем папку ffmpeg в текущей директории
        ffmpeg_dir = os.path.join(current_dir, 'ffmpeg')
        ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        ffprobe_exe = os.path.join(ffmpeg_dir, 'ffprobe.exe')
        
        if os.path.exists(ffmpeg_exe):
            # Добавляем в PATH
            os.environ['PATH'] = ffmpeg_dir + ';' + os.environ['PATH']
            
            # Устанавливаем пути для pydub
            AudioSegment.converter = ffmpeg_exe
            
            # Устанавливаем ffprobe если есть
            if os.path.exists(ffprobe_exe):
                try:
                    AudioSegment.ffprobe = ffprobe_exe
                except AttributeError:
                    os.environ['FFPROBE'] = ffprobe_exe
            
            # Тестируем FFmpeg
            try:
                result = subprocess.run([ffmpeg_exe, '-version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5,
                                      shell=True)
                if result.returncode == 0:
                    # Тестируем pydub
                    test_audio = AudioSegment.silent(duration=1000)
                    test_path = os.path.join(tempfile.gettempdir(), 'test_pydub.mp3')
                    test_audio.export(test_path, format='mp3')
                    
                    if os.path.exists(test_path):
                        os.remove(test_path)
                        return True
                    return False
                return False
                    
            except:
                return False
                
        else:
            # Пробуем найти в системе
            try:
                if sys.platform == "win32":
                    result = subprocess.run(['where', 'ffmpeg'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=2,
                                          shell=True)
                else:
                    result = subprocess.run(['which', 'ffmpeg'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=2)
                
                if result.returncode == 0:
                    system_path = result.stdout.strip().split('\n')[0]
                    AudioSegment.converter = system_path
                    
                    # Тестируем
                    test_audio = AudioSegment.silent(duration=100)
                    test_path = os.path.join(tempfile.gettempdir(), 'test.mp3')
                    test_audio.export(test_path, format='mp3')
                    
                    if os.path.exists(test_path):
                        os.remove(test_path)
                        return True
                        
            except:
                pass
            
            return False
            
    except:
        return False

# Настраиваем при импорте
setup_pydub()

def get_attachment_info(attachment):
    """Получает информацию о вложении"""
    att_type = attachment['type']
    
    if att_type == 'audio':
        audio = attachment['audio']
        return {
            'type': 'audio',
            'url': audio.get('url', ''),
            'duration': audio.get('duration', 0)
        }
    
    elif att_type == 'doc':
        doc = attachment['doc']
        return {
            'type': 'doc',
            'ext': doc.get('ext', 'mp3'),
            'url': doc.get('url', ''),
            'size': doc.get('size', 0)
        }
    
    elif att_type == 'audio_message':
        audio_msg = attachment['audio_message']
        return {
            'type': 'audio_message',
            'link_ogg': audio_msg.get('link_ogg', '')
        }
    
    return {'type': att_type}

def download_file(url, filename):
    """Скачивает файл"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
    except:
        return False
    return False

def convert_voice_to_mp3(input_path, output_path):
    """Конвертирует голосовое сообщение в MP3 через pydub"""
    try:
        if not os.path.exists(input_path):
            return False
        
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            return False
        
        # Загружаем аудио
        try:
            audio = AudioSegment.from_file(input_path, format="ogg")
        except:
            try:
                audio = AudioSegment.from_file(input_path)
            except:
                return False
        
        # Экспортируем в MP3
        try:
            audio.export(
                output_path, 
                format='mp3',
                bitrate='128k',
                tags={
                    'title': 'Voice Message',
                    'artist': 'VK Bot',
                    'album': 'Converted',
                    'date': '2024'
                },
                parameters=[
                    '-write_id3v1', '1',
                    '-id3v2_version', '3'
                ]
            )
        except:
            try:
                audio.export(output_path, format='mp3', bitrate='128k')
            except:
                return False
        
        return os.path.exists(output_path)
            
    except:
        return False

def convert_to_voice(input_path, output_path):
    """Конвертирует файл в голосовое сообщение через pydub"""
    try:
        if not os.path.exists(input_path):
            return False
        
        # Загружаем аудио
        audio = AudioSegment.from_file(input_path)
        
        # Ограничиваем длительность если слишком длинное
        max_duration = 5 * 60 * 1000
        if len(audio) > max_duration:
            audio = audio[:max_duration]
        
        # Конвертируем в OGG
        audio.export(output_path, format='ogg', codec='libvorbis', bitrate='64k')
        
        return os.path.exists(output_path)
            
    except:
        return False

def boost_audio(input_path, output_path, boost_factor):
    """Усиливает громкость аудио через pydub"""
    try:
        if not os.path.exists(input_path):
            return False
        
        # Загружаем аудио
        audio = AudioSegment.from_file(input_path)
        
        # Усиливаем громкость
        import math
        volume_dB = 20 * math.log10(boost_factor)
        boosted_audio = audio + volume_dB
        
        # Нормализуем
        normalized_audio = normalize(boosted_audio)
        
        # Сохраняем в том же формате
        ext = os.path.splitext(input_path)[1].lower()
        if ext == '.mp3':
            normalized_audio.export(output_path, format='mp3', bitrate='192k')
        elif ext == '.ogg':
            normalized_audio.export(output_path, format='ogg', bitrate='192k')
        else:
            normalized_audio.export(output_path, format='mp3', bitrate='192k')
        
        return os.path.exists(output_path)
            
    except:
        return False