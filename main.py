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
    print("--- ЗАПУСК БОТА v5.1 (GPT + BACON HAIR + SPEED 1.2x) ---")
    
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
            
        with open("temp_audio.mp3", "wb") as f:
            f.write(response.content)
        print("✅ Аудио записано.")

        # --- УСКОРЕНИЕ ГОЛОСА НА 20% ---
        print("⚡ Ускоряю озвучку на 20%...")
        # Используем FFmpeg для ускорения (atempo=1.20)
        os.system('ffmpeg -y -i temp_audio.mp3 -filter:a "atempo=1.20" temp_audio_fast.mp3')
        # -------------------------------

        # 4. МОНТАЖ
        print("🎬 Начинаю монтаж...")
        
        # Используем УСКОРЕННЫЙ файл
        audio = AudioFileClip("temp_audio_fast.mp3") 
        video = VideoFileClip(VIDEO_FILENAME)
        
        if video.duration < audio.duration:
            print("Ошибка: Видео короче, чем аудио!")
            return

        # Выбираем случайный момент старта
        max_start = video.duration - audio.duration
        start_time = random.uniform(0, max_start)
        
        print(f"✂️ Беру кусок: {start_time:.1f}с")
        
        # Обрезка видео по длине аудио
        final_clip = video.subclip(start_time, start_time + audio.duration)
        
        # Делаем вертикальным (9:16) - Crop по центру
        w, h = final_clip.size
        new_w = h * (9/16) # Рассчитываем ширину для вертикального видео
        final_clip = final_clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
        final_clip = final_clip.resize(height=1920) # Высокое качество
        
        final_clip = final_clip.set_audio(audio)
        
        output_filename = "final_shorts.mp4"
        # preset='ultrafast' делает рендер быстрее
        final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
        
        print("\n🎉 ВИДЕО ГОТОВО! Загружаю на Catbox...")

        # 5. ВЫГРУЗКА (Catbox)
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
