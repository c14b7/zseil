from playwright.sync_api import sync_playwright
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import re
import logging
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduleScraper:
    def __init__(self):
        self.base_url = "http://zseil.ikkm.pl/PLAN"
        self.teacher_mapping = {}
        
    def test_connection(self):
        """Testuje połączenie ze stroną ZSEIL"""
        logger.info("=== TEST POŁĄCZENIA ===")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info(f"Próbuję połączyć się z: {self.base_url}")
                response = page.goto(self.base_url, timeout=15000)
                
                if response:
                    logger.info(f"Kod odpowiedzi: {response.status}")
                    logger.info(f"URL odpowiedzi: {response.url}")
                    
                title = page.title()
                logger.info(f"Tytuł strony: '{title}'")
                
                # Sprawdź podstawowe elementy
                lista_n = page.query_selector("#lista-n")
                lista_s = page.query_selector("#lista-s") 
                lista_k = page.query_selector("#lista-k")
                
                logger.info(f"Element #lista-n: {'✓' if lista_n else '✗'}")
                logger.info(f"Element #lista-s: {'✓' if lista_s else '✗'}")
                logger.info(f"Element #lista-k: {'✓' if lista_k else '✗'}")
                
                browser.close()
                logger.info("=== TEST ZAKOŃCZONY ===")
                return True
                
        except Exception as e:
            logger.error(f"=== TEST NIEUDANY ===")
            logger.error(f"Błąd: {e}")
            return False
        
    def get_available_items(self):
        """Pobiera listę dostępnych klas, nauczycieli i sal"""
        logger.info("=== ROZPOCZYNAM POBIERANIE DOSTĘPNYCH ELEMENTÓW ===")
        logger.info(f"Łączę się z URL: {self.base_url}")
        
        try:
            with sync_playwright() as p:
                logger.info("Uruchamiam przeglądarkę Chromium...")
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info("Nawiguję do strony głównej...")
                page.goto(self.base_url, wait_until="networkidle")
                logger.info("Strona załadowana, czekam na stabilizację...")
                
                # Sprawdź czy strona się załadowała
                page_title = page.title()
                logger.info(f"Tytuł strony: '{page_title}'")
                
                # Pobierz nauczycieli z div#lista-n
                logger.info("Szukam listy nauczycieli (#lista-n)...")
                nauczyciele = []
                teacher_elements = page.query_selector_all("#lista-n p[data-id]")
                logger.info(f"Znaleziono {len(teacher_elements)} elementów nauczycieli")
                
                for idx, elem in enumerate(teacher_elements):
                    teacher_id = elem.get_attribute("data-id")
                    teacher_name = elem.inner_text().strip()
                    if teacher_id and teacher_name:
                        nauczyciele.append({
                            'name': teacher_name,
                            'id': teacher_id
                        })
                        if idx < 5:  # Loguj pierwsze 5 dla sprawdzenia
                            logger.info(f"  Nauczyciel {idx+1}: {teacher_name} (ID: {teacher_id})")
                
                logger.info(f"Całkowita liczba nauczycieli: {len(nauczyciele)}")
                
                # Pobierz sale z div#lista-s
                logger.info("Szukam listy sal (#lista-s)...")
                sale = []
                room_elements = page.query_selector_all("#lista-s p")
                logger.info(f"Znaleziono {len(room_elements)} elementów sal")
                
                for idx, elem in enumerate(room_elements):
                    room_name = elem.inner_text().strip()
                    if room_name:
                        sale.append(room_name)
                        if idx < 10:  # Loguj pierwsze 10 dla sprawdzenia
                            logger.info(f"  Sala {idx+1}: {room_name}")
                
                logger.info(f"Całkowita liczba sal: {len(sale)}")
                
                # Pobierz klasy z div#lista-k
                logger.info("Szukam listy klas (#lista-k)...")
                klasy = []
                class_elements = page.query_selector_all("#lista-k p")
                logger.info(f"Znaleziono {len(class_elements)} elementów klas")
                
                for idx, elem in enumerate(class_elements):
                    class_name = elem.inner_text().strip()
                    if class_name:
                        klasy.append(class_name)
                        if idx < 10:  # Loguj pierwsze 10 dla sprawdzenia
                            logger.info(f"  Klasa {idx+1}: {class_name}")
                
                logger.info(f"Całkowita liczba klas: {len(klasy)}")
                
                browser.close()
                logger.info("Przeglądarka zamknięta")
                
                items = {
                    'klasa': klasy,
                    'nauczyciel': [t['name'] for t in nauczyciele],
                    'sala': sale
                }
                
                # Zapisz mapowanie nauczycieli (nazwa -> id) do późniejszego użycia
                self.teacher_mapping = {t['name']: t['id'] for t in nauczyciele}
                logger.info("Mapowanie nauczycieli utworzone")
                
                logger.info("=== POBIERANIE ELEMENTÓW ZAKOŃCZONE SUKCESEM ===")
                logger.info(f"PODSUMOWANIE: klasy={len(klasy)}, nauczyciele={len(nauczyciele)}, sale={len(sale)}")
                return items
                
        except Exception as e:
            logger.error(f"=== BŁĄD PODCZAS POBIERANIA ELEMENTÓW ===")
            logger.error(f"Szczegóły błędu: {e}")
            logger.error(f"Typ błędu: {type(e).__name__}")
            logger.info("Przełączam na dane mockowe...")
            return self._get_mock_items()
    
    def get_schedule(self, item_type, item_name):
        """Pobiera plan lekcji dla określonego elementu"""
        logger.info("=== ROZPOCZYNAM POBIERANIE PLANU LEKCJI ===")
        logger.info(f"Typ: {item_type}, Element: {item_name}")
        
        try:
            # Zbuduj URL na podstawie typu
            if item_type == 'nauczyciel':
                logger.info("Przetwarzam żądanie dla nauczyciela...")
                
                if not hasattr(self, 'teacher_mapping'):
                    logger.info("Brak mapowania nauczycieli, pobieram dane...")
                    self.get_available_items()  # Pobierz mapowanie jeśli nie ma
                
                teacher_id = self.teacher_mapping.get(item_name)
                if not teacher_id:
                    logger.warning(f"Nie znaleziono ID dla nauczyciela: {item_name}")
                    logger.info(f"Dostępni nauczyciele (pierwsze 5): {list(self.teacher_mapping.keys())[:5]}")
                    return self._get_mock_schedule(item_name)
                
                schedule_url = f"{self.base_url}/N/{teacher_id}"
                logger.info(f"URL nauczyciela: {schedule_url} (ID: {teacher_id})")
                
            elif item_type == 'sala':
                schedule_url = f"{self.base_url}/S/{item_name}"
                logger.info(f"URL sali: {schedule_url}")
                
            elif item_type == 'klasa':
                schedule_url = f"{self.base_url}/K/{item_name}"
                logger.info(f"URL klasy: {schedule_url}")
            
            else:
                logger.error(f"Nieznany typ elementu: {item_type}")
                return self._get_mock_schedule(item_name)
            
            logger.info(f"Łączę się z: {schedule_url}")
            
            with sync_playwright() as p:
                logger.info("Uruchamiam przeglądarkę dla planu...")
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info("Nawiguję do strony planu...")
                response = page.goto(schedule_url, wait_until="networkidle")
                
                if response:
                    logger.info(f"Odpowiedź serwera: {response.status}")
                    if response.status != 200:
                        logger.warning(f"Nieprawidłowy kod odpowiedzi: {response.status}")
                
                page_title = page.title()
                logger.info(f"Tytuł strony planu: '{page_title}'")
                
                # Pobierz informację o sali/klasie/nauczycielu z nagłówka
                current_item_info = ""
                header_info = page.query_selector('header h4')
                if header_info:
                    current_item_info = header_info.inner_text().strip()
                    logger.info(f"Informacja z nagłówka: '{current_item_info}'")
                
                # Sprawdź czy jest kontener planu zamiast tabeli
                plan_container = page.query_selector('#cont')
                if plan_container:
                    logger.info("Znaleziono kontener planu (#cont) - używam nowego parsera")
                    schedule = self._parse_schedule_page(page, current_item_info)
                else:
                    # Sprawdź czy jest tabela (stary format)
                    tables = page.query_selector_all('table')
                    logger.info(f"Znaleziono {len(tables)} tabel na stronie")
                    
                    if tables:
                        for i, table in enumerate(tables):
                            rows = table.query_selector_all('tr')
                            logger.info(f"  Tabela {i+1}: {len(rows)} wierszy")
                        
                        schedule = self._parse_table_schedule(page)
                    else:
                        logger.warning("Nie znaleziono ani kontenera #cont ani tabeli")
                        schedule = self._get_mock_schedule(item_name)
                
                browser.close()
                logger.info("Przeglądarka zamknięta")
                
                # Sprawdź czy plan zawiera dane
                total_lessons = sum(len(lessons) for day in schedule.values() for lessons in day)
                logger.info(f"Całkowita liczba lekcji w planie: {total_lessons}")
                
                logger.info("=== POBIERANIE PLANU ZAKOŃCZONE ===")
                return schedule
                
        except Exception as e:
            logger.error(f"=== BŁĄD PODCZAS POBIERANIA PLANU ===")
            logger.error(f"Szczegóły błędu: {e}")
            logger.error(f"Typ błędu: {type(e).__name__}")
            logger.info("Przełączam na plan mockowy...")
            return self._get_mock_schedule(item_name)
    
    def _parse_schedule_page(self, page, current_item_info=""):
        """Parsuje stronę z planem lekcji"""
        logger.info("--- PARSOWANIE STRONY PLANU ---")
        
        schedule = {
            'monday': [[] for _ in range(10)],     # Zwiększam do 10 lekcji
            'tuesday': [[] for _ in range(10)],
            'wednesday': [[] for _ in range(10)],
            'thursday': [[] for _ in range(10)],
            'friday': [[] for _ in range(10)]
        }
        
        try:
            # Sprawdź czy jest kontener planu
            plan_container = page.query_selector('#cont')
            if not plan_container:
                logger.warning("Nie znaleziono kontenera planu (#cont)")
                return schedule
                
            logger.info("Znaleziono kontener planu (#cont)")
            
            # Pobierz wszystkie dni
            day_containers = plan_container.query_selector_all('.day-cont')
            logger.info(f"Znaleziono {len(day_containers)} dni")
            
            day_mapping = {
                'Pn': 'monday',
                'Wt': 'tuesday', 
                'Śr': 'wednesday',
                'Cz': 'thursday',
                'Pt': 'friday'
            }
            
            for day_container in day_containers:
                # Nazwa dnia jest w pierwszym div-ie
                day_name_elem = day_container.query_selector('div')
                if not day_name_elem:
                    continue
                    
                day_name_pl = day_name_elem.inner_text().strip()
                day_name_en = day_mapping.get(day_name_pl)
                
                if not day_name_en:
                    logger.warning(f"Nieznany dzień: {day_name_pl}")
                    continue
                    
                logger.info(f"Przetwarzam dzień: {day_name_pl} -> {day_name_en}")
                
                # Pobierz kontener z lekcjami - różne klasy CSS dla różnych widoków
                lessons_container = day_container.query_selector('.sala.lekcje, .nauczyciel.lekcje, .klasa.lekcje, .lekcje')
                if not lessons_container:
                    logger.warning(f"Brak kontenera lekcji dla dnia {day_name_pl}")
                    continue
                
                # Sprawdź typ kontenera (sala/nauczyciel/klasa)
                container_classes = lessons_container.get_attribute('class') or ''
                is_room_view = 'sala' in container_classes
                is_teacher_view = 'nauczyciel' in container_classes  
                is_class_view = 'klasa' in container_classes
                
                logger.info(f"  Typ widoku: {'sala' if is_room_view else 'nauczyciel' if is_teacher_view else 'klasa' if is_class_view else 'nieznany'}")
                
                # Pobierz wszystkie elementy lekcji
                lesson_elements = lessons_container.query_selector_all('div')
                
                # Parsuj lekcje - elementy są grupowane po 5: g, d, k/s, n/k, p
                lessons_parsed = 0
                i = 0
                while i < len(lesson_elements):
                    try:
                        # Sprawdź czy mamy komplet elementów lekcji
                        if i + 4 >= len(lesson_elements):
                            break
                            
                        g_elem = lesson_elements[i]     # Numer lekcji
                        d_elem = lesson_elements[i + 1] # Godzina
                        third_elem = lesson_elements[i + 2]  # Klasa/Sala
                        fourth_elem = lesson_elements[i + 3] # Nauczyciel/Klasa  
                        p_elem = lesson_elements[i + 4] # Przedmiot
                        
                        # Sprawdź klasy CSS
                        if not (g_elem.get_attribute('class') and 'g' in g_elem.get_attribute('class') and 
                                d_elem.get_attribute('class') and 'd' in d_elem.get_attribute('class')):
                            i += 1
                            continue
                        
                        lesson_num = g_elem.inner_text().strip()
                        time = d_elem.inner_text().strip()
                        subject = p_elem.inner_text().strip()
                        
                        # Różne struktury dla różnych widoków
                        if is_teacher_view:
                            # Dla nauczyciela: g, d, s (sala), k (klasa), p
                            room = third_elem.inner_text().strip()
                            class_name = fourth_elem.inner_text().strip() 
                            # Wyciągnij nazwę nauczyciela z nagłówka (usuń przedrostek)
                            teacher = current_item_info.replace('nauczyciel:', '').replace('sala:', '').replace('klasa:', '').strip()
                        elif is_room_view:
                            # Dla sali: g, d, k (klasa), n (nauczyciel), p
                            class_name = third_elem.inner_text().strip()
                            teacher_short = fourth_elem.inner_text().strip()
                            teacher_full = fourth_elem.get_attribute('title') or teacher_short
                            teacher = teacher_full
                            # Wyciągnij numer sali z nagłówka 
                            room = current_item_info.replace('sala:', '').replace('nauczyciel:', '').replace('klasa:', '').strip()
                        else:
                            # Dla klasy lub domyślnie
                            room = third_elem.inner_text().strip()
                            teacher_short = fourth_elem.inner_text().strip()
                            teacher_full = fourth_elem.get_attribute('title') or teacher_short
                            teacher = teacher_full
                            # Wyciągnij nazwę klasy z nagłówka
                            class_name = current_item_info.replace('klasa:', '').replace('sala:', '').replace('nauczyciel:', '').strip()
                        
                        # Sprawdź czy jest element grupy po 5 podstawowych elementach
                        group = ""
                        next_elem_idx = i + 5
                        if next_elem_idx < len(lesson_elements):
                            next_elem = lesson_elements[next_elem_idx]
                            next_classes = next_elem.get_attribute('class') or ''
                            if 'gr1' in next_classes:
                                group = "grupa 1"
                                i += 1  # Dodatkowy przeskok dla elementu grupy
                            elif 'gr2' in next_classes:
                                group = "grupa 2"
                                i += 1  # Dodatkowy przeskok dla elementu grupy
                            elif next_classes.strip() == "" and next_elem.inner_text().strip() == "":
                                # Pusty span oznacza całą klasę (brak podziału na grupy)
                                group = ""
                                i += 1  # Przeskocz pusty element
                        
                        try:
                            lesson_index = int(lesson_num) - 1  # Lekcje numerowane od 1
                            if 0 <= lesson_index < 10:
                                lesson = {
                                    'subject': subject,
                                    'teacher': teacher,
                                    'room': room,
                                    'time': time,
                                    'class': class_name,
                                    'group': group
                                }
                                
                                schedule[day_name_en][lesson_index].append(lesson)
                                lessons_parsed += 1
                                
                                if is_teacher_view:
                                    logger.info(f"  Lekcja {lesson_num}: {subject} - sala {room} - klasa {class_name}" + (f" - {group}" if group else ""))
                                elif is_room_view:
                                    logger.info(f"  Lekcja {lesson_num}: {subject} - {teacher} - {class_name}" + (f" - {group}" if group else ""))
                                else:
                                    logger.info(f"  Lekcja {lesson_num}: {subject} - {teacher} - sala {room}" + (f" - {group}" if group else ""))
                            
                        except ValueError:
                            logger.warning(f"Nieprawidłowy numer lekcji: {lesson_num}")
                        
                        i += 5  # Przejdź do następnej lekcji (podstawowe 5 elementów)
                        
                    except Exception as e:
                        logger.warning(f"Błąd parsowania lekcji na pozycji {i}: {e}")
                        i += 1
                
                logger.info(f"  Sparsowano {lessons_parsed} lekcji dla dnia {day_name_pl}")
            
            total_lessons = sum(len(lessons) for day_schedule in schedule.values() for lessons in day_schedule)
            logger.info(f"--- PARSOWANIE ZAKOŃCZONE: {total_lessons} lekcji ---")
            return schedule
            
        except Exception as e:
            logger.error(f"--- BŁĄD PODCZAS PARSOWANIA ---")
            logger.error(f"Szczegóły: {e}")
            logger.error(f"Typ błędu: {type(e).__name__}")
            return schedule
    
    def _parse_table_schedule(self, page):
        """Parsuje starą wersję planu w formie tabeli HTML"""
        logger.info("--- PARSOWANIE TABELI HTML ---")
        
        schedule = {
            'monday': [[] for _ in range(8)],
            'tuesday': [[] for _ in range(8)],
            'wednesday': [[] for _ in range(8)],
            'thursday': [[] for _ in range(8)],
            'friday': [[] for _ in range(8)]
        }
        
        try:
            table = page.query_selector('table')
            if not table:
                logger.warning("Nie znaleziono tabeli")
                return schedule
            
            rows = table.query_selector_all('tr')[1:]  # Pomijamy nagłówek
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            
            for row_idx, row in enumerate(rows[:8]):
                cells = row.query_selector_all('td, th')
                if len(cells) < 6:
                    continue
                    
                for day_idx, day in enumerate(days):
                    if day_idx + 1 < len(cells):
                        cell = cells[day_idx + 1]
                        lessons = self._parse_cell_content(cell)
                        schedule[day][row_idx] = lessons
            
            logger.info("--- PARSOWANIE TABELI ZAKOŃCZONE ---")
            return schedule
            
        except Exception as e:
            logger.error(f"Błąd parsowania tabeli: {e}")
            return schedule
    
    def _parse_cell_content(self, cell):
        """Parsuje zawartość komórki tabeli"""
        lessons = []
        
        try:
            # Pobierz tekst z komórki
            text = cell.inner_text().strip()
            
            if not text or text == '' or text == '&nbsp;':
                return lessons
            
            logger.info(f"      Parsowanie komórki: '{text}'")
            
            # Podziel na linie
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if not lines:
                logger.info("        Brak linii do przetworzenia")
                return lessons
            
            logger.info(f"        Znalezione linie: {lines}")
            
            # Spróbuj sparsować lekcję
            lesson = {}
            
            # Pierwszy wiersz to zazwyczaj przedmiot
            if lines:
                lesson['subject'] = lines[0]
                logger.info(f"        Przedmiot: {lines[0]}")
            
            # Szukaj nauczyciela i sali w pozostałych liniach
            for line in lines[1:]:
                if self._looks_like_teacher(line):
                    lesson['teacher'] = line
                    logger.info(f"        Nauczyciel: {line}")
                elif self._looks_like_room(line):
                    lesson['room'] = line
                    logger.info(f"        Sala: {line}")
            
            if lesson:
                lessons.append(lesson)
                logger.info(f"        Dodano lekcję: {lesson}")
            
        except Exception as e:
            logger.warning(f"        Błąd podczas parsowania komórki: {e}")
        
        return lessons
    
    def _looks_like_teacher(self, text):
        """Sprawdza czy tekst wygląda jak nazwisko nauczyciela"""
        teacher_patterns = [
            r'^[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+',  # Imię Nazwisko
            r'^[A-Z]{1,3}\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+',  # Skrót + Nazwisko
            r'^\([^)]+\)$'  # Tekst w nawiasach
        ]
        
        for pattern in teacher_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _looks_like_room(self, text):
        """Sprawdza czy tekst wygląda jak numer sali"""
        room_patterns = [
            r'^\d+[a-zA-Z]?$',  # 101, 102a
            r'^sala\s+\d+',  # sala 101
            r'pracownia|laboratorium|gimnastyczna|SG\d+',
        ]
        
        for pattern in room_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _get_mock_items(self):
        """Zwraca przykładowe dane w przypadku błędu"""
        return {
            'klasa': ['1A', '1C', '1D', '1F', '1G', '1H', '2A', '2C', '2D', '2F', '2H'],
            'nauczyciel': [
                'BAJUK JOANNA', 'BANASZEK IRMINA', 'BODZAK ANDRZEJ', 'BUDZIŃSKA ALEKSANDRA'
            ],
            'sala': ['101', '104', '108', '112', '113', '116', '117', '120', 'SG1', 'SG2']
        }
    
    def _get_mock_schedule(self, item_name):
        """Zwraca przykładowy plan lekcji"""
        return {
            'monday': [
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101'}],
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102'}],
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201'}],
                [],
                [{'subject': 'Historia', 'teacher': 'P. Wiśniewski', 'room': '202'}],
                [{'subject': 'Chemia', 'teacher': 'E. Kaczmarek', 'room': 'Lab'}],
                [],
                []
            ],
            'tuesday': [
                [{'subject': 'Fizyka', 'teacher': 'T. Zieliński', 'room': '103'}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101'}],
                [],
                [{'subject': 'WF', 'teacher': 'K. Adamska', 'room': 'Sala gym'}],
                [{'subject': 'Informatyka', 'teacher': 'R. Nowicki', 'room': 'Prac. inf.'}],
                [{'subject': 'Geografia', 'teacher': 'S. Lewandowski', 'room': '104'}],
                [],
                []
            ],
            'wednesday': [
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102'}],
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201'}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101'}],
                [],
                [{'subject': 'Biologia', 'teacher': 'D. Jankowski', 'room': '105'}],
                [{'subject': 'Plastyka', 'teacher': 'B. Kowalczyk', 'room': '106'}],
                [],
                []
            ],
            'thursday': [
                [{'subject': 'Historia', 'teacher': 'P. Wiśniewski', 'room': '202'}],
                [{'subject': 'Fizyka', 'teacher': 'T. Zieliński', 'room': '103'}],
                [{'subject': 'WF', 'teacher': 'K. Adamska', 'room': 'Sala gym'}],
                [],
                [{'subject': 'Chemia', 'teacher': 'E. Kaczmarek', 'room': 'Lab'}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101'}],
                [],
                []
            ],
            'friday': [
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201'}],
                [{'subject': 'Geografia', 'teacher': 'S. Lewandowski', 'room': '104'}],
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102'}],
                [{'subject': 'Informatyka', 'teacher': 'R. Nowicki', 'room': 'Prac. inf.'}],
                [],
                [{'subject': 'Religia', 'teacher': 'Ks. M. Kowal', 'room': '107'}],
                [],
                []
            ]
        }

