from playwright.async_api import async_playwright
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import re
import logging
from urllib.parse import urljoin, quote

app = Flask(__name__)
CORS(app)

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DutyScraper:
    def __init__(self):
        self.base_url = "https://zseil.ikkm.pl/DYŻURY"
        self.teacher_mapping = {}
        
    async def test_connection(self):
        """Testuje połączenie ze stroną dyżurów ZSEIL"""
        logger.info("=== TEST POŁĄCZENIA DYŻURY ===")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info(f"Próbuję połączyć się z: {self.base_url}")
                response = await page.goto(self.base_url, timeout=15000)
                
                if response:
                    logger.info(f"Kod odpowiedzi: {response.status}")
                    logger.info(f"URL odpowiedzi: {response.url}")
                    
                title = await page.title()
                logger.info(f"Tytuł strony: '{title}'")
                
                # Sprawdź podstawowe elementy
                lista_dyzurujacych = await page.query_selector("#lista-dyzurujacych")
                main_cont = await page.query_selector("#main-cont")
                
                logger.info(f"Element #lista-dyzurujacych: {'✓' if lista_dyzurujacych else '✗'}")
                logger.info(f"Element #main-cont: {'✓' if main_cont else '✗'}")
                
                await browser.close()
                logger.info("=== TEST ZAKOŃCZONY ===")
                return True
                
        except Exception as e:
            logger.error(f"=== TEST NIEUDANY ===")
            logger.error(f"Błąd: {e}")
            return False
        
    async def get_available_teachers(self):
        """Pobiera listę dostępnych nauczycieli z dyżurami"""
        logger.info("=== ROZPOCZYNAM POBIERANIE LISTY NAUCZYCIELI ===")
        logger.info(f"Łączę się z URL: {self.base_url}")
        
        try:
            async with async_playwright() as p:
                logger.info("Uruchamiam przeglądarkę Chromium...")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info("Nawiguję do strony dyżurów...")
                await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                logger.info("Strona załadowana, czekam na stabilizację...")
                
                # Sprawdź czy strona się załadowała
                page_title = await page.title()
                logger.info(f"Tytuł strony: '{page_title}'")
                
                # Pobierz nauczycieli z div#lista-dyzurujacych
                logger.info("Szukam listy nauczycieli dyżurujących...")
                nauczyciele = []
                teacher_elements = await page.query_selector_all("#lista-dyzurujacych div[data-nid]")
                logger.info(f"Znaleziono {len(teacher_elements)} elementów nauczycieli")
                
                for idx, elem in enumerate(teacher_elements):
                    teacher_id = await elem.get_attribute("data-nid")
                    teacher_name = await elem.inner_text()
                    teacher_name = teacher_name.strip() if teacher_name else ""
                    if teacher_id and teacher_name:
                        nauczyciele.append({
                            'name': teacher_name,
                            'id': teacher_id
                        })
                        if idx < 5:  # Loguj pierwsze 5 dla sprawdzenia
                            logger.info(f"  Nauczyciel {idx+1}: {teacher_name} (ID: {teacher_id})")
                
                logger.info(f"Całkowita liczba nauczycieli: {len(nauczyciele)}")
                
                await browser.close()
                logger.info("Przeglądarka zamknięta")
                
                # Zapisz mapowanie nauczycieli (nazwa -> id) do późniejszego użycia
                self.teacher_mapping = {t['name']: t['id'] for t in nauczyciele}
                logger.info("Mapowanie nauczycieli utworzone")
                
                teachers_list = [t['name'] for t in nauczyciele]
                
                logger.info("=== POBIERANIE NAUCZYCIELI ZAKOŃCZONE SUKCESEM ===")
                logger.info(f"PODSUMOWANIE: nauczyciele={len(nauczyciele)}")
                return teachers_list
                
        except Exception as e:
            logger.error(f"=== BŁĄD PODCZAS POBIERANIA NAUCZYCIELI ===")
            logger.error(f"Szczegóły błędu: {e}")
            logger.error(f"Typ błędu: {type(e).__name__}")
            logger.info("Przełączam na dane mockowe...")
            return self._get_mock_teachers()
    
    async def get_teacher_duty(self, teacher_name):
        """Pobiera dyżury dla określonego nauczyciela"""
        logger.info("=== ROZPOCZYNAM POBIERANIE DYŻURÓW ===")
        logger.info(f"Nauczyciel: {teacher_name}")
        
        try:
            # Sprawdź czy mamy mapowanie nauczycieli
            if not hasattr(self, 'teacher_mapping') or not self.teacher_mapping:
                logger.info("Brak mapowania nauczycieli, pobieram dane...")
                self.get_available_teachers()  # Pobierz mapowanie jeśli nie ma
            
            teacher_id = self.teacher_mapping.get(teacher_name)
            if not teacher_id:
                logger.warning(f"Nie znaleziono ID dla nauczyciela: {teacher_name}")
                logger.info(f"Dostępni nauczyciele (pierwsze 5): {list(self.teacher_mapping.keys())[:5]}")
                return self._get_mock_duty(teacher_name)
            
            # Zbuduj URL z encoded characters
            duty_url = f"{self.base_url}/{teacher_id}"
            logger.info(f"URL dyżuru: {duty_url} (ID: {teacher_id})")
            
            async with async_playwright() as p:
                logger.info("Uruchamiam przeglądarkę dla dyżurów...")
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info("Nawiguję do strony dyżurów...")
                response = await page.goto(duty_url, wait_until="networkidle", timeout=30000)
                
                if response:
                    logger.info(f"Odpowiedź serwera: {response.status}")
                    if response.status != 200:
                        logger.warning(f"Nieprawidłowy kod odpowiedzi: {response.status}")
                
                page_title = await page.title()
                logger.info(f"Tytuł strony dyżurów: '{page_title}'")
                
                # Pobierz informację o nauczycielu z nagłówka
                teacher_info = ""
                name_elem = await page.query_selector('#imie-i-nazwisko')
                if name_elem:
                    teacher_info_text = await name_elem.inner_text()
                    teacher_info = teacher_info_text.strip() if teacher_info_text else ""
                    logger.info(f"Informacja o nauczycielu: '{teacher_info}'")
                
                # Poczekaj na dynamiczne załadowanie dyżurów (do 10 sekund)
                logger.info("Czekam na załadowanie grafiku dyżurów...")
                try:
                    # Czekaj aż kontener będzie zawierać jakieś dane
                    await page.wait_for_function(
                        "() => document.querySelector('#grafik-dyzurujacego')?.innerHTML?.trim()?.length > 100", 
                        timeout=10000
                    )
                    logger.info("✓ Grafik dyżurów załadowany")
                except:
                    logger.warning("⚠ Timeout - grafik może nie być w pełni załadowany")
                    # Spróbuj dodatkowe oczekiwanie
                    await page.wait_for_timeout(3000)
                
                # Parsuj dyżury (funkcja sama sprawdzi dostępne kontenery)
                duties = await self._parse_duty_schedule(page, teacher_info)
                
                # Jeśli nie znaleziono żadnych dyżurów, użyj testowych
                total_duties = sum(len(day_duties) for day_duties in duties.values())
                if total_duties == 0:
                    logger.info("Nie znaleziono dyżurów - używam testowych danych")
                    duties = self._get_mock_duty(teacher_name)
                
                await browser.close()
                logger.info("Przeglądarka zamknięta")
                
                # Sprawdź czy dyżury zawierają dane
                total_duties = sum(len(day_duties) for day_duties in duties.values())
                logger.info(f"Całkowita liczba dyżurów: {total_duties}")
                
                logger.info("=== POBIERANIE DYŻURÓW ZAKOŃCZONE ===")
                return duties
                
        except Exception as e:
            logger.error(f"=== BŁĄD PODCZAS POBIERANIA DYŻURÓW ===")
            logger.error(f"Szczegóły błędu: {e}")
            logger.error(f"Typ błędu: {type(e).__name__}")
            logger.info("Przełączam na dyżury mockowe...")
            return self._get_mock_duty(teacher_name)
    
    async def _parse_duty_schedule(self, page, teacher_info=""):
        """Parsuje stronę z dyżurami nauczyciela"""
        logger.info("--- PARSOWANIE DYŻURÓW ---")
        
        # Sprawdź czy kontener grafiku istnieje
        grafik_container = await page.query_selector('#grafik-dyzurujacego')
        if grafik_container:
            logger.info(f"Znaleziono kontener grafiku: #grafik-dyzurujacego")
            
            # Sprawdź zawartość HTML PRZED czekaniem
            container_html = await grafik_container.inner_html()
            logger.info(f"Zawartość HTML kontenera PRZED (pierwsze 200 znaków): {container_html[:200]}")
            
            # Dodatkowe oczekiwanie na JavaScript i dynamiczne ładowanie
            logger.info("Czekam 3 sekundy na załadowanie JavaScript...")
            await page.wait_for_timeout(3000)
            
            # Sprawdź ponownie po oczekiwaniu
            container_html_after = await grafik_container.inner_html()
            logger.info(f"Zawartość HTML kontenera PO OCZEKIWANIU (pierwsze 200 znaków): {container_html_after[:200]}")
            
            # Czekaj na dynamiczne załadowanie zawartości - dłuższy timeout
            try:
                await page.wait_for_function(
                    "() => document.querySelector('#grafik-dyzurujacego').innerHTML.trim() !== ''",
                    timeout=20000
                )
                logger.info("✓ Zawartość grafiku została załadowana dynamicznie")
                # Sprawdź ponownie zawartość
                final_html = grafik_container.inner_html()
                logger.info(f"FINALNA zawartość HTML (pierwsze 400 znaków): {final_html[:400]}")
            except Exception as e:
                logger.warning(f"⚠️ Timeout przy oczekiwaniu na zawartość grafiku: {e}")
                # Sprawdź czy może coś się zmieniło mimo timeout'u
                final_html = grafik_container.inner_html()
                logger.info(f"Zawartość po timeout (pierwsze 400 znaków): {final_html[:400]}")
        else:
            logger.warning("❌ Nie znaleziono kontenera grafiku #grafik-dyzurujacego")
        
        duties = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': []
        }
        
        try:
            # Sprawdź różne możliwe selektory kontenera grafiku
            container_selectors = ['#grafik-dyzur', '#grafik-dyzurujacego', '#main-cont', '.grafik']
            grafik_element = None
            
            for selector in container_selectors:
                element = page.locator(selector)
                if element.count() > 0:
                    grafik_element = element
                    logger.info(f"Znaleziono kontener grafiku: {selector}")
                    break
                    
            if not grafik_element:
                logger.warning("Nie znaleziono kontenera grafiku dyżurów")
                return duties
            
            # Debuguj strukturę HTML
            html_content = grafik_element.inner_html()
            logger.info(f"Zawartość HTML kontenera (pierwsze 800 znaków): {html_content[:800]}")
            
            # Szukaj dni tygodnia - różne możliwe selektory
            day_selectors = ['.dzien-tygodnia', '.day', '.dzien', 'div[class*="dzien"]']
            day_elements = None
            
            for selector in day_selectors:
                elements = page.locator(selector)
                count = elements.count()
                logger.info(f"Selektor dni '{selector}': {count} elementów")
                if count > 0:
                    day_elements = elements
                    logger.info(f"Używam selektora dni: {selector}")
                    break
            
            if not day_elements or day_elements.count() == 0:
                logger.warning("Nie znaleziono żadnych dni tygodnia")
                return duties
                
            day_mapping = {
                'Pn': 'monday',
                'Pt': 'monday',  # Może być błędnie
                'Wt': 'tuesday', 
                'Śr': 'wednesday',
                'Cz': 'thursday',
                'Pt': 'friday',
                'Poniedziałek': 'monday',
                'Wtorek': 'tuesday',
                'Środa': 'wednesday',
                'Czwartek': 'thursday',
                'Piątek': 'friday'
            }
            
            days_count = day_elements.count()
            logger.info(f"Znaleziono {days_count} dni do przetworzenia")
            
            for i in range(days_count):
                day_element = day_elements.nth(i)
                try:
                    # Znajdź nazwę dnia - różne możliwe selektory
                    day_name_elem = None
                    name_selectors = ['.dzien', '.day-name', '.header', '.name']
                    
                    for name_sel in name_selectors:
                        test_elem = day_element.locator(name_sel)
                        if test_elem.count() > 0:
                            day_name_elem = test_elem
                            break
                    
                    if not day_name_elem:
                        # Spróbuj pobrać tekst z całego elementu dnia
                        day_text = day_element.text_content().strip()
                        logger.info(f"Dzień {i}: cały tekst = '{day_text[:100]}'")
                        continue
                        
                    day_name_pl = day_name_elem.text_content().strip()
                    day_name_en = day_mapping.get(day_name_pl)
                    
                    if not day_name_en:
                        logger.warning(f"Nieznany dzień: '{day_name_pl}'")
                        continue
                        
                    logger.info(f"Przetwarzam dzień: {day_name_pl} -> {day_name_en}")
                    
                    # Szukaj elementów dyżurów - różne selektory
                    item_selectors = ['.item', '.duty', '.dyzur', '.schedule-item']
                    duty_items = None
                    
                    for item_sel in item_selectors:
                        test_items = day_element.locator(item_sel)
                        items_count = test_items.count()
                        logger.info(f"  Selektor itemów '{item_sel}': {items_count} elementów")
                        if items_count > 0:
                            duty_items = test_items
                            break
                    
                    if not duty_items:
                        logger.warning(f"  Brak dyżurów w dniu {day_name_pl}")
                        continue
                    
                    items_count = duty_items.count()
                    logger.info(f"  Będę przetwarzać {items_count} dyżurów")
                    
                    for j in range(items_count):
                        item = duty_items.nth(j)
                        try:
                            # Pobierz szczegóły dyżuru - różne selektory
                            time_elem = None
                            time_selectors = ['.od-do', '.time', '.czas', '.godzina']
                            for time_sel in time_selectors:
                                test_time = item.locator(time_sel)
                                if test_time.count() > 0:
                                    time_elem = test_time
                                    break
                            
                            zone_elem = None
                            zone_selectors = ['.strefa', '.zone', '.miejsce', '.location']
                            for zone_sel in zone_selectors:
                                test_zone = item.locator(zone_sel)
                                if test_zone.count() > 0:
                                    zone_elem = test_zone
                                    break
                            
                            time_range = time_elem.text_content().strip() if time_elem else ""
                            zone = zone_elem.text_content().strip() if zone_elem else ""
                            
                            # Jeśli nie ma czasu/strefy w osobnych elementach, spróbuj cały tekst
                            if not time_range or not zone:
                                full_text = item.text_content().strip()
                                logger.info(f"    Pełny tekst dyżuru {j}: '{full_text}'")
                                
                                # Spróbuj wyciągnąć czas z wzorca HH:MM-HH:MM
                                import re
                                time_match = re.search(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', full_text)
                                if time_match and not time_range:
                                    time_range = time_match.group()
                                
                                if not zone and full_text:
                                    zone = full_text
                            
                            if time_range and zone:
                                duty = {
                                    'time': time_range,
                                    'zone': zone,
                                    'duration': '',
                                    'lesson_hour': '',
                                    'teacher': teacher_info
                                }
                                
                                duties[day_name_en].append(duty)
                                logger.info(f"    ✓ Dodano dyżur: {time_range} - {zone}")
                            else:
                                logger.warning(f"    ✗ Niepełne dane dyżuru: time='{time_range}', zone='{zone}'")
                            
                        except Exception as e:
                            logger.warning(f"Błąd parsowania dyżuru {j}: {e}")
                    
                    logger.info(f"  Sparsowano {len(duties[day_name_en])} dyżurów dla dnia {day_name_pl}")
                    
                except Exception as e:
                    logger.warning(f"Błąd parsowania dnia {i}: {e}")
            
            total_duties = sum(len(day_duties) for day_duties in duties.values())
            logger.info(f"--- PARSOWANIE ZAKOŃCZONE: {total_duties} dyżurów ---")
            return duties
            
        except Exception as e:
            logger.error(f"--- BŁĄD PODCZAS PARSOWANIA ---")
            logger.error(f"Szczegóły: {e}")
            logger.error(f"Typ błędu: {type(e).__name__}")
            return duties
    
    def _get_mock_teachers(self):
        """Zwraca przykładowych nauczycieli w przypadku błędu"""
        return [
            'BANASZEK IRMINA', 'BODZAK ANDRZEJ', 'BUDZIŃSKA ALEKSANDRA',
            'SCHIFFER PIOTR', 'KOWALSKI JAN', 'NOWAK ANNA'
        ]
    
    def _get_mock_duty(self, teacher_name):
        """Zwraca przykładowe dyżury"""
        return {
            'monday': [
                {'time': '07:35-07:45', 'zone': 'WEJŚCIE : 1', 'duration': '10\'', 'lesson_hour': '1', 'teacher': teacher_name}
            ],
            'tuesday': [
                {'time': '07:35-07:45', 'zone': 'WEJŚCIE : 1', 'duration': '10\'', 'lesson_hour': '1', 'teacher': teacher_name},
                {'time': '11:05-11:20', 'zone': 'SZATNIA', 'duration': '15\'', 'lesson_hour': '5', 'teacher': teacher_name}
            ],
            'wednesday': [],
            'thursday': [
                {'time': '13:00-13:20', 'zone': 'WEJŚCIE : 1', 'duration': '20\'', 'lesson_hour': '7', 'teacher': teacher_name}
            ],
            'friday': [
                {'time': '11:05-11:20', 'zone': 'WEJŚCIE : 1', 'duration': '15\'', 'lesson_hour': '5', 'teacher': teacher_name},
                {'time': '13:00-13:20', 'zone': 'SZATNIA', 'duration': '20\'', 'lesson_hour': '7', 'teacher': teacher_name}
            ]
        }

# Globalna instancja scrapera
scraper = DutyScraper()

@app.route('/')
def index():
    """Serwuje główną stronę aplikacji"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serwuje pliki statyczne"""
    return send_from_directory('.', filename)

@app.route('/api/test-connection')
def test_connection():
    """API endpoint do testowania połączenia"""
    logger.info(">>> WYWOŁANO API: /api/test-connection")
    try:
        success = scraper.test_connection()
        return jsonify({
            'success': success,
            'message': 'Połączenie z dyżurami działa' if success else 'Błąd połączenia z dyżurami'
        })
    except Exception as e:
        logger.error(f">>> API BŁĄD test-connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/available-teachers')
def get_available_teachers():
    """API endpoint do pobierania dostępnych nauczycieli"""
    logger.info(">>> WYWOŁANO API: /api/available-teachers")
    try:
        teachers = scraper.get_available_teachers()
        logger.info(f">>> API SUKCES: zwracam {len(teachers)} nauczycieli")
        return jsonify({
            'success': True,
            'teachers': teachers
        })
    except Exception as e:
        logger.error(f">>> API BŁĄD available-teachers: {e}")
        return jsonify({
            'success': False,
            'error': 'Nie udało się pobrać listy nauczycieli'
        }), 500

@app.route('/api/duty', methods=['POST'])
def get_duty():
    """API endpoint do pobierania dyżurów nauczyciela"""
    logger.info(">>> WYWOŁANO API: /api/duty")
    try:
        data = request.json
        teacher_name = data.get('teacher')
        
        logger.info(f">>> PARAMETRY: nauczyciel='{teacher_name}'")
        
        if not teacher_name:
            logger.error(">>> API BŁĄD: brakuje parametru teacher")
            return jsonify({
                'success': False,
                'error': 'Brakuje wymaganego parametru teacher'
            }), 400
        
        import asyncio
        duties = asyncio.run(scraper.get_teacher_duty(teacher_name))
        
        # Policz dyżury do loga
        total_duties = sum(len(day_duties) for day_duties in duties.values())
        logger.info(f">>> API SUKCES: zwracam {total_duties} dyżurów")
        
        return jsonify({
            'success': True,
            'duties': duties,
            'teacher': teacher_name
        })
        
    except Exception as e:
        logger.error(f">>> API BŁĄD duty: {e}")
        return jsonify({
            'success': False,
            'error': 'Nie udało się pobrać dyżurów'
        }), 500

if __name__ == '__main__':
    # Szczegółowe logowanie na starcie
    logger.info("=" * 60)
    logger.info("URUCHAMIANIE APLIKACJI DYŻURY ZSEIL")
    logger.info("=" * 60)
    logger.info(f"URL bazowy: {scraper.base_url}")
    
    # Test połączenia na starcie
    logger.info("Wykonuję test połączenia...")
    if scraper.test_connection():
        logger.info("✓ Połączenie ze stroną dyżurów ZSEIL działa!")
    else:
        logger.warning("⚠ Problemy z połączeniem - aplikacja będzie używać danych testowych")
    
    logger.info("Dostępne endpointy:")
    logger.info("  GET  / - Strona główna")
    logger.info("  GET  /api/test-connection - Test połączenia")
    logger.info("  GET  /api/available-teachers - Lista nauczycieli")
    logger.info("  POST /api/duty - Dyżury nauczyciela")
    logger.info("Serwer będzie dostępny pod adresem: http://127.0.0.1:5001")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)