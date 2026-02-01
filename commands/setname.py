def process(clean_command, vk):
    """Обрабатывает команду .setname"""
    parts = clean_command[8:].strip().split(' ', 1)
    if len(parts) == 2:
        first_name, last_name = parts[0], parts[1]
        try:
            vk.account.saveProfileInfo(first_name=first_name, last_name=last_name)
            return f"✅ Имя изменено!\n\n👤 Новое имя: {first_name} {last_name}"
        except Exception as e:
            return f"❌ Ошибка изменения имени: {str(e)}"
    else:
        return "❌ Укажите имя и фамилию: .setname <имя> <фамилия>"