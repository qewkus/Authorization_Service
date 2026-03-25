FROM python:3.12-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/list/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements

# Копируем проект
COPY . .

# Открытие порта
EXPOSE 8000

# Создаем директорию для файлов со статикой
RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles

# Команда для запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]