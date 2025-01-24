FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

RUN pip install --upgrade pip
# Копируем файл зависимостей
COPY app/requirements.txt /app/

RUN pip install requests
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Копируем остальные файлы приложения
COPY app /app/

# Открываем порт
EXPOSE 5005

# Указываем команду для запуска приложения
CMD ["python", "/app/app.py"]
