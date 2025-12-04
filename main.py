import os
import requests
import time

# Настройки
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

def run_bot():
    print("--- ЗАПУСК БОТА (СТАБИЛЬНАЯ ВЕРСИЯ) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Ключ не найден!")
        time.sleep(60)
        return

    # Настройки для ElevenLabs
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": "Системы в норме. Озвучка работает. Мы готовы приступать к созданию видео.",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    try:
        print("1. Отправляю текст в ElevenLabs...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Сохраняем файл внутри сервера
            with open("test_audio.mp3", "wb") as f:
                f.write(response.content)
            
            print("\n" + "="*40)
            print("✅ УСПЕХ! АУДИО ФАЙЛ СОЗДАН И ЛЕЖИТ НА СЕРВЕРЕ")
            print("Теперь можно накладывать его на видео.")
            print("="*40 + "\n")
            
        else:
            print(f"ОШИБКА API: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        
    print("Бот переходит в режим ожидания (чтобы не перезапускаться)...")
    time.sleep(600)

if __name__ == "__main__":
    run_bot()
