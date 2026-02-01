import os
import zipfile
import requests
import datetime
import time as time_module
import tempfile
import shutil

def create_backup(vk, settings, USER_ID):
    """Создает резервную копию всей папки юзербота"""
    temp_zip = None
    temp_py = None
    
    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")
        
        # Создаем временные файлы
        temp_dir = tempfile.gettempdir()
        timestamp = int(time_module.time())
        
        # Создаем ZIP архив
        temp_zip = os.path.join(temp_dir, f"backup_{timestamp}.zip")
        # Копия с расширением .py
        temp_py = os.path.join(temp_dir, f"backup_{timestamp}.py")
        
        # Имя файла для отправки (просто .py файл)
        backup_filename = f"auto_backup_{timestamp}.py"
        
        print(f"🔄 Создание архива...")
        
        # Собираем ВСЕ файлы из текущей директории
        files_to_backup = []
        
        for root, dirs, files in os.walk('.'):
            # Пропускаем временные директории
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv', 'temp', 'tmp']]
            
            for file in files:
                # Пропускаем временные файлы
                if file.endswith(('.pyc', '.log', '.tmp', '.bak')):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                files_to_backup.append((file_path, arcname))
        
        if not files_to_backup:
            return "❌ Не найдено файлов для бекапа!"
        
        print(f"📁 Найдено файлов: {len(files_to_backup)}")
        
        # Создаем ZIP архив
        files_added = 0
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, arcname in files_to_backup:
                try:
                    zipf.write(file_path, arcname)
                    files_added += 1
                    
                    if files_added % 50 == 0:
                        print(f"📦 Добавлено: {files_added}/{len(files_to_backup)}")
                        
                except Exception as e:
                    print(f"⚠️ Не удалось добавить {arcname}: {e}")
        
        print(f"✅ Создан ZIP архив: {files_added} файлов")
        
        # Копируем ZIP в файл с расширением .py
        with open(temp_zip, 'rb') as src, open(temp_py, 'wb') as dst:
            dst.write(src.read())
        
        file_size = os.path.getsize(temp_py)
        print(f"📊 Размер файла: {file_size} байт ({file_size/1024/1024:.2f} MB)")
        
        # Проверяем размер
        if file_size > 200 * 1024 * 1024:  # 200 MB
            return f"❌ Файл слишком большой: {file_size/1024/1024:.2f} MB"
        
        # Загружаем файл на сервер VK
        print("🔄 Загрузка на сервер VK...")
        
        # Получаем URL для загрузки
        upload_server = vk.docs.getMessagesUploadServer(type='doc', peer_id=USER_ID)
        upload_url = upload_server['upload_url']
        
        # Читаем файл
        with open(temp_py, 'rb') as f:
            # Просто загружаем как файл
            files = {'file': (backup_filename, f)}
            
            response = requests.post(upload_url, files=files, timeout=120)
            
            if response.status_code != 200:
                return f"❌ Ошибка загрузки: статус {response.status_code}"
            
            result = response.json()
            
            if 'error' in result:
                return f"❌ Ошибка VK: {result.get('error_descr', 'Неизвестная ошибка')}"
            
            if 'file' not in result:
                return "❌ Не получен ключ 'file' от сервера"
            
            # Сохраняем документ
            save_result = vk.docs.save(file=result['file'], title=backup_filename)
            
            if not save_result:
                return "❌ Не удалось сохранить документ"
            
            # Получаем последний загруженный документ
            docs = vk.docs.get(count=10)
            
            if not docs or 'items' not in docs or len(docs['items']) == 0:
                return "❌ Не удалось получить информацию о загруженном файле"
            
            # Берем последний документ (первый в списке)
            uploaded_doc = docs['items'][0]
            
            attachment = f"doc{uploaded_doc['owner_id']}_{uploaded_doc['id']}"
            
            # Отправляем сообщение в Избранное (без технических деталей)
            vk.messages.send(
                peer_id=USER_ID,
                message=f"✅ Backup создан\n📅 {date_str} {time_str}\n📁 {files_added} файлов",
                attachment=attachment,
                random_id=0
            )
        
        # В чат просто сообщаем что backup создан
        return f"✅ Backup создан и отправлен в Избранное\n📅 {date_str} {time_str}\n📁 {files_added} файлов"
        
    except Exception as e:
        error_details = f"{type(e).__name__}: {str(e)}"
        import traceback
        traceback.print_exc()
        return f"❌ Ошибка создания бекапа:\n{error_details}"
    
    finally:
        # Очищаем временные файлы
        for temp_file in [temp_zip, temp_py]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

