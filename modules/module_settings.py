MODULE_INFO = {
    'name': 'Settings Manager',
    'version': '2.0',
    'description': 'Удобное управление настройками модулей',
    'author': 'SnowCode'
}

MODULE_COMMANDS = [
    'config список - показать все модули и их настройки',
    'config модули - показать только список модулей',
    'config получить <модуль> - показать настройки модуля',
    'config установить <модуль> <параметр> <значение> - изменить настройку',
    'config сбросить <модуль> - сбросить настройки модуля',
    'config создать <модуль> <параметр> <значение> - создать новую настройку',
    'config удалить <модуль> <параметр> - удалить настройку'
]

def process_command(command, vk, peer_id, user_id, settings=None):
    """
    Обрабатывает команды менеджера настроек
    """
    if command.startswith('config '):
        parts = command[7:].strip().split()
        
        if not parts:
            return show_config_help()
        
        action = parts[0]
        
        if action == 'список':
            return show_all_modules_with_settings(settings)
        
        elif action == 'модули':
            return show_installed_modules()
        
        elif action == 'получить':
            if len(parts) >= 2:
                module_name = parts[1]
                return get_module_settings(module_name, settings)
            else:
                return "❌ Укажите имя модуля: .config получить <имя_модуля>"
        
        elif action == 'установить':
            if len(parts) >= 4:
                module_name = parts[1]
                parameter = parts[2]
                value = ' '.join(parts[3:])
                return set_module_setting(module_name, parameter, value, settings)
            else:
                return "❌ Формат: .config установить <модуль> <параметр> <значение>"
        
        elif action == 'создать':
            if len(parts) >= 4:
                module_name = parts[1]
                parameter = parts[2]
                value = ' '.join(parts[3:])
                return create_module_setting(module_name, parameter, value, settings)
            else:
                return "❌ Формат: .config создать <модуль> <параметр> <значение>"
        
        elif action == 'удалить':
            if len(parts) >= 3:
                module_name = parts[1]
                parameter = parts[2]
                return delete_module_setting(module_name, parameter, settings)
            else:
                return "❌ Формат: .config удалить <модуль> <параметр>"
        
        elif action == 'сбросить':
            if len(parts) >= 2:
                module_name = parts[1]
                return reset_module_settings(module_name, settings)
            else:
                return "❌ Укажите имя модуля: .config сбросить <имя_модуля>"
        
        else:
            return show_config_help()
    
    return None

def show_config_help():
    """Показывает справку по командам config"""
    help_text = """
⚙️ **Менеджер настроек модулей**

**📋 Основные команды:**
`.config список` - все модули и их настройки
`.config модули` - только список установленных модулей
`.config получить <модуль>` - настройки модуля
`.config установить <модуль> <параметр> <значение>` - изменить настройку
`.config создать <модуль> <параметр> <значение>` - создать настройку
`.config удалить <модуль> <параметр>` - удалить настройку
`.config сбросить <модуль>` - сбросить все настройки модуля

**💡 Примеры:**
`.config модули` - список модулей
`.config получить calculator` - настройки калькулятора
`.config установить calculator precision 3` - точность 3 знака
`.config создать mymodule color blue` - создать настройку
`.config сбросить calculator` - сбросить настройки
"""
    return help_text.strip()

def show_installed_modules():
    """Показывает список установленных модулей"""
    import os
    modules_dir = 'modules'
    
    if not os.path.exists(modules_dir):
        return "📁 Папка modules не найдена"
    
    module_files = [f for f in os.listdir(modules_dir) if f.endswith('.py') and not f.startswith('_')]
    
    if not module_files:
        return "📭 Модули не установлены"
    
    result = ["📦 **Установленные модули:**\n"]
    
    for module_file in module_files:
        module_name = module_file[:-3]  # Убираем .py
        try:
            # Пытаемся получить информацию о модуле
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(modules_dir, module_file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'MODULE_INFO'):
                info = module.MODULE_INFO
                result.append(f"• **{module_name}** - {info.get('description', 'Нет описания')}")
            else:
                result.append(f"• **{module_name}** ⚠️ (нет MODULE_INFO)")
                
        except Exception as e:
            result.append(f"• **{module_name}** ❌ (ошибка загрузки: {str(e)})")
    
    result.append(f"\n📊 Всего модулей: {len(module_files)}")
    result.append("🔧 Используйте `.config получить имя_модуля` для просмотра настроек")
    
    return '\n'.join(result)

