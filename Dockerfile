# Используем slim-версию для уменьшения веса образа
FROM python:3.10-slim

# Устанавливаем системные зависимости, необходимые для компиляции llama-cpp
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем список зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки (компиляция llama-cpp может занять пару минут)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY app.py .

# Создаем папку для хранения моделей (ее мы примонтируем через compose)
RUN mkdir -p /app/models

# Открываем порт
EXPOSE 8000

# Запуск приложения через uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
