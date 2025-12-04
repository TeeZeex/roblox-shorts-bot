import os
from elevenlabs.client import ElevenLabs
from openai import OpenAI

# 1. Настройки (берем ключи из Railway)
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Тестовая история
STORY_TEXT = "Привет! Это тестовый запуск твоего сервера на Railway. Если ты слышишь этот голос, значит, ключи работают и бот готов создавать контент по Роблоксу."

def run_bot():
    print("--- ЗАПУСК БОТА ---")

    # Проверка ключей
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Не найден ключ ElevenLabs!")
        return
    if not OPENAI_KEY:
        print("ОШИБКА: Не найден ключ OpenAI!")
        return

    print("1. Ключи найдены. Начинаем озвучку...")

    try:
        # Инициализация клиента ElevenLabs
        client = ElevenLabs(api_key=ELEVENLABS_KEY)

        # Генерация аудио
        audio = client.generate(
            text=STORY_TEXT,
            voice="Rachel", # Можешь поменять на "Adam" или другой
            model="eleven_multilingual_v2"
        )

        # Сохранение файла
        save_path = "test_audio.mp3"
        with open(save_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        print(f"2. УСПЕХ! Аудио сохранено в {save_path}")
        print("Теперь можно добавлять видео-монтаж.")

    except Exception as e:
        print(f"ПРОИЗОШЛА ОШИБКА: {e}")

if __name__ == "__main__":
    run_bot()
