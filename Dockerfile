# Użyj oficjalnego, lekkiego obrazu Python jako bazę
FROM python:3.10-slim

# Instalacja zależności systemowych wymaganych przez OpenCV i pyzbar
# libzbar0 - dla dekodowania kodów kreskowych
# libgl1-mesa-glx, libglib2.0-0 - dla OpenCV
RUN apt-get update && apt-get install -y libzbar0 libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Kopiowanie pliku z zależnościami Pythona
COPY requirements.txt .

# Instalacja zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu aplikacji do kontenera
COPY main.py .

# Wystawienie portu, na którym nasłuchuje aplikacja
EXPOSE 8000

# Polecenie uruchamiające aplikację przy starcie kontenera
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]