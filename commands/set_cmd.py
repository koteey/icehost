def process_set_command(vk, message_id, peer_id, settings, command_text=None):
    """Обрабатывает команду set для установки кастомных сообщений"""
    from lib.settings import save_settings
    
    try:
        if command_text:
            # Если команда пришла как .set ping текст
            parts = command_text.split(' ', 2)  # Разделяем на 3 части: set, ping, текст
            if len(parts) < 3:
                return "❌ Неправильный формат. Используйте: .set <команда> <текст>"
            
            command_type = parts[1]
            message_text = parts[2]
        else:
            # Если команда пришла как .settings set (многострочное сообщение)
            messages = vk.messages.getById(message_ids=[message_id])
            if not messages['items']:
                return "❌ Не удалось получить информацию о сообщении"
            
            original_message = messages['items'][0]['text']
            
            # Проверяем, что это команда .settings set
            if not original_message.startswith('.settings set'):
                return "❌ Это не команда .settings set"
            
            # Разбираем команду - берем первую строку для определения типа
            first_line = original_message.split('\n')[0]
            parts = first_line.split()
            
            if len(parts) < 3:
                return "❌ Неправильный формат. Используйте: .settings set <команда> и текст на новых строках"
            
            command_type = parts[2]  # ping или info после .settings set
            
            # Извлекаем текст после ".settings set ping" 
            set_prefix = f".settings set {command_type}"
            set_pos = original_message.find(set_prefix)
            if set_pos == -1:
                return "❌ Ошибка парсинга команда"
            
            # Берем текст после команды
            message_text = original_message[set_pos + len(set_prefix):].strip()
        
        if command_type not in ['info', 'ping']:
            return "❌ Неверная команда. Доступно: info, ping"
        
        if not message_text:
            # Показать текущее сообщение и переменные
            current_message = settings['custom_messages'].get(command_type, '')
            variables = get_variables_for_command(command_type)
            
            response = f"📝 Текущее сообщение для .{command_type}:\n\n{current_message}\n\n"
            response += f"📋 Доступные переменные для .{command_type}:\n{variables}"
            response += f"\n\n💡 Чтобы изменить:\n• .set {command_type} ваш текст\n• Или: .settings set {command_type} и текст на новых строках"
            return response
        
        # Сохраняем сообщение
        settings['custom_messages'][command_type] = message_text
        
        if save_settings(settings):
            # Показываем как будет выглядеть сообщение
            preview = f"✅ Сообщение для .{command_type} обновлено!\n\n📝 Новый текст:\n{message_text}\n\n📋 Переменные будут заменены при выполнении команда"
            return preview
        else:
            return "❌ Ошибка сохранения настроек"
            
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def get_variables_for_command(command_type):
    """Возвращает список доступных переменных для команды"""
    import platform
    if command_type == 'info':
        return """{user_name} - Имя и фамилия пользователя
{user_id} - ID пользователя
{online_status} - Статус онлайн (✅/❌)
{os_info} - Информация об ОС
{python_version} - Версия Python
{architecture} - Архитектура системы
{uptime} - Время работы бота
{platform} - Платформа системы
{processor} - Процессор"""
    elif command_type == 'ping':
        return """{ping} - Сетевая задержка в ms
{uptime} - Время работы бота
{quality} - Качество соединения
{timestamp} - Текущее время
{status} - Статус бота"""
    return ""