# Używamy lekkiego obrazu z Pythonem
FROM python:3.10-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki projektu
COPY . /app

# Zainstaluj wymagane biblioteki
RUN pip install --no-cache-dir -r requirements.txt

# Otwórz port aplikacji
EXPOSE 8000

# Uruchom serwer produkcyjny
CMD ["uvicorn", "archiwum_api:app", "--host", "0.0.0.0", "--port", "8000"]
