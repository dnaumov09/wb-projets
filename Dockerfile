# Use an official Python runtime as a base image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including build tools and locales
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    locales && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ru_RU.UTF-8

# Set environment variables for locale and timezone
ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru_RU:ru
ENV TZ=Europe/Moscow

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Django project code into the container
COPY . .

# Run Django migrations and start the development server
CMD ["sh", "-c", "python ./app/run.py"]