def show_all_modules_with_settings(settings):
    """Показывает все модули и их настройки"""
    import os
    
    # Получаем список установленных модулей
    modules_dir = 'modules'
    if not os.path.exists(modules_dir):
        return "📁 Папка modules не найдена"
    
    module_files = [f for f in os.listdir(modules_dir) if f.endswith('.py') and not f.startswith('_')]
    
    if not module_files:
        return "📭 Модули не установлены"
    
    result = ["⚙️ **Все модули и их настройки:**\n"]
    
    # Настройки из settings.json
    modules_settings = settings.get('modules', {})
    
    for module_file in module_files:
        module_name = module_file[:-3]
        
        # Информация о модуле
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(modules_dir, module_file))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'MODULE_INFO'):
                info = module.MODULE_INFO
                module_display = f"**📦 {module_name}** - {info.get('description', 'Нет описания')}"
            else:
                module_display = f"**📦 {module_name}** ⚠️"
                
        except Exception:
            module_display = f"**📦 {module_name}** ❌"
        
        result.append(module_display)
        
        # Настройки модуля
        if module_name in modules_settings:
            module_config = modules_settings[module_name]
            if module_config:
                for key, value in module_config.items():
                    result.append(f"  • {key} = `{value}`")
            else:
                result.append("  ⚠️ Настроек нет")
        else:
            result.append("  📝 Настроек нет (используйте .config создать)")
        
        result.append("")  # Пустая строка между модулями
    
    result.append(f"📊 Всего модулей: {len(module_files)}")
    result.append(f"⚙️ Модулей с настройками: {len(modules_settings)}")
    
    return '\n'.join(result).strip()

def get_module_settings(module_name, settings):
    """Показывает настройки конкретного модуля"""
    import os
    
    # Проверяем существует ли модуль
    module_path = os.path.join('modules', f'{module_name}.py')
    if not os.path.exists(module_path):
        return f"❌ Модуль '{module_name}' не найден"
    
    modules_settings = settings.get('modules', {})
    
    # Получаем информацию о модуле
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        module_info = ""
        if hasattr(module, 'MODULE_INFO'):
            info = module.MODULE_INFO
            module_info = f"**{info.get('name', module_name)}** v{info.get('version', '1.0')}\n"
            module_info += f"📝 {info.get('description', 'Нет описания')}\n"
            if hasattr(module, 'MODULE_COMMANDS'):
                commands = module.MODULE_COMMANDS
                module_info += f"🔧 Команд: {len(commands)}\n"
        else:
            module_info = f"**{module_name}** ⚠️ (нет информации)\n"
        
    except Exception as e:
        module_info = f"**{module_name}** ❌ (ошибка загрузки)\n"
    
    result = [f"⚙️ **Настройки модуля:**\n{module_info}"]
    
    if module_name in modules_settings:
        module_config = modules_settings[module_name]
        if module_config:
            result.append("\n**📋 Текущие настройки:**")
            for key, value in module_config.items():
                result.append(f"• **{key}** = `{value}`")
            
            result.append(f"\n💡 Всего настроек: {len(module_config)}")
        else:
            result.append("\n⚠️ Настроек нет")
    else:
        result.append("\n📝 Настроек нет")
    
    result.append(f"\n🔧 **Команды управления:**")
    result.append(f"`.config установить {module_name} параметр значение`")
    result.append(f"`.config создать {module_name} параметр значение`")
    result.append(f"`.config сбросить {module_name}`")
    
    return '\n'.join(result)

