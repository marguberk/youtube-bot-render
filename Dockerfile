FROM python:3.9-slim

# Установка ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY . .

# Создание директории для временных файлов
RUN mkdir -p tmp && \
    chmod 777 tmp

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск бота в режиме worker
ENTRYPOINT ["python", "bot.py"] 