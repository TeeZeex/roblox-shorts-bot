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

# Ссылка на видео (Google Drive)
VIDEO_URL = "https://drive.google.com/file/d/1EB2FFQks8TWLZ85Ss7vyckpXIJescen9/view?usp=drive_link"
VIDEO_FILENAME = "background_gameplay.mp4"

def download_video_from_drive():
    if os.path.exists(VIDEO_FILENAME):
        print("✅ Видео уже есть на сервере. Скачивание не требуется.")
        return

    print("📥 Скачиваю видео с Google Drive (5 ГБ)...")
    try:
        output = gdown.download(VIDEO_URL, VIDEO_FILENAME, quiet=False, fuzzy=True)
        if output:
            print("✅ Видео успешно скачано!")
        else:
            print("⚠️ gdown ничего не вернул, проверяем файл...")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")

def generate_gpt_story():
    print("🧠 ChatGPT придумывает историю...")
    
    if not OPENAI_KEY:
        print("⚠️ Нет ключа ChatGPT. Использую запасной текст.")
        return "Вчера я зашел на пустой сервер и увидел Бэкон Хейра, который стоял спиной ко мне. Когда он повернулся, у него не было лица."

    client = OpenAI(api_key=OPENAI_KEY)
    
    prompt = (
        "Напиши очень короткую, пугающую историю (крипипасту) для TikTok "
        "про Роблокс. Главный герой — Bacon Hair (Бэкон Хейр). "
        "Максимум 3-4 предложения. Сделай неожиданную концовку. "
        "Не используй хештеги и смайлики."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты сценарист вирусных видео."},
                {"role": "user", "content": prompt}
            ]
        )
        story = completion.choices[0].message.content
        print(f"📝 История: {story}")
        return story
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return "Ошибка генерации истории. Бэкон Хейр следит за тобой."

def make_video():
    """Основная логика создания видео"""
    print(f"\n--- НАЧАЛО ЦИКЛА v5.4 (NO-SSL + LOOP) ---")
    
    if not ELEVENLABS_KEY:
        print("ОШИБКА: Нет ключа ElevenLabs")
        return

    # 1. Скачиваем (Если файл уже есть, функция просто выйдет)
    download_video_from_drive()
    if not os.path.exists(VIDEO_FILENAME):
        print("❌ Не удалось найти видео.")
        return

    # 2. Текст
    story_text = generate_gpt_story()

    # 3. Озвучка
    print("🎤 Озвучиваю...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": story_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка озвучки: {response.text}")
        return
        
    with open("temp_audio.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Аудио записано.")

    # Ускорение
    print("⚡ Ускоряю голос...")
    os.system('ffmpeg -y -i temp_audio.mp3 -filter:a "atempo=1.20" temp_audio_fast.mp3')

    # 4. Монтаж
    print("🎬 Монтирую...")
    audio = AudioFileClip("temp_audio_fast.mp3") 
    video = VideoFileClip(VIDEO_FILENAME)
    
    if video.duration < audio.duration:
        print("Ошибка: Видео короче аудио!")
        return

    max_start = video.duration - audio.duration
    start_time = random.uniform(0, max_start)
    
    final_clip = video.subclip(start_time, start_time + audio.duration)
    
    # 9:16 Crop
    w, h = final_clip.size
    new_w = h * (9/16)
    final_clip = final_clip.crop(x1=w/2 - new_w/2, width=new_w, height=h)
    final_clip = final_clip.resize(height=1920)
    
    final_clip = final_clip.set_audio(audio)
    output_filename = "final_shorts.mp4"
    
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
    
    print("\n🎉 ВИДЕО ГОТОВО! Загружаю на PixelDrain...")

    # 5. Выгрузка (PixelDrain) с отключенной проверкой SSL
    with open(output_filename, 'rb') as f:
        upload_response = requests.post(
            "https://pixeldrain.com/api/file", 
            files={"file": f},
            auth=('', ''),
            verify=False # <--- ИГНОРИРУЕМ ОШИБКИ SSL
        )
        if upload_response.status_code == 201:
            file_id = upload_response.json().get("id")
            link = f"https://pixeldrain.com/u/{file_id}"
            print("\n" + "="*40)
            print(f"👉 ТВОЕ ВИДЕО ТУТ: {link}")
            print("="*40 + "\n")
        else:
            print(f"Ошибка выгрузки: {upload_response.text}")

def run_bot_loop():
    """Вечный цикл, чтобы бот не выключался и не удалял видео"""
    while True:
        try:
            make_video()
        except Exception as e:
            print(f"\n❌ ПРОИЗОШЛА ОШИБКА: {e}")
            print("Не выключаюсь, видео на месте. Попробую снова через час.")
        
        print("✅ Работа завершена. Сплю 1 час перед следующим видео...")
        time.sleep(3600) # Ждем 1 час

if __name__ == "__main__":
    run_bot_loop()
