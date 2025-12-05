import os
import requests
import random
import time
import gdown
import urllib3 # Для отключения предупреждений SSL
from moviepy.editor import VideoFileClip, AudioFileClip
from openai import OpenAI

# Отключаем предупреждения о небезопасном соединении (так как мы используем verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- НАСТРОЙКИ ---
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# Ссылка на твое видео (Google Drive) - может быть заблокирована квотой
PRIMARY_VIDEO_URL = "https://drive.google.com/file/d/1EB2FFQks8TWLZ85Ss7vyckpXIJescen9/view?usp=drive_link"
# Запасная ссылка (Parkour Gameplay), если Google заблокирует основную
BACKUP_VIDEO_URL = "https://videos.pexels.com/video-files/5196323/5196323-hd_1920_1080_25fps.mp4"

VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    if os.path.exists(VIDEO_FILENAME):
        print("✅ Видео уже есть на сервере. Скачивание не требуется.")
        return

    print("📥 Попытка 1: Скачиваю основное видео с Google Drive...")
    try:
        # Пытаемся скачать оригинал
        output = gdown.download(PRIMARY_VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        
        if output and os.path.exists(VIDEO_FILENAME):
            print("✅ Основное видео успешно скачано!")
            return
    except Exception as e:
        print(f"⚠️ Ошибка Google Drive: {e}")
    
    # Если мы здесь, значит основное видео не скачалось (квота или ошибка)
    print("\n⚠️ Google Drive заблокировал файл (квота превышена).")
    print("📥 Попытка 2: Скачиваю ЗАПАСНОЕ видео (Parkour Gameplay)...")
    
    try:
        response = requests.get(BACKUP_VIDEO_URL, stream=True, verify=False)
        with open(VIDEO_FILENAME, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print("✅ Запасное видео успешно скачано!")
    except Exception as e:
        print(f"❌ Критическая ошибка скачивания: {e}")

def generate_gpt_story():
    print("🧠 ChatGPT пишет длинную историю (5 глав) на АНГЛИЙСКОМ...")
    
    if not OPENAI_KEY:
        print("⚠️ Нет ключа ChatGPT. Использую запасной текст.")
        return "Chapter 1. The Beginning. Yesterday I joined an empty server..."

    client = OpenAI(api_key=OPENAI_KEY)
    
    # ОБНОВЛЕННЫЙ ПРОМПТ (ТЕПЕРЬ НА АНГЛИЙСКОМ)
    prompt = (
        "Write a captivating and scary story (creepypasta) about Roblox "
        "with the main character being a Bacon Hair. "
        "The story should feel like a scary fairy tale. "
        "MANDATORY REQUIREMENT: The story must consist of exactly 5 chapters. "
        "Format it as 'Chapter 1: ...', 'Chapter 2: ...' and so on. "
        "The story must be long, sufficient for a 3-5 minute reading time. "
        "Make the plot exciting with an unexpected ending in the 5th chapter. "
        "Do not use hashtags or emojis. Only plain text. "
        "Write the story entirely in English."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-16k", # Используем модель с большим контекстом
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
    print(f"\n--- НАЧАЛО ЦИКЛА v6.2 (SMART DOWNLOADER) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Нет ключа ElevenLabs")
        return

    # 1. Скачиваем (Сначала пробуем Drive, потом запасное)
    download_video_from_drive()
    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео ни на Drive, ни на резерве.")
        return

    # 2. Текст
    story_text = generate_gpt_story()

    # 3. Озвучка
    print("🎤 Озвучиваю большой текст (это займет время)...")
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
    print("🎬 Монтирую (рендеринг длинного видео)...")
    try:
        audio = AudioFileClip("temp_audio_fast.mp3") 
        video = VideoFileClip(VIDEO_FILENAME)
        
        # Проверка: Хватит ли длины фона?
        if video.duration < audio.duration:
            print(f"⚠️ ВНИМАНИЕ: Видео (фон) короче аудио! Аудио: {audio.duration}с, Фон: {video.duration}с")
            print("🔄 Зацикливаю видео, чтобы хватило на всю историю...")
            loops = int(audio.duration / video.duration) + 1
            video = video.loop(n=loops) 

        # Выбираем случайный старт
        # Если видео намного длиннее аудио (с запасом), выбираем случайный кусок
        if video.duration > audio.duration + 60:
            max_start = video.duration - audio.duration
            start_time = random.uniform(0, max_start)
            final_clip = video.subclip(start_time, start_time + audio.duration)
        else:
            # Если видео впритык (или после зацикливания), берем с начала
            final_clip = video.subclip(0, audio.duration)
        
        # 9:16 Crop
        w, h = final_clip.size
        new_w = h * (9/16)
        final_clip = final_clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
        final_clip = final_clip.resize(height=1920)
        
        final_clip = final_clip.set_audio(audio)
        output_filename = "final_long_story.mp4"
        
        # preset='ultrafast' критичен для длинных видео
        final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
        
        print("\n🎉 ВИДЕО ГОТОВО! Загружаю на tmpfiles.org...")

        # 5. Выгрузка (tmpfiles.org)
        with open(output_filename, 'rb') as f:
            upload_response = requests.post(
                "https://tmpfiles.org/api/v1/upload", 
                files={"file": f}
            )
            
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
    """Вечный цикл"""
    while True:
        try:
            make_video()
        except Exception as e:
            print(f"\n❌ ПРОИЗОШЛА ОШИБКА: {e}")
            print("Не выключаюсь. Попробую снова через час.")
        
        print("✅ Работа завершена. Сплю 1 час...")
        time.sleep(3600)

if __name__ == "__main__":
    run_bot_loop()
