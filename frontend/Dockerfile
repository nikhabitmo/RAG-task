# Базовый образ для Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта фронтенда
COPY . .

# Открываем порт, на котором работает Streamlit
EXPOSE 8501

# Команда для запуска Streamlit приложения
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