def restore_backup(vk, message_id, peer_id, USER_ID):
    """Восстанавливает бекап из прикрепленного файла"""
    temp_file = None
    temp_zip = None
    
    try:
        # Получаем сообщение
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return "❌ Не удалось получить сообщение"
        
        message = messages['items'][0]
        
        # Ищем ЛЮБОЙ прикрепленный файл
        doc_file = None
        if 'attachments' in message:
            for attachment in message['attachments']:
                if attachment['type'] == 'doc':
                    doc = attachment['doc']
                    # Принимаем ЛЮБОЙ файл
                    doc_file = doc
                    break
        
        if not doc_file:
            return "❌ В сообщении нет прикрепленного файла!"
        
        file_url = doc_file['url']
        file_name = doc_file['title']
        file_ext = doc_file.get('ext', '')
        
        print(f"🔄 Восстановление из {file_name}")
        
        # Создаем временные файлы
        temp_dir = tempfile.gettempdir()
        timestamp = int(time_module.time())
        
        # Временный файл как скачали
        temp_file = os.path.join(temp_dir, f"restore_{timestamp}")
        # ZIP файл
        temp_zip = os.path.join(temp_dir, f"restore_{timestamp}.zip")
        
        # Скачиваем файл
        response = requests.get(file_url, stream=True, timeout=120)
        if response.status_code != 200:
            return f"❌ Ошибка скачивания"
        
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Пробуем разные способы открытия файла
        extracted_files = 0
        
        # Способ 1: Пробуем как ZIP (даже если расширение не .zip)
        try:
            # Сначала копируем файл с расширением .zip
            shutil.copy2(temp_file, temp_zip)
            
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"📁 Найдено файлов в архиве: {len(file_list)}")
                
                # Создаем бекап текущих файлов
                backup_dir = "backup_before_restore"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                for file in file_list:
                    try:
                        target_path = os.path.join('.', file)
                        
                        # Если файл уже существует, создаем бекап
                        if os.path.exists(target_path):
                            backup_path = os.path.join(backup_dir, file.replace('/', '_'))
                            try:
                                shutil.copy2(target_path, backup_path)
                            except:
                                pass
                        
                        # Создаем директорию если нужно
                        target_dir = os.path.dirname(target_path)
                        if target_dir and not os.path.exists(target_dir):
                            os.makedirs(target_dir, exist_ok=True)
                        
                        # Извлекаем файл
                        zip_ref.extract(file, '.')
                        extracted_files += 1
                        
                        # Логируем каждые 10 файлов
                        if extracted_files % 10 == 0:
                            print(f"📄 Извлечено: {extracted_files}/{len(file_list)}")
                        
                    except Exception as e:
                        print(f"⚠️ Ошибка извлечения {file}: {e}")
                
                print(f"✅ Извлечено файлов: {extracted_files}")
                
        except Exception as e:
            print(f"⚠️ Не ZIP архив: {e}")
            
            # Способ 2: Если это один файл .py, просто копируем его
            try:
                # Пробуем открыть файл и посмотреть содержимое
                with open(temp_file, 'rb') as f:
                    content = f.read(1024)  # Читаем первые 1024 байта
                    
                    # Проверяем, это ZIP архив с сигнатурой PK?
                    if content.startswith(b'PK'):
                        print("✅ Обнаружена ZIP сигнатура!")
                        # Пробуем еще раз открыть как ZIP
                        with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                            file_list = zip_ref.namelist()
                            for file in file_list:
                                try:
                                    target_path = os.path.join('.', file)
                                    target_dir = os.path.dirname(target_path)
                                    if target_dir and not os.path.exists(target_dir):
                                        os.makedirs(target_dir, exist_ok=True)
                                    
                                    zip_ref.extract(file, '.')
                                    extracted_files += 1
                                except:
                                    pass
                    else:
                        # Если не ZIP, просто копируем файл
                        shutil.copy2(temp_file, file_name)
                        extracted_files = 1
                        print(f"✅ Скопирован файл: {file_name}")
                        
            except Exception as e2:
                print(f"❌ Не удалось обработать файл: {e2}")
        
        if extracted_files == 0:
            return "❌ Не удалось восстановить файлы"
        
        # Создаем файл-флаг для автоматического перезапуска
        with open('.restart_flag', 'w') as f:
            f.write(str(int(time_module.time())))
        
        return f"✅ Восстановлено {extracted_files} файлов\n\n⚠️ Для применения изменений перезапустите бота командой:\n.restart"
            
    except Exception as e:
        error_details = f"{type(e).__name__}: {str(e)}"
        import traceback
        traceback.print_exc()
        return f"❌ Ошибка восстановления:\n{error_details}"
    
    finally:
        # Очищаем временные файлы
        for temp_f in [temp_file, temp_zip]:
            if temp_f and os.path.exists(temp_f):
                try:
                    os.remove(temp_f)
                except:
                    pass