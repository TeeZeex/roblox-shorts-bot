import os
import requests
import random
import time
import gdown
from moviepy.editor import VideoFileClip, AudioFileClip
from openai import OpenAI  # Библиотека для ChatGPT

# --- НАСТРОЙКИ ---
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") # Ключ ChatGPT
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

# Ссылка на твое видео (геймплей Roblox)
VIDEO_URL = "https://drive.google.com/file/d/1EB2FFQks8TWLZ85Ss7vyckpXIJescen9/view?usp=drive_link"
VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    """Скачивает видео с Google Drive"""
    if os.path.exists(VIDEO_FILENAME):
        print("✅ Видео уже есть на сервере.")
        return

    print("📥 Скачиваю видео с Google Drive (5 ГБ)...")
    try:
        # fuzzy=True помогает найти файл, даже если ссылка немного отличается
        output = gdown.download(VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        if output:
            print("✅ Видео успешно скачано!")
        else:
            print("⚠️ gdown ничего не вернул, проверяем файл...")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")

def generate_gpt_story():
    """Генерирует историю через ChatGPT"""
    print("🧠 ChatGPT придумывает историю про Bacon Hair...")
    
    if not OPENAI_KEY:
        print("⚠️ Нет ключа OPENAI_API_KEY. Использую запасной текст.")
        return "Вчера я зашел на пустой сервер и увидел Бэкон Хейра, который стоял спиной ко мне. Когда он повернулся, у него не было лица."

    client = OpenAI(api_key=OPENAI_KEY)
    
    # Промпт (Задание для ИИ)
    prompt = (
        "Напиши очень короткую, увлекательную и пугающую историю (крипипасту) для TikTok "
        "про Роблокс. Главный герой — Bacon Hair (Бэкон Хейр). "
        "История должна быть от первого лица. "
        "Максимум 3-4 предложения. Сделай неожиданную концовку. "
        "Не используй хештеги и смайлики. Только текст истории."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # Можно поменять на gpt-4o, если тариф позволяет
            messages=[
                {"role": "system", "content": "Ты сценарист вирусных видео для YouTube Shorts."},
                {"role": "user", "content": prompt}
            ]
        )
        story = completion.choices[0].message.content
        print(f"📝 История от GPT: {story}")
        return story
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return "Ошибка генерации истории. Бэкон Хейр следит за тобой."

def run_bot():
    print("--- ЗАПУСК БОТА v5.2 (PIXELDRAIN UPLOAD) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Нет ключа ElevenLabs")
        return

    # 1. Скачиваем фон
    download_video_from_drive()

    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео-файл.")
        return

    # 2. ГЕНЕРАЦИЯ ТЕКСТА (ChatGPT)
    story_text = generate_gpt_story()

    # 3. ОЗВУЧКА (ElevenLabs)
    print("🎤 Озвучиваю текст...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    
    data = {
        "text": story_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            print(f"Ошибка озвучки: {response.text}")
            return
            
        with
