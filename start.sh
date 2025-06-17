#!/bin/sh

# Uruchom serwer Uvicorn w tle. Będzie on dostępny tylko wewnątrz kontenera.
uvicorn backend_main:app --host 127.0.0.1 --port 8000 &

# Uruchom Nginx na pierwszym planie. Przejmie on główny proces kontenera.
nginx -g 'daemon off;'