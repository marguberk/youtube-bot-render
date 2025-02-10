FROM python:3.9-slim

# Установка ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .
COPY bot.py .

# Создание директории для временных файлов
RUN mkdir tmp

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск бота
CMD ["python", "bot.py"] 