# Ideas_projekt
🐳 Konteneryzacja

Cały system składa się z dwóch kontenerów:

    mongo – oficjalny kontener MongoDB (v6)

    archiwum-api – kontener z aplikacją FastAPI

Pliki konteneryzacyjne:

    Dockerfile – definiuje obraz z FastAPI i wymaganiami (requirements.txt)

    docker-compose.yml – uruchamia usługę bazy oraz API i definiuje ich połączenie

⚙️ Konfiguracja

Zmienne środowiskowe:

    MONGODB_URI: domyślnie ustawione w docker-compose na mongodb://mongo:27017/samplesdb (wymagane połączenie z MongoDB)

🔌 Endpointy API  
POST /samples

Tworzy nową próbkę w archiwum.
Body (JSON):

{
  "sample_number": "12345678",
  "cropped_image": "base64string"
}

Odpowiedź:

{
  "message": "Sample created",
  "sample_number": "12345678"
}
  
PUT /samples/{sample_number}

Aktualizuje rekord próbki po predykcji.
Body (JSON):

{
  "algorithm": "gradcam",
  "status": "positive",
  "evaluated_image": "base64string",
  "confidence": 0.92
}

GET /samples

Zwraca listę wszystkich próbek.
Przykład odpowiedzi:

[
  {
    "sample_number": "12345678",
    "date_added": "2025-05-30T18:00:00",
    "cropped_image": "base64string",
    "status": "positive",
    "algorithm": "gradcam",
    "evaluated_image": "base64string",
    "confidence": 0.92,
    "date_predicted": "2025-05-30T18:05:00"
  }
]

GET /samples/{sample_number}

Zwraca pojedynczy rekord próbki.
