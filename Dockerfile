# Usar Python 3.11 oficial slim
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
COPY main.py .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Variables de entorno (preferible configurar en Render / Docker Compose, aquí solo ejemplo)
# ENV TELEGRAM_BOT_TOKEN=tu_token
# ENV OPENAI_API_KEY=tu_api_key

# Comando para correr la app
CMD ["python", "main.py"]
