from lib.backup_utils import restore_backup

def process(vk, message_id, peer_id, USER_ID):
    """Обрабатывает команду .restoreall"""
    return restore_backup(vk, message_id, peer_id, USER_ID)