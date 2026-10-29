FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tts_server.py .
ENV PORT=8766
EXPOSE 8766
CMD ["python", "tts_server.py"]
