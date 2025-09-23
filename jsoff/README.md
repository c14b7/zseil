# Plan Lekcji ZSEIL

Aplikacja do pobierania planów lekcji ze strony ZSEIL i generowania danych JSON.

## Instalacja

1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Zainstaluj Playwright browsers:
```bash
playwright install
```

## Konfiguracja

Aplikacja używa pliku `.env` do konfiguracji. Przykładowy plik `.env`:

```env
# URL strony z planami lekcji
BASE_URL=http://url.data.pl/data

# Ustawienia scrapowania
HEADLESS_MODE=true
SCRAPING_DELAY=1
TIMEOUT=15000

# Plik wyjściowy
OUTPUT_FILE=data.json

# Ustawienia logowania
LOG_LEVEL=INFO

# Opcjonalne ustawienia przeglądarki
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

## Dostępne zmienne środowiskowe

- `BASE_URL` - URL strony z planami
- `HEADLESS_MODE` - czy uruchamiać przeglądarkę w trybie headless (true/false)
- `SCRAPING_DELAY` - opóźnienie między requestami w sekundach (domyślnie: 1)
- `TIMEOUT` - timeout dla requestów w milisekundach (domyślnie: 15000)
- `OUTPUT_FILE` - nazwa pliku wyjściowego (domyślnie: data.json)
- `LOG_LEVEL` - poziom logowania (DEBUG, INFO, WARNING, ERROR)
- `USER_AGENT` - User-Agent dla przeglądarki

## Użycie

```bash
python app.py
```

Aplikacja pobierze wszystkie dostępne plany lekcji i zapisze je do pliku JSON określonego w zmiennej `OUTPUT_FILE`.

## Bez biblioteki dotenv

Jeśli nie masz zainstalowanej biblioteki `python-dotenv`, aplikacja automatycznie użyje prostszej metody ładowania pliku `.env`. W takim przypadku usuń tę linię z `requirements.txt`:
```
python-dotenv>=1.0.0
```

## Struktura wyjściowa

Plik JSON zawiera:
- `metadata` - informacje o scrapowaniu
- `available_items` - listy dostępnych klas, nauczycieli i sal
- `schedules` - plany lekcji pogrupowane według typu (klasa/nauczyciel/sala)