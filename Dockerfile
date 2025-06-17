# ETAP 1: Budowanie frontendu Vue.js
FROM node:18-alpine AS builder

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików package.json i instalacja zależności (wykorzystuje cache Dockera)
COPY package.json package-lock.json ./
RUN npm install

# Kopiowanie reszty kodu źródłowego frontendu
# Ważne: vite.config.js definiuje katalog wyjściowy jako '../dist'
COPY . .

# Budowanie aplikacji. Pliki wynikowe znajdą się w katalogu /dist
RUN npm run build

# ETAP 2: Tworzenie finalnego obrazu produkcyjnego
FROM python:3.10-slim

# Instalacja Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie i instalacja zależności Pythona
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu backendu
COPY backend_main.py .

# Kopiowanie zbudowanego frontendu z etapu 1 do katalogu /app/dist
COPY --from=builder /dist ./dist

# Kopiowanie konfiguracji Nginx oraz skryptu startowego
COPY nginx.conf /etc/nginx/sites-enabled/default
COPY start.sh .
# Nadanie uprawnień do wykonania skryptu startowego
RUN chmod +x start.sh

# Wystawienie portu, na którym nasłuchuje Nginx
EXPOSE 80

# Uruchomienie skryptu startowego, który włączy Nginx i Uvicorn
CMD ["./start.sh"]