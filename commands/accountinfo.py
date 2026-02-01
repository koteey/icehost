def process(vk, USER_ID):
    """Обрабатывает команду .accountinfo"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='sex,bdate,city,country,photo_max_orig,online,domain,has_mobile,contacts,connections,site,education,universities,schools,status,last_seen,followers_count,common_count,occupation,nickname,relatives,relation,personal,interests,music,activities,movies,tv,books,games,about,quotes')[0]
        
        friends = vk.friends.get(user_id=USER_ID)['count']
        groups = vk.groups.get(user_id=USER_ID)['count']
        
        info_text = f"""👤 **ПОЛНАЯ ИНФОРМАЦИЯ ОБ АККАУНТЕ**

**📋 Основная информация:**
• Имя: {user_info.get('first_name', 'Не указано')} {user_info.get('last_name', 'Не указано')}
• ID: {USER_ID}
• Онлайн: {'✅' if user_info.get('online', 0) else '❌'}
• Статус: {user_info.get('status', 'Не установлен')}

**👥 Социальная информация:**
• Друзей: {friends}
• Подписок на группы: {groups}

**🔐 Уровень доступа:**
• Видит все сообщения: ✅
• Может публиковать везде: ✅
• Может изменять профиль: ✅
• Может управлять группами: ✅
• Полный доступ к API: ✅

**💡 Для управления используйте:**
• .vkapi <метод> <параметры> - выполнить любой метод VK API
• .post <текст> - опубликовать на стене
• .setphoto - установить аватар
• .setname <имя> <фамилия> - изменить имя"""
        
        return info_text
    except Exception as e:
        return f"❌ Ошибка получения информации: {str(e)}"