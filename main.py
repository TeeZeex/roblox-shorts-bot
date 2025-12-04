import os
import requests
import time

# Настройки
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

def run_bot():
    print("--- ЗАПУСК БОТА v2.2 (С ВЫВОДОМ ССЫЛКИ) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Ключ не найден!")
        time.sleep(60)
        return

    # 1. Генерация (как раньше)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": "Поздравляю! Если ты скачал этот файл, значит твой сервер на Railway полностью рабочий.",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    try:
        print("1. Генерирую аудио...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            filename = "test_audio.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            print("2. Аудио сохранено внутри сервера.")

            # --- НОВАЯ ЧАСТЬ: ВЫГРУЗКА ФАЙЛА ---
            print("3. Создаю ссылку для скачивания...")
            with open(filename, 'rb') as f:
                # Загружаем на временный хостинг file.io
                upload_response = requests.post('https://file.io', files={'file': f})
                if upload_response.status_code == 200:
                    link = upload_response.json().get('link')
                    print("\n" + "="*40)
                    print(f"👉 ТВОЙ ФАЙЛ ТУТ: {link}")
                    print("="*40 + "\n")
                else:
                    print("Ошибка выгрузки файла.")
            # -----------------------------------

        else:
            print(f"ОШИБКА API: {response.status_code}")

    except Exception as e:
        print(f"ОШИБКА: {e}")
        
    print("Жду 10 минут...")
    time.sleep(600)

if __name__ == "__main__":
    run_bot()
