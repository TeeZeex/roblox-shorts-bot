import os
import requests
import random
import time
import gdown
from moviepy.editor import VideoFileClip, AudioFileClip

# --- НАСТРОЙКИ ---
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

# 👇 ВСТАВЬ СЮДА ССЫЛКУ НА ФАЙЛ С ГУГЛ ДИСКА (не на папку!)
VIDEO_URL = "https://drive.google.com/file/d/1EB2FFQks8TWLZ85Ss7vyckpXIJescen9/view?usp=drive_link" 
VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    """Скачивает видео с Google Drive"""
    if os.path.exists(VIDEO_FILENAME):
        print("✅ Видео уже есть на сервере.")
        return

    print("📥 Скачиваю видео с Google Drive (это может занять время)...")
    try:
        # gdown сам разберется с форматом ссылки и скачает файл
        gdown.download(VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        print("✅ Видео успешно скачано!")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")

def run_bot():
    print("--- ЗАПУСК МОНТАЖЕРА v4.0 (GOOGLE DRIVE) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Нет ключа ElevenLabs")
        return

    # 1. Скачиваем фон
    download_video_from_drive()

    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео-файл. Проверь ссылку.")
        return

    # 2. Генерируем голос
    print("🎤 Генерирую голос...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    
    # Текст истории
    story_text = "Представь, ты находишь секретную комнату в Роблоксе, о которой никто не знал. Я зашел туда и увидел такое, что пришлось удалить игру."
    
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
            
        with open("temp_audio.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Аудио готово.")

        # 3. Монтаж
        print("🎬 Начинаю монтаж...")
        audio = AudioFileClip("temp_audio.mp3")
        video = VideoFileClip(VIDEO_FILENAME)
        
        if video.duration < audio.duration:
            print("Ошибка: Видео короче, чем аудио!")
            return

        # Случайный старт
        max_start = video.duration - audio.duration
        start_time = random.uniform(0, max_start)
        
        print(f"✂️ Беру кусок: {start_time:.1f}с - {start_time + audio.duration:.1f}с")
        
        # Обрезка по времени
        final_clip = video.subclip(start_time, start_time + audio.duration)
        
        # Кроп под 9:16 (Shorts)
        w, h = final_clip.size
        target_ratio = 9 / 16
        new_w = h * target_ratio
        final_clip = final_clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
        final_clip = final_clip.resize(height=1920)
        
        # Звук
        final_clip = final_clip.set_audio(audio)
        
        output_filename = "final_shorts.mp4"
        final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24)
        
        print("\n🎉 ВИДЕО ГОТОВО! Загружаю ссылку...")

        # 4. Выгрузка
        with open(output_filename, 'rb') as f:
            upload = requests.put(f"https://transfer.sh/{output_filename}", data=f)
            print("\n" + "="*40)
            print(f"👉 СКАЧАТЬ ГОТОВОЕ ВИДЕО: {upload.text.strip()}")
            print("="*40 + "\n")

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")

    print("Сплю 1 час...")
    time.sleep(3600)

if __name__ == "__main__":
    run_bot()
