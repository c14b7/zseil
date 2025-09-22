# GitHub Pages Deployment

## Szybkie uruchomienie na GitHub Pages:

1. **Skopiuj pliki do głównego folderu repo:**
```bash
cp jsoff/index.html ./
cp jsoff/script.js ./
cp jsoff/style.css ./
cp jsoff/data.json ./
```

2. **Commit i push:**
```bash
git add .
git commit -m "Add static schedule app"
git push
```

3. **Włącz GitHub Pages:**
   - Idź do Settings > Pages
   - Source: Deploy from a branch
   - Branch: main / root
   - Save

4. **Strona będzie dostępna pod:**
   `https://c14b7.github.io/zseil`

## Alternatywnie - subfolder:

Jeśli chcesz zachować strukturę folderów:

1. **GitHub Pages Settings:**
   - Source: Deploy from a branch  
   - Branch: main / docs

2. **Przenieś pliki do folderu docs:**
```bash
mkdir docs
cp jsoff/index.html docs/
cp jsoff/script.js docs/
cp jsoff/style.css docs/
cp jsoff/data.json docs/
```

Strona będzie pod: `https://c14b7.github.io/zseil`