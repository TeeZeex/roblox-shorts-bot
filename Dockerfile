FROM python:3.9-slim

# Устанавливаем системные библиотеки для работы с видео
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Создаем папку проекта
WORKDIR /app

# Копируем файлы
COPY . .

# Устанавливаем Python-библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска (пока что запустим и будем ждать, чтобы контейнер не падал)
CMD ["python", "main.py"]
