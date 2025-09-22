# Plan Lekcji ZSEIL - Hosting Statyczny

System planu lekcji działający wyłącznie w przeglądarce (JavaScript) z danymi w pliku JSON.

## 🚀 Deployment na hosting statyczny

### Pliki potrzebne do hostingu:
```
📁 jsoff/
├── index.html      # Główna strona
├── script.js       # Logika aplikacji
├── style.css       # Style CSS
└── data.json       # Dane planów (1.6MB)
```

### ⚠️ Ważne: Plik `app.py` NIE jest potrzebny na hostingu!

## 📋 Instrukcja deployment:

### 1. GitHub Pages
1. Skopiuj pliki: `index.html`, `script.js`, `style.css`, `data.json` do głównego folderu repo
2. Włącz GitHub Pages w ustawieniach repo
3. Strona będzie dostępna pod: `https://username.github.io/repo-name`

### 2. Netlify
1. Przeciągnij folder `jsoff` na netlify.com/drop
2. Lub podłącz repo GitHub i ustaw folder publikacji na `jsoff`

### 3. Vercel
1. `npx vercel --cwd jsoff` 
2. Lub podłącz repo GitHub

### 4. Surge.sh
```bash
cd jsoff
npm install -g surge
surge
```

### 5. Firebase Hosting
```bash
cd jsoff
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

## 🔄 Aktualizacja danych

1. Uruchom lokalnie: `python app.py` (w folderze jsoff)
2. Zostanie wygenerowany nowy `data.json`
3. Prześlij nowy `data.json` na hosting

## ✨ Funkcjonalności

- ✅ Działa bez serwera backend
- ✅ Wszystkie dane w JSON (1.6MB)
- ✅ Responsywny design
- ✅ Filtrowanie: klasy, nauczyciele, sale
- ✅ Plan lekcji z godzinami
- ✅ Metadane: ostatnia aktualizacja, statystyki
- ✅ Obsługa błędów i fallback data

## 📊 Statystyki danych

- **Klasy**: ~40
- **Nauczyciele**: ~60 
- **Sale**: ~67
- **Plany**: 195 (wszystkie kombinacje)
- **Rozmiar danych**: 1.6MB

## 🛠️ Technologie

- **Frontend**: Vanilla JavaScript, CSS3, HTML5
- **Data source**: JSON file (statyczne dane)
- **Scraping**: Python + Playwright (tylko do generowania danych)

---

**Gotowe do użycia!** Skopiuj 4 pliki na dowolny hosting statyczny.