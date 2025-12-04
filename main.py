import os
import requests  # Используем обычные запросы, это надежнее

# 1. Настройки
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# ID голоса "Adam" (стандартный мужской голос)
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

# Тестовая история
STORY_TEXT = "Привет! Если ты слышишь этот голос, значит мы победили ошибку и сервер работает правильно."

def run_bot():
    print("--- ЗАПУСК БОТА (ВЕРСИЯ 2.0) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Не найден ключ ElevenLabs!")
        return

    print("1. Ключи на месте. Отправляем запрос в ElevenLabs...")

    # Прямой запрос к API (без использования глючной библиотеки)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_KEY
    }
    
    data = {
        "text": STORY_TEXT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Сохраняем файл
            save_path = "test_audio.mp3"
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"2. УСПЕХ! Аудио сохранено в {save_path}")
            print("Размер файла:", len(response.content), "байт")
        else:
            print(f"ОШИБКА API: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    run_bot()

if __name__ == "__main__":
    run_bot()
