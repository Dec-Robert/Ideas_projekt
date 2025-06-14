# Ideas_projekt
Moduł odpowiada za generowanie raportu DOCX na podstawie analizowanych próbek.  
Endpointy  
POST /generate-report

    Opis: Generuje plik .docx z wybranymi próbkami.

    Body (JSON):

{
  "sample_ids": ["<id_1>", "<id_2>", "..."]
}

Działanie:

    Pobiera dane z Archiwum API (/samples/batch)

    Wczytuje plik szablonu template.docx (w katalogu modułu)

    Wypełnia tabelę w szablonie danymi:

        numer próbki

        data dodania

        data predykcji

        status

        algorytm

        confidence

        obraz po predykcji (base64 jako tekst)

    Zwraca wygenerowany plik .docx do pobrania

raport_api.py – główny plik aplikacji

requirements.txt – zależności Pythona

szablon.docx – szablon z gotową tabelą do uzupełnienia
