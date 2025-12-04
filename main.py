import os
import requests
import time

# Настройки
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

def run_bot():
    print("--- ЗАПУСК БОТА v2.3 (FIX TRANSFER) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Ключ не найден!")
        time.sleep(60)
        return

    # 1. Генерация аудио
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": "Привет! Если ты скачал этот файл по новой ссылке, значит мы готовы делать видео с Роблоксом!",
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
            print("2. Аудио готово.")

            # --- НОВЫЙ СПОСОБ ВЫГРУЗКИ (Transfer.sh) ---
            print("3. Загружаю на сервер...")
            with open(filename, 'rb') as f:
                # Используем PUT запрос, он надежнее для этого сервиса
                upload_url = f"https://transfer.sh/{filename}"
                upload_response = requests.put(upload_url, data=f)
                
                if upload_response.status_code == 200:
                    link = upload_response.text.strip()
                    print("\n" + "="*40)
                    print(f"👉 СКАЧАЙ АУДИО ТУТ: {link}")
                    print("="*40 + "\n")
                else:
                    print(f"Ошибка выгрузки: {upload_response.status_code}")
            # -------------------------------------------

        else:
            print(f"ОШИБКА API ElevenLabs: {response.status_code}")

    except Exception as e:
        print(f"ОШИБКА: {e}")
        
    print("Бот спит 10 минут...")
    time.sleep(600)

if __name__ == "__main__":
    run_bot()
