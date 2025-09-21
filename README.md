# Plan Lekcji ZSEIL

Aplikacja do przeglądania planu lekcji Zespołu Szkół Ekonomiczno-Informatycznych im. prof. Janusza Groszkowskiego w Łomży.

## 🚀 Demo

Aplikacja jest dostępna pod adresem: [https://c14b7.github.io/zsei/](https://c14b7.github.io/zsei/)

## 🔧 Jak to działa

Aplikacja używa GitHub Actions do automatycznego pobierania danych z oficjalnej strony ZSEIL i generowania statycznych plików JSON, które są następnie hostowane na GitHub Pages.

### Aktualizacja danych

- **Automatycznie**: Codziennie o 8:00 (czasu polskiego)
- **Ręcznie**: Przez zakładkę "Actions" w repozytorium GitHub

### Technologie

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Scraping**: Python + Playwright
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions

## 📁 Struktura plików

```
├── .github/workflows/
│   └── update-schedule.yml    # GitHub Actions workflow
├── data/                      # Dane JSON (generowane automatycznie)
│   ├── available_items.json   # Lista klas, nauczycieli, sal
│   ├── metadata.json          # Metadane ostatniej aktualizacji
│   └── schedule_*.json        # Plany lekcji
├── data_scraper.py            # Skrypt do pobierania danych
├── index.html                 # Strona główna
├── script.js                  # Logika aplikacji
├── style.css                  # Stylowanie
└── README.md                  # Ten plik
```

## 🛠️ Uruchamianie lokalnie

1. Sklonuj repozytorium:
```bash
git clone https://github.com/c14b7/zsei.git
cd zsei
```

2. Zainstaluj zależności:
```bash
pip install playwright requests beautifulsoup4
playwright install chromium
```

3. Pobierz dane:
```bash
python data_scraper.py
```

4. Uruchom lokalny serwer HTTP:
```bash
python -m http.server 8000
```

5. Otwórz [http://localhost:8000](http://localhost:8000) w przeglądarce

## 📝 Licencja

Projekt jest udostępniony na licencji MIT. Dane pochodzą z oficjalnej strony ZSEIL.

## ⚠️ Zastrzeżenia

- Aplikacja pobiera dane z publicznej strony ZSEIL
- Nie gwarantujemy 100% dokładności danych
- W przypadku problemów z oficjalną stroną, aplikacja może pokazywać stare dane

## 🤝 Współpraca

Zgłaszaj błędy i sugestie przez [Issues](https://github.com/c14b7/zsei/issues) w GitHub.