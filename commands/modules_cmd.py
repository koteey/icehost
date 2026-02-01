from lib.modules import install_module_from_file, delete_module, get_module_commands

def process(clean_command, vk, message_id, peer_id, modules):
    """Обрабатывает команды modules, dm, delm"""
    command_parts = clean_command.split()
    
    if command_parts[0] == 'modules':
        if modules:
            module_list = []
            for name, mod in modules.items():
                commands = get_module_commands(mod)
                commands_text = ", ".join(commands) if commands else "команды модуля"
                module_list.append(f"• {name} - {mod.MODULE_INFO.get('description', 'Нет описания')}\n  📝 Команды: {commands_text}")
            
            return f"📦 Загруженные модули ({len(modules)}):\n" + "\n\n".join(module_list)
        else:
            return "📦 Модули не загружены.\nДля установки модуля ответьте на файл .py командой .dm"
    
    elif command_parts[0] == 'dm':
        result_message = install_module_from_file(vk, message_id, peer_id)
        # Перезагружаем модули после установки
        if result_message.startswith("✅"):
            from lib.modules import load_modules
            modules.update(load_modules())
        return result_message
    
    elif command_parts[0] == 'delm' and len(command_parts) == 2:
        module_name = command_parts[1]
        return delete_module(module_name, modules)
    
    else:
        return """❌ Неправильный формат команды.
Доступные команды:
.modules - показать список модулей
.dm - установить модуль (ответьте на сообщение с файлом .py)
.delm имя - удалить модуль"""