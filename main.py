import os
import requests
import random
import time
import gdown
import urllib3 
from moviepy.editor import VideoFileClip, AudioFileClip
from openai import OpenAI

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- НАСТРОЙКИ ---
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# Ссылки
PRIMARY_VIDEO_URL = "https://drive.google.com/file/d/12bWc0UH4I0kI0Nu5OR6D_D5Oxdt53F3v/view?usp=drive_link"

VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    # 1. Проверка существующего файла
    if os.path.exists(VIDEO_FILENAME):
        file_size_mb = os.path.getsize(VIDEO_FILENAME) / (1024 * 1024)
        if file_size_mb > 10: # Если файл больше 10 МБ, считаем его нормальным
            print(f"✅ Видео уже есть на сервере ({file_size_mb:.1f} MB). Скачивание не требуется.")
            return
        else:
            print(f"⚠️ Найден битый или пустой файл ({file_size_mb:.1f} MB). Удаляю...")
            os.remove(VIDEO_FILENAME)

    # 2. Попытка скачать с Google Drive
    print("📥 Скачиваю видео с Google Drive...")
    try:
        output = gdown.download(PRIMARY_VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        # Проверяем, что скачалось
        if os.path.exists(VIDEO_FILENAME) and os.path.getsize(VIDEO_FILENAME) > 10 * 1024 * 1024:
            print("✅ Видео успешно скачано!")
            return
    except Exception as e:
        print(f"⚠️ Ошибка Google Drive: {e}")

def generate_gpt_story():
    print("🧠 ChatGPT пишет длинную историю (5 глав) на АНГЛИЙСКОМ...")
    
    if not OPENAI_KEY:
        print("⚠️ Нет ключа ChatGPT. Использую запасной текст.")
        return "Chapter 1. The Beginning. Yesterday I joined an empty server..."

    client = OpenAI(api_key=OPENAI_KEY)
    
    prompt = (
        "Write a captivating and scary story (creepypasta) about Roblox "
        "with the main character being a Bacon Hair. "
        "The story should feel like a scary fairy tale. "
        "MANDATORY REQUIREMENT: The story must consist of exactly 3 chapters. "
        "Format it as 'Chapter 1: ...', 'Chapter 2: ...' and so on. "
        "The story must be long, sufficient for a 2-3 minute reading time. "
        "Make the plot exciting with an unexpected ending in the 5th chapter. "
        "Do not use hashtags or emojis. Only plain text. "
        "Write the story entirely in English."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-16k", 
            messages=[
                {"role": "system", "content": "You are a professional horror story writer for YouTube."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000 
        )
        story = completion.choices[0].message.content
        print(f"📝 История готова (Первые 100 символов): {story[:100]}...")
        return story
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return "Error generating story. The Bacon Hair stole the script."

def make_video():
    """Основная логика создания видео"""
    print(f"\n--- НАЧАЛО ЦИКЛА v6.4 (NO BACKUP VIDEO) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Нет ключа ElevenLabs")
        return

    # 1. Скачиваем
    download_video_from_drive()
    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео.")
        return

    # 2. Текст
    story_text = generate_gpt_story()

    # 3. Озвучка
    print("🎤 Озвучиваю большой текст...")
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
    except Exception as e:
        print(f"Ошибка при запросе к ElevenLabs: {e}")
        return

    # Ускорение
    print("⚡ Ускоряю голос...")
    os.system('ffmpeg -y -i temp_audio.mp3 -filter:a "atempo=1.20" temp_audio_fast.mp3')

    # 4. Монтаж
    print("🎬 Монтирую...")
    try:
        audio = AudioFileClip("temp_audio_fast.mp3") 
        
        # БЕЗОПАСНАЯ ЗАГРУЗКА ВИДЕО
        try:
            video = VideoFileClip(VIDEO_FILENAME)
        except Exception as e:
            print(f"❌ ОШИБКА ВИДЕОФАЙЛА: {e}")
            print("⚠️ Файл битый! Удаляю его, чтобы в следующий раз скачать нормальный.")
            os.remove(VIDEO_FILENAME)
            return # Прерываем этот круг, начнем заново

        # Проверка длины
        if video.duration < audio.duration:
            print(f"🔄 Зацикливаю видео (Аудио: {audio.duration}с)...")
            loops = int(audio.duration / video.duration) + 1
            video = video.loop(n=loops) 

        # Выбираем кусок
        if video.duration > audio.duration + 60:
            max_start = video.duration - audio.duration
            start_time = random.uniform(0, max_start)
            final_clip = video.subclip(start_time, start_time + audio.duration)
        else:
            final_clip = video.subclip(0, audio.duration)
        
        # 9:16 Crop
        w, h = final_clip.size
        new_w = h * (9/16)
        final_clip = final_clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
        final_clip = final_clip.resize(height=1920)
        
        final_clip = final_clip.set_audio(audio)
        output_filename = "final_long_story.mp4"
        
        final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
        
        print("\n🎉 ВИДЕО ГОТОВО! Загружаю на tmpfiles.org...")

        # 5. Выгрузка
        with open(output_filename, 'rb') as f:
            upload_response = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f})
            if upload_response.status_code == 200:
                json_resp = upload_response.json()
                original_url = json_resp['data']['url']
                download_link = original_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                print("\n" + "="*40)
                print(f"👉 ТВОЕ ДЛИННОЕ ВИДЕО ТУТ: {download_link}")
                print("="*40 + "\n")
            else:
                print(f"Ошибка выгрузки: {upload_response.text}")

    except Exception as e:
        print(f"Ошибка монтажа: {e}")

def run_bot_loop():
    while True:
        try:
            make_video()
        except Exception as e:
            print(f"\n❌ ОБЩАЯ ОШИБКА: {e}")
        
        print("✅ Сплю 1 час...")
        time.sleep(3600)

if __name__ == "__main__":
    run_bot_loop()
