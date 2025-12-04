import os
import requests
import time

# Настройки
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Голос Adam

def run_bot():
    print("--- ЗАПУСК БОТА v2.1 ---")
    
    # 1. Проверка ключа
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Ключ ElevenLabs не найден в переменных!")
        # Держим сервер живым, чтобы видеть логи
        time.sleep(60) 
        return

    print("1. Ключ найден. Пробуем озвучить текст...")

    # 2. Подготовка запроса
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": "Привет! Если ты слышишь это, значит новый код наконец-то заработал!",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    # 3. Отправка
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            print("2. УСПЕХ! Ответ от сервера получен.")
            with open("test_audio.mp3", "wb") as f:
                f.write(response.content)
            print("3. Файл test_audio.mp3 успешно сохранен!")
        else:
            print(f"ОШИБКА API: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        
    print("Бот завершил работу. Жду 10 минут...")
    time.sleep(600) # Чтобы контейнер не перезапускался постоянно

if __name__ == "__main__":
    run_bot()