# Globalna instancja scrapera
scraper = ScheduleScraper()

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
            'message': 'Połączenie działa' if success else 'Błąd połączenia'
        })
    except Exception as e:
        logger.error(f">>> API BŁĄD test-connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/available-items')
def get_available_items():
    """API endpoint do pobierania dostępnych opcji"""
    logger.info(">>> WYWOŁANO API: /api/available-items")
    try:
        items = scraper.get_available_items()
        logger.info(f">>> API SUKCES: zwracam {len(items.get('klasa', []))} klas, {len(items.get('nauczyciel', []))} nauczycieli, {len(items.get('sala', []))} sal")
        return jsonify({
            'success': True,
            'items': items
        })
    except Exception as e:
        logger.error(f">>> API BŁĄD available-items: {e}")
        return jsonify({
            'success': False,
            'error': 'Nie udało się pobrać dostępnych opcji'
        }), 500

@app.route('/api/schedule', methods=['POST'])
def get_schedule():
    """API endpoint do pobierania planu lekcji"""
    logger.info(">>> WYWOŁANO API: /api/schedule")
    try:
        data = request.json
        item_type = data.get('type')
        item_name = data.get('item')
        
        logger.info(f">>> PARAMETRY: typ='{item_type}', element='{item_name}'")
        
        if not item_type or not item_name:
            logger.error(">>> API BŁĄD: brakuje parametrów")
            return jsonify({
                'success': False,
                'error': 'Brakuje wymaganych parametrów'
            }), 400
        
        schedule = scraper.get_schedule(item_type, item_name)
        
        # Policz lekcje do loga
        total_lessons = sum(len(lessons) for day in schedule.values() for lessons in day)
        logger.info(f">>> API SUKCES: zwracam plan z {total_lessons} lekcjami")
        
        return jsonify({
            'success': True,
            'schedule': schedule
        })
        
    except Exception as e:
        logger.error(f">>> API BŁĄD schedule: {e}")
        return jsonify({
            'success': False,
            'error': 'Nie udało się pobrać planu lekcji'
        }), 500

if __name__ == '__main__':
    # Szczegółowe logowanie na starcie
    logger.info("=" * 60)
    logger.info("URUCHAMIANIE APLIKACJI PLAN LEKCJI ZSEIL")
    logger.info("=" * 60)
    logger.info(f"URL bazowy: {scraper.base_url}")
    
    # Test połączenia na starcie
    logger.info("Wykonuję test połączenia...")
    if scraper.test_connection():
        logger.info("✓ Połączenie ze stroną ZSEIL działa!")
    else:
        logger.warning("⚠ Problemy z połączeniem - aplikacja będzie używać danych testowych")
    
    logger.info("Dostępne endpointy:")
    logger.info("  GET  / - Strona główna")
    logger.info("  GET  /api/test-connection - Test połączenia")
    logger.info("  GET  /api/available-items - Lista klas/nauczycieli/sal")
    logger.info("  POST /api/schedule - Plan lekcji")
    logger.info("Serwer będzie dostępny pod adresem: http://127.0.0.1:5000")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
