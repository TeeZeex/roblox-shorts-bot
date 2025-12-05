import os
import requests
import random
import time
import gdown
from moviepy.editor import VideoFileClip, AudioFileClip

# --- НАСТРОЙКИ ---
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

# Ссылка на твое видео (твоя ссылка сохранена)
VIDEO_URL = "https://drive.google.com/file/d/1EB2FFQks8TWLZ85Ss7vyckpXIJescen9/view?usp=drive_link"
VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    """Скачивает видео с Google Drive"""
    if os.path.exists(VIDEO_FILENAME):
        print("✅ Видео уже есть на сервере.")
        return

    print("📥 Скачиваю видео с Google Drive (5 ГБ, жди 5-10 мин)...")
    try:
        # Используем gdown для скачивания
        output = gdown.download(VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        if output:
            print("✅ Видео успешно скачано!")
        else:
            print("⚠️ gdown ничего не вернул, проверяем файл...")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")

def run_bot():
    print("--- ЗАПУСК МОНТАЖЕРА v4.3 (SPEED UP 1.2x) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Нет ключа ElevenLabs")
        return

    # 1. Скачиваем фон
    download_video_from_drive()

    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео-файл. Проверь ссылку и права доступа.")
        return

    # 2. Генерируем голос
    print("🎤 Генерирую голос...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    
    story_text = "In the vast world of Roblox, a foggy night settled over everything. On the empty streets of Bloxburg, only the echo of footsteps could be heard. These footsteps belonged to an ordinary-looking player—a skinny boy with messy orange hair. Everyone knew him as Bacon Hair."
    
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

        # --- НОВЫЙ БЛОК: УСКОРЕНИЕ ---
        # atempo=1.20 означает ускорение на 20% без изменения тональности
        print("⚡ Ускоряю озвучку на 20%...")
        os.system('ffmpeg -y -i temp_audio.mp3 -filter:a "atempo=1.20" temp_audio_fast.mp3')
        # -----------------------------

        # 3. Монтаж
        print("🎬 Начинаю монтаж (это займет время)...")
        
        # ВАЖНО: Тут мы теперь берем файл temp_audio_fast.mp3 (ускоренный)
        audio = AudioFileClip("temp_audio_fast.mp3") 
        video = VideoFileClip(VIDEO_FILENAME)
        
        if video.duration < audio.duration:
            print("Ошибка: Видео короче, чем аудио!")
            return

        # Случайный старт
        max_start = video.duration - audio.duration
        start_time = random.uniform(0, max_start)
        
        print(f"✂️ Беру кусок: {start_time:.1f}с - {start_time + audio.duration:.1f}с")
        
        # Обрезка и Кроп
        final_clip = video.subclip(start_time, start_time + audio.duration)
        
        w, h = final_clip.size
        target_ratio = 9 / 16
        new_w = h * target_ratio
        
        # Кроп по центру + Ресайз
        final_clip = final_clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
        final_clip = final_clip.resize(height=1920)
        
        final_clip = final_clip.set_audio(audio)
        
        output_filename = "final_shorts.mp4"
        # preset='ultrafast' для скорости
        final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
        
        print("\n🎉 ВИДЕО ГОТОВО! Загружаю на Catbox...")

        # 4. ВЫГРУЗКА НА CATBOX
        with open(output_filename, 'rb') as f:
            try:
                upload_response = requests.post(
                    "https://catbox.moe/user/api.php", 
                    data={"reqtype": "fileupload"}, 
                    files={"fileToUpload": f}
                )
                
                if upload_response.status_code == 200:
                    print("\n" + "="*40)
                    print(f"👉 ТВОЕ ВИДЕО ТУТ: {upload_response.text}")
                    print("="*40 + "\n")
                else:
                    print(f"Ошибка Catbox: {upload_response.text}")
            except Exception as nav_err:
                print(f"Ошибка сети при загрузке: {nav_err}")

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")

    print("Сплю 1 час...")
    time.sleep(3600)

if __name__ == "__main__":
    run_bot()
