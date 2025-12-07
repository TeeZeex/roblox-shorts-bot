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

# Ссылка на видео (Google Drive)
VIDEO_URL = "https://drive.google.com/file/d/1EB2FFQks8TWLZ85Ss7vyckpXIJescen9/view?usp=drive_link"
VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    # 1. Проверка существующего файла
    if os.path.exists(VIDEO_FILENAME):
        file_size_mb = os.path.getsize(VIDEO_FILENAME) / (1024 * 1024)
        if file_size_mb > 10: 
            print(f"✅ Видео уже есть на сервере ({file_size_mb:.1f} MB). Скачивание не требуется.")
            return
        else:
            print(f"⚠️ Найден битый файл. Удаляю...")
            os.remove(VIDEO_FILENAME)

    # 2. Попытка скачать с Google Drive
    print("📥 Скачиваю видео с Google Drive...")
    try:
        output = gdown.download(VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        if os.path.exists(VIDEO_FILENAME) and os.path.getsize(VIDEO_FILENAME) > 10 * 1024 * 1024:
            print("✅ Видео успешно скачано!")
            return
    except Exception as e:
        print(f"⚠️ Ошибка Google Drive: {e}")

def generate_gpt_story():
    print("🧠 ChatGPT пишет захватывающую историю (3 главы) на АНГЛИЙСКОМ...")
    
    if not OPENAI_KEY:
        print("⚠️ Нет ключа ChatGPT. Использую запасной текст.")
        return "Chapter 1. The Glitch. I saw a Bacon Hair walking through walls..."

    client = OpenAI(api_key=OPENAI_KEY)
    
    # ОБНОВЛЕННЫЙ ПРОМПТ (3 ГЛАВЫ + ИНТЕРЕС)
    prompt = (
        "Write a HIGHLY ENGAGING and SCARY story (creepypasta) about Roblox "
        "featuring a Bacon Hair character. "
        "MANDATORY REQUIREMENT: The story must consist of exactly 3 chapters. "
        "Format: 'Chapter 1: ...', 'Chapter 2: ...', 'Chapter 3: ...'. "
        "Total length should be enough for a 2-3 minute video. "
        "Make it very interesting with a shocking plot twist at the end. "
        "Do not use hashtags/emojis. Write in English."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-16k", 
            messages=[
                {"role": "system", "content": "You are a master of horror storytelling."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000 
        )
        story = completion.choices[0].message.content
        print(f"📝 История готова (Первые 100 символов): {story[:100]}...")
        return story
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return "Error generating story."

def upload_to_gofile(file_path):
    """Загрузка на Gofile.io (Самый надежный метод)"""
    print("🚀 Ищу лучший сервер для загрузки на Gofile...")
    
    # Заголовки, чтобы притвориться браузером
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 1. Получаем доступный сервер
        server_response = requests.get("https://api.gofile.io/getServer", headers=headers)
        
        if server_response.status_code != 200:
            print(f"Ошибка получения сервера Gofile: Код {server_response.status_code}")
            print(server_response.text)
            return None
        
        data = server_response.json()
        if data['status'] != 'ok':
            print(f"Ошибка API Gofile: {data}")
            return None
            
        server = data['data']['server']
        print(f"✅ Сервер найден: {server}")

        # 2. Загружаем файл
        print(f"📤 Загружаю файл на {server}...")
        with open(file_path, 'rb') as f:
            upload_response = requests.post(
                f"https://{server}.gofile.io/uploadFile",
                files={'file': f},
                headers=headers
            )
            
            if upload_response.status_code == 200:
                data = upload_response.json()
                if data['status'] == 'ok':
                    return data['data']['downloadPage']
                else:
                    print(f"Ошибка Gofile upload: {data}")
            else:
                print(f"Ошибка сети Gofile upload: {upload_response.status_code}")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
    return None

def make_video():
    print(f"\n--- НАЧАЛО ЦИКЛА v6.9 (GOFILE HEADERS FIX) ---")
    
    # if not ELEVENLABS_KEY:
    #     print("ОШИБКА: Нет ключа ElevenLabs")
    #     return

    # 1. Скачиваем
    download_video_from_drive()
    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео.")
        return

    # 2. Текст (Генерируем, чтобы проверить GPT, но озвучивать не будем)
    story_text = generate_gpt_story()

    # 3. Озвучка (ОТКЛЮЧЕНО)
    print("🎤 Озвучиваю... (ОТКЛЮЧЕНО: ЭКОНОМИЯ ПОИНТОВ)")
    # url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    # headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    # data = {
    #     "text": story_text,
    #     "model_id": "eleven_multilingual_v2",
    #     "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    # }

    # try:
    #     response = requests.post(url, json=data, headers=headers)
    #     if response.status_code != 200:
    #         print(f"Ошибка озвучки: {response.text}")
    #         return
    #     with open("temp_audio.mp3", "wb") as f:
    #         f.write(response.content)
    #     print("✅ Аудио записано.")
    # except Exception as e:
    #     print(f"Ошибка ElevenLabs: {e}")
    #     return
    
    # --- ВРЕМЕННАЯ ЗАГЛУШКА (10 секунд тишины), чтобы код не ломался ---
    print("⚠️ Создаю пустой аудиофайл для теста монтажа...")
    os.system('ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 -q:a 9 -acodec libmp3lame temp_audio.mp3 -y')
    # ------------------------------------------------------------------

    # Ускорение
    print("⚡ Ускоряю голос...")
    os.system('ffmpeg -y -i temp_audio.mp3 -filter:a "atempo=1.20" temp_audio_fast.mp3')

    # 4. Монтаж
    print("🎬 Монтирую...")
    try:
        audio = AudioFileClip("temp_audio_fast.mp3") 
        try:
            video = VideoFileClip(VIDEO_FILENAME)
        except:
            print("⚠️ Битое видео! Удаляю.")
            os.remove(VIDEO_FILENAME)
            return

        # Проверка длины
        if video.duration < audio.duration:
            print("🔄 Зацикливаю видео...")
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
        output_filename = "final_story_3ch.mp4"
        
        final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
        
        print("\n🎉 ВИДЕО ГОТОВО! Загружаю на Gofile...")

        # 5. Выгрузка (Gofile)
        link = upload_to_gofile(output_filename)
        
        if link:
            print("\n" + "="*40)
            print(f"👉 ТВОЕ ВИДЕО ТУТ: {link}")
            print("="*40 + "\n")
        else:
            print("❌ Не удалось загрузить видео.")

    except Exception as e:
        print(f"Ошибка монтажа: {e}")

def run_bot_loop():
    while True:
        try:
            make_video()
        except Exception as e:
            print(f"\n❌ ОБЩАЯ ОШИБКА: {e}")
        
        # 18 часов = 18 * 60 * 60 = 64800 секунд
        print("✅ Работа завершена. Сплю 18 часов перед следующим видео...")
        time.sleep(64800)

if __name__ == "__main__":
    run_bot_loop()
