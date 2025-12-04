FROM python:3.9-slim

# ЭТА СТРОКА ВАЖНА: Она заставляет Python писать логи мгновенно
ENV PYTHONUNBUFFERED=1

# Устанавливаем системные библиотеки (FFmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Папка проекта
WORKDIR /app

# Копируем файлы
COPY . .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Запуск
CMD ["python", "main.py"]
