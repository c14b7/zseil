from playwright.sync_api import sync_playwright

url = "https://zseil.ikkm.pl/DY%c5%bbURY/SP"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")   # czeka aż sieć ucichnie
    # możesz też czekać na konkretny selektor:
    # page.wait_for_selector("div.some-class", timeout=10000)

    html = page.content()   # pełny, wyrenderowany HTML
    print(html)

    # przykład: pobranie tekstu ze wszystkich divów o danej klasie
    elems = page.query_selector_all("div.some-class")
    for e in elems:
        print(e.inner_text())

    browser.close()
