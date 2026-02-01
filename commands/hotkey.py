from lib.settings import save_hotkeys

def process(clean_command, hotkeys, settings):
    """Обрабатывает команды hotkey, hotlist, delhotkey"""
    prefix = settings['prefix']
    command_parts = clean_command.split()
    
    if command_parts[0] == 'hotkey' and len(command_parts) >= 3:
        alias = command_parts[1]
        target_command = ' '.join(command_parts[2:])
        
        if not target_command.startswith(prefix):
            target_command = prefix + target_command
        
        # Проверяем, существует ли такая команда
        valid_commands = ['info', 'ping', 'hotkey', 'hotlist', 'delhotkey', 'dm', 'modules', 'delm', 'settings', 'set', 'terminal', 'python', 'backupall', 'restoreall', 'accountinfo', 'vkapi', 'post', 'setname', 'setphoto', 'restart']
        if target_command[len(prefix):].split(' ')[0] not in valid_commands:
            return f"❌ Команда {target_command} не существует!"
        elif alias in hotkeys:
            return f"❌ Хоткей '{alias}' уже существует!"
        else:
            hotkeys[alias] = target_command
            save_hotkeys(hotkeys)
            return f"✅ Хоткей создан!\n• Алиас: {prefix}{alias}\n• Команда: {target_command}\n\nИспользуй: {prefix}{alias}"
    
    elif command_parts[0] == 'hotlist':
        if hotkeys:
            hotkey_list = "\n".join([f"• {prefix}{alias} → {cmd}" for alias, cmd in hotkeys.items()])
            return f"📋 Список хоткеев:\n{hotkey_list}"
        else:
            return f"📋 Список хоткеев пуст.\nСоздай хоткей: {prefix}hotkey алиас команда"
    
    elif command_parts[0] == 'delhotkey' and len(command_parts) == 2:
        alias = command_parts[1]
        if alias in hotkeys:
            del hotkeys[alias]
            save_hotkeys(hotkeys)
            return f"✅ Хоткей '{alias}' удален!"
        else:
            return f"❌ Хоткей '{alias}' не найден!"
    
    else:
        return f"""❌ Неправильный формат команды.
Доступные команды:
{prefix}hotkey алиас команда - создать хоткей
{prefix}hotlist - показать список хоткеев
{prefix}delhotkey алиас - удалить хоткей
Пример: {prefix}hotkey пинг ping"""