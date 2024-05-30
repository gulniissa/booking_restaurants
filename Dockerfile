# Dockerfile

# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости для GDAL и PostGIS
RUN apt-get update && apt-get install -y \
    binutils \
    gdal-bin \
    libproj-dev \
    postgresql-client

# Устанавливаем рабочую директорию
WORKDIR /app/

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

