import requests

def download_file(url, filename):
    """Скачивает файл по URL"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
    except Exception as e:
        print(f"❌ Ошибка скачивания файла: {e}")
    return False