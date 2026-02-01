from lib.backup_utils import create_backup

def process(vk, settings, USER_ID):
    """Обрабатывает команду .backupall"""
    return create_backup(vk, settings, USER_ID)