def set_module_setting(module_name, parameter, value, settings):
    """Устанавливает значение настройки модуля"""
    try:
        import os
        # Проверяем существует ли модуль
        module_path = os.path.join('modules', f'{module_name}.py')
        if not os.path.exists(module_path):
            return f"❌ Модуль '{module_name}' не найден"
        
        # Создаем секцию модуля если её нет
        if 'modules' not in settings:
            settings['modules'] = {}
        
        if module_name not in settings['modules']:
            settings['modules'][module_name] = {}
        
        # Преобразуем значения если нужно
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        # Сохраняем настройку
        old_value = settings['modules'][module_name].get(parameter, 'не установлено')
        settings['modules'][module_name][parameter] = value
        
        # Сохраняем в файл
        import json
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        return f"✅ Настройка обновлена!\n\n**Модуль:** {module_name}\n**Параметр:** {parameter}\n**Было:** `{old_value}`\n**Стало:** `{value}`"
    
    except Exception as e:
        return f"❌ Ошибка сохранения настройки: {str(e)}"

def create_module_setting(module_name, parameter, value, settings):
    """Создает новую настройку модуля"""
    try:
        import os
        # Проверяем существует ли модуль
        module_path = os.path.join('modules', f'{module_name}.py')
        if not os.path.exists(module_path):
            return f"❌ Модуль '{module_name}' не найден"
        
        # Проверяем существует ли уже настройка
        if 'modules' in settings and module_name in settings['modules']:
            if parameter in settings['modules'][module_name]:
                return f"❌ Настройка '{parameter}' уже существует в модуле '{module_name}'\nИспользуйте `.config установить` для изменения"
        
        # Создаем настройку
        return set_module_setting(module_name, parameter, value, settings)
    
    except Exception as e:
        return f"❌ Ошибка создания настройки: {str(e)}"

def delete_module_setting(module_name, parameter, settings):
    """Удаляет настройку модуля"""
    try:
        if 'modules' in settings and module_name in settings['modules']:
            if parameter in settings['modules'][module_name]:
                # Сохраняем значение для сообщения
                old_value = settings['modules'][module_name][parameter]
                
                # Удаляем настройку
                del settings['modules'][module_name][parameter]
                
                # Если у модуля больше нет настроек, удаляем его секцию
                if not settings['modules'][module_name]:
                    del settings['modules'][module_name]
                
                # Если секция modules пуста, удаляем её
                if not settings['modules']:
                    del settings['modules']
                
                # Сохраняем в файл
                import json
                with open('settings.json', 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                return f"✅ Настройка удалена!\n\n**Модуль:** {module_name}\n**Параметр:** {parameter}\n**Значение:** `{old_value}`"
            else:
                return f"❌ Настройка '{parameter}' не найдена в модуле '{module_name}'"
        else:
            return f"❌ Модуль '{module_name}' не найден в настройках"
    
    except Exception as e:
        return f"❌ Ошибка удаления настройки: {str(e)}"

def reset_module_settings(module_name, settings):
    """Сбрасывает все настройки модуля"""
    try:
        if 'modules' in settings and module_name in settings['modules']:
            # Сохраняем копию настроек для сообщения
            old_settings = settings['modules'][module_name].copy()
            
            # Удаляем настройки модуля
            del settings['modules'][module_name]
            
            # Если секция модулей пуста, удаляем её
            if not settings['modules']:
                del settings['modules']
            
            # Сохраняем в файл
            import json
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # Формируем сообщение
            result = [f"✅ Настройки модуля '{module_name}' сброшены!\n"]
            if old_settings:
                result.append("🗑️ Удаленные настройки:")
                for key, value in old_settings.items():
                    result.append(f"  • {key} = `{value}`")
            else:
                result.append("⚠️ Настроек не было")
            
            return '\n'.join(result)
        else:
            return f"❌ Модуль '{module_name}' не найден в настройках"
    
    except Exception as e:
        return f"❌ Ошибка сброса настроек: {str(e)}"