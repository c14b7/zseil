# 🚀 Instrukcja wdrożenia na GitHub Pages

## Krok 1: Wypchnij kod do GitHub

```bash
git add .
git commit -m "Dodanie obsługi GitHub Actions + GitHub Pages"
git push origin main
```

## Krok 2: Włącz GitHub Pages

1. Idź do repozytorium na GitHub: https://github.com/c14b7/zsei
2. Kliknij **Settings** (Ustawienia)
3. Przewiń w dół do sekcji **Pages**
4. W sekcji **Source** wybierz:
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
5. Kliknij **Save**

## Krok 3: Uruchom pierwszy scraping (opcjonalnie)

1. Idź do zakładki **Actions** w repozytorium
2. Kliknij na workflow **Update Schedule Data**
3. Kliknij **Run workflow** → **Run workflow**
4. Poczekaj aż się zakończy (około 2-5 minut)

## Krok 4: Sprawdź stronę

Po kilku minutach Twoja strona będzie dostępna pod adresem:
**https://c14b7.github.io/zsei/**

## ⚙️ Automatyczna aktualizacja

- GitHub Actions będzie automatycznie pobierać dane **codziennie o 8:00** (czasu polskiego)
- Możesz też uruchomić aktualizację ręcznie przez zakładkę **Actions**

## 🐛 Troubleshooting

### Strona nie działa?
1. Sprawdź czy GitHub Pages jest włączone w Settings
2. Sprawdź czy workflow Actions się wykonał pomyślnie
3. Sprawdź czy istnieją pliki w folderze `data/`

### Brak danych?
1. Uruchom workflow ręcznie przez Actions
2. Sprawdź logi w Actions czy nie ma błędów
3. Sprawdź czy strona ZSEIL jest dostępna

### Stare dane?
1. Workflow uruchamia się o 8:00 każdego dnia
2. Możesz wymusić aktualizację przez Actions → Run workflow

## 📊 Monitorowanie

- **Actions**: Historia wykonań i logi
- **Pages**: Status wdrożenia strony  
- **data/metadata.json**: Statystyki ostatniej aktualizacji

## 🔧 Konfiguracja

### Zmiana częstotliwości aktualizacji

Edytuj `.github/workflows/update-schedule.yml` linię:
```yaml
- cron: '0 6 * * *'  # 0 6 = 8:00 polskiego czasu (UTC+2)
```

### Wyłączenie automatycznych aktualizacji

Usuń lub zakomentuj sekcję `schedule:` w workflow.

## ✅ Gotowe!

Twoja aplikacja powinna teraz działać na GitHub Pages z automatyczną aktualizacją danych!