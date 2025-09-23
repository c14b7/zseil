from playwright.sync_api import sync_playwright
import json
import logging
from datetime import datetime
import time
import os

# Próba załadowania dotenv - jeśli nie jest dostępne, używamy alternatywnej metody
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger_setup = logging.getLogger(__name__)
    logger_setup.info("Załadowano konfigurację z pliku .env")
except ImportError:
    # Alternatywna metoda ładowania .env bez biblioteki dotenv
    def load_dotenv_manual():
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("Załadowano konfigurację z pliku .env (bez biblioteki dotenv)")
        else:
            print("Plik .env nie znaleziony - używam domyślnych wartości")
    
    load_dotenv_manual()

# Konfiguracja logowania
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

class ScheduleScraper:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL', "http://zseil.ikkm.pl/PLAN")
        self.headless_mode = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
        self.scraping_delay = float(os.getenv('SCRAPING_DELAY', '1'))
        self.timeout = int(os.getenv('TIMEOUT', '15000'))
        self.user_agent = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.output_file = os.getenv('OUTPUT_FILE', 'data.json')
        self.teacher_mapping = {}
        
        logger.info(f"Konfiguracja załadowana z .env:")
        logger.info(f"  BASE_URL: {self.base_url}")
        logger.info(f"  HEADLESS_MODE: {self.headless_mode}")
        logger.info(f"  SCRAPING_DELAY: {self.scraping_delay}s")
        logger.info(f"  TIMEOUT: {self.timeout}ms")
        logger.info(f"  OUTPUT_FILE: {self.output_file}")
        
    def test_connection(self):
        """Testuje połączenie ze stroną ZSEIL"""
        logger.info("=== TEST POŁĄCZENIA ===")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless_mode)
                page = browser.new_page()
                
                # Ustaw User-Agent jeśli zdefiniowany
                if self.user_agent:
                    page.set_extra_http_headers({"User-Agent": self.user_agent})
                
                logger.info(f"Próbuję połączyć się z: {self.base_url}")
                response = page.goto(self.base_url, timeout=self.timeout)
                
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
                browser = p.chromium.launch(headless=self.headless_mode)
                page = browser.new_page()
                
                # Ustaw User-Agent jeśli zdefiniowany
                if self.user_agent:
                    page.set_extra_http_headers({"User-Agent": self.user_agent})
                
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
        logger.info(f"=== POBIERANIE PLANU: {item_type} - {item_name} ===")
        
        try:
            # Zbuduj URL na podstawie typu
            if item_type == 'nauczyciel':
                teacher_id = self.teacher_mapping.get(item_name)
                if not teacher_id:
                    logger.warning(f"Nie znaleziono ID dla nauczyciela: {item_name}")
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
                browser = p.chromium.launch(headless=self.headless_mode)
                page = browser.new_page()
                
                # Ustaw User-Agent jeśli zdefiniowany
                if self.user_agent:
                    page.set_extra_http_headers({"User-Agent": self.user_agent})
                
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
                        schedule = self._parse_table_schedule(page)
                    else:
                        logger.warning("Nie znaleziono ani kontenera #cont ani tabeli")
                        schedule = self._get_mock_schedule(item_name)
                
                browser.close()
                
                # Sprawdź czy plan zawiera dane
                total_lessons = sum(len(lessons) for day in schedule.values() for lessons in day)
                logger.info(f"Pobrano plan z {total_lessons} lekcjami")
                
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
            'monday': [[] for _ in range(10)],
            'tuesday': [[] for _ in range(10)],
            'wednesday': [[] for _ in range(10)],
            'thursday': [[] for _ in range(10)],
            'friday': [[] for _ in range(10)]
        }
        
        try:
            plan_container = page.query_selector('#cont')
            if not plan_container:
                logger.warning("Nie znaleziono kontenera planu (#cont)")
                return schedule
                
            logger.info("Znaleziono kontener planu (#cont)")
            
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
                day_name_elem = day_container.query_selector('div')
                if not day_name_elem:
                    continue
                    
                day_name_pl = day_name_elem.inner_text().strip()
                day_name_en = day_mapping.get(day_name_pl)
                
                if not day_name_en:
                    logger.warning(f"Nieznany dzień: {day_name_pl}")
                    continue
                    
                logger.info(f"Przetwarzam dzień: {day_name_pl} -> {day_name_en}")
                
                lessons_container = day_container.query_selector('.sala.lekcje, .nauczyciel.lekcje, .klasa.lekcje, .lekcje')
                if not lessons_container:
                    logger.warning(f"Brak kontenera lekcji dla dnia {day_name_pl}")
                    continue
                
                container_classes = lessons_container.get_attribute('class') or ''
                is_room_view = 'sala' in container_classes
                is_teacher_view = 'nauczyciel' in container_classes  
                is_class_view = 'klasa' in container_classes
                
                lesson_elements = lessons_container.query_selector_all('div')
                
                lessons_parsed = 0
                i = 0
                while i < len(lesson_elements):
                    try:
                        if i + 4 >= len(lesson_elements):
                            break
                            
                        g_elem = lesson_elements[i]
                        d_elem = lesson_elements[i + 1]
                        third_elem = lesson_elements[i + 2]
                        fourth_elem = lesson_elements[i + 3]
                        p_elem = lesson_elements[i + 4]
                        
                        if not (g_elem.get_attribute('class') and 'g' in g_elem.get_attribute('class') and 
                                d_elem.get_attribute('class') and 'd' in d_elem.get_attribute('class')):
                            i += 1
                            continue
                        
                        lesson_num = g_elem.inner_text().strip()
                        time = d_elem.inner_text().strip()
                        subject = p_elem.inner_text().strip()
                        
                        if is_teacher_view:
                            room = third_elem.inner_text().strip()
                            class_name = fourth_elem.inner_text().strip() 
                            teacher = current_item_info.replace('nauczyciel:', '').replace('sala:', '').replace('klasa:', '').strip()
                        elif is_room_view:
                            class_name = third_elem.inner_text().strip()
                            teacher_short = fourth_elem.inner_text().strip()
                            teacher_full = fourth_elem.get_attribute('title') or teacher_short
                            teacher = teacher_full
                            room = current_item_info.replace('sala:', '').replace('nauczyciel:', '').replace('klasa:', '').strip()
                        else:
                            room = third_elem.inner_text().strip()
                            teacher_short = fourth_elem.inner_text().strip()
                            teacher_full = fourth_elem.get_attribute('title') or teacher_short
                            teacher = teacher_full
                            class_name = current_item_info.replace('klasa:', '').replace('sala:', '').replace('nauczyciel:', '').strip()
                        
                        group = ""
                        next_elem_idx = i + 5
                        if next_elem_idx < len(lesson_elements):
                            next_elem = lesson_elements[next_elem_idx]
                            next_classes = next_elem.get_attribute('class') or ''
                            if 'gr1' in next_classes:
                                group = "grupa 1"
                                i += 1
                            elif 'gr2' in next_classes:
                                group = "grupa 2"
                                i += 1
                            elif next_classes.strip() == "" and next_elem.inner_text().strip() == "":
                                group = ""
                                i += 1
                        
                        try:
                            lesson_index = int(lesson_num) - 1
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
                            
                        except ValueError:
                            logger.warning(f"Nieprawidłowy numer lekcji: {lesson_num}")
                        
                        i += 5
                        
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
            
            rows = table.query_selector_all('tr')[1:]
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
            text = cell.inner_text().strip()
            
            if not text or text == '' or text == '&nbsp;':
                return lessons
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if not lines:
                return lessons
            
            lesson = {}
            
            if lines:
                lesson['subject'] = lines[0]
            
            for line in lines[1:]:
                if self._looks_like_teacher(line):
                    lesson['teacher'] = line
                elif self._looks_like_room(line):
                    lesson['room'] = line
            
            if lesson:
                lessons.append(lesson)
        
        except Exception as e:
            logger.warning(f"Błąd podczas parsowania komórki: {e}")
        
        return lessons
    
    def _looks_like_teacher(self, text):
        """Sprawdza czy tekst wygląda jak nazwisko nauczyciela"""
        import re
        teacher_patterns = [
            r'^[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+',
            r'^[A-Z]{1,3}\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+',
            r'^\([^)]+\)$'
        ]
        
        for pattern in teacher_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _looks_like_room(self, text):
        """Sprawdza czy tekst wygląda jak numer sali"""
        import re
        room_patterns = [
            r'^\d+[a-zA-Z]?$',
            r'^sala\s+\d+',
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
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '7:10-7:55', 'class': item_name, 'group': ''}],
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102', 'time': '8:00-8:45', 'class': item_name, 'group': ''}],
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201', 'time': '8:50-9:35', 'class': item_name, 'group': ''}],
                [],
                [{'subject': 'Historia', 'teacher': 'P. Wiśniewski', 'room': '202', 'time': '10:35-11:20', 'class': item_name, 'group': ''}],
                [{'subject': 'Chemia', 'teacher': 'E. Kaczmarek', 'room': 'Lab', 'time': '11:35-12:20', 'class': item_name, 'group': ''}],
                [],
                []
            ],
            'tuesday': [
                [{'subject': 'Fizyka', 'teacher': 'T. Zieliński', 'room': '103', 'time': '7:10-7:55', 'class': item_name, 'group': ''}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '8:00-8:45', 'class': item_name, 'group': ''}],
                [],
                [{'subject': 'WF', 'teacher': 'K. Adamska', 'room': 'Sala gym', 'time': '9:45-10:30', 'class': item_name, 'group': ''}],
                [{'subject': 'Informatyka', 'teacher': 'R. Nowicki', 'room': 'Prac. inf.', 'time': '10:35-11:20', 'class': item_name, 'group': ''}],
                [{'subject': 'Geografia', 'teacher': 'S. Lewandowski', 'room': '104', 'time': '11:35-12:20', 'class': item_name, 'group': ''}],
                [],
                []
            ],
            'wednesday': [
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102', 'time': '7:10-7:55', 'class': item_name, 'group': ''}],
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201', 'time': '8:00-8:45', 'class': item_name, 'group': ''}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '8:50-9:35', 'class': item_name, 'group': ''}],
                [],
                [{'subject': 'Biologia', 'teacher': 'D. Jankowski', 'room': '105', 'time': '10:35-11:20', 'class': item_name, 'group': ''}],
                [{'subject': 'Plastyka', 'teacher': 'B. Kowalczyk', 'room': '106', 'time': '11:35-12:20', 'class': item_name, 'group': ''}],
                [],
                []
            ],
            'thursday': [
                [{'subject': 'Historia', 'teacher': 'P. Wiśniewski', 'room': '202', 'time': '7:10-7:55', 'class': item_name, 'group': ''}],
                [{'subject': 'Fizyka', 'teacher': 'T. Zieliński', 'room': '103', 'time': '8:00-8:45', 'class': item_name, 'group': ''}],
                [{'subject': 'WF', 'teacher': 'K. Adamska', 'room': 'Sala gym', 'time': '8:50-9:35', 'class': item_name, 'group': ''}],
                [],
                [{'subject': 'Chemia', 'teacher': 'E. Kaczmarek', 'room': 'Lab', 'time': '10:35-11:20', 'class': item_name, 'group': ''}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '11:35-12:20', 'class': item_name, 'group': ''}],
                [],
                []
            ],
            'friday': [
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201', 'time': '7:10-7:55', 'class': item_name, 'group': ''}],
                [{'subject': 'Geografia', 'teacher': 'S. Lewandowski', 'room': '104', 'time': '8:00-8:45', 'class': item_name, 'group': ''}],
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102', 'time': '8:50-9:35', 'class': item_name, 'group': ''}],
                [{'subject': 'Informatyka', 'teacher': 'R. Nowicki', 'room': 'Prac. inf.', 'time': '9:45-10:30', 'class': item_name, 'group': ''}],
                [],
                [{'subject': 'Religia', 'teacher': 'Ks. M. Kowal', 'room': '107', 'time': '11:35-12:20', 'class': item_name, 'group': ''}],
                [],
                []
            ]
        }

    def scrape_all_data_to_json(self, output_file='data.json'):
        """Scrapuje wszystkie dostępne dane i zapisuje do pliku JSON"""
        logger.info("=" * 60)
        logger.info("ROZPOCZYNAM PEŁNE SCRAPOWANIE DANYCH DO JSON")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Pobierz listę dostępnych elementów
        logger.info("1. Pobieranie listy dostępnych elementów...")
        available_items = self.get_available_items()
        
        # Struktura danych do zapisania
        data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.base_url,
                'total_classes': len(available_items.get('klasa', [])),
                'total_teachers': len(available_items.get('nauczyciel', [])),
                'total_rooms': len(available_items.get('sala', [])),
                'scraping_errors': []
            },
            'available_items': available_items,
            'schedules': {
                'klasa': {},
                'nauczyciel': {},
                'sala': {}
            }
        }
        
        # Scrapuj plany dla wszystkich klas
        logger.info("2. Scrapowanie planów dla klas...")
        for i, class_name in enumerate(available_items.get('klasa', [])):
            try:
                logger.info(f"   Klasa {i+1}/{len(available_items['klasa'])}: {class_name}")
                schedule = self.get_schedule('klasa', class_name)
                data['schedules']['klasa'][class_name] = schedule
                time.sleep(self.scraping_delay)  # Pauza między requestami z .env
            except Exception as e:
                error_msg = f"Błąd scrapowania klasy {class_name}: {str(e)}"
                logger.error(error_msg)
                data['metadata']['scraping_errors'].append(error_msg)
        
        # Scrapuj plany dla wszystkich nauczycieli 
        logger.info("3. Scrapowanie planów dla nauczycieli...")
        for i, teacher_name in enumerate(available_items.get('nauczyciel', [])):
            try:
                logger.info(f"   Nauczyciel {i+1}/{len(available_items['nauczyciel'])}: {teacher_name}")
                schedule = self.get_schedule('nauczyciel', teacher_name)
                data['schedules']['nauczyciel'][teacher_name] = schedule
                time.sleep(self.scraping_delay)  # Pauza między requestami z .env
            except Exception as e:
                error_msg = f"Błąd scrapowania nauczyciela {teacher_name}: {str(e)}"
                logger.error(error_msg)
                data['metadata']['scraping_errors'].append(error_msg)
        
        # Scrapuj plany dla wszystkich sal
        logger.info("4. Scrapowanie planów dla sal...")
        for i, room_name in enumerate(available_items.get('sala', [])):
            try:
                logger.info(f"   Sala {i+1}/{len(available_items['sala'])}: {room_name}")
                schedule = self.get_schedule('sala', room_name)
                data['schedules']['sala'][room_name] = schedule
                time.sleep(self.scraping_delay)  # Pauza między requestami z .env
            except Exception as e:
                error_msg = f"Błąd scrapowania sali {room_name}: {str(e)}"
                logger.error(error_msg)
                data['metadata']['scraping_errors'].append(error_msg)
        
        # Oblicz statystyki
        total_schedules = (
            len(data['schedules']['klasa']) + 
            len(data['schedules']['nauczyciel']) + 
            len(data['schedules']['sala'])
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        data['metadata']['total_schedules_scraped'] = total_schedules
        data['metadata']['scraping_duration_seconds'] = round(duration, 2)
        data['metadata']['errors_count'] = len(data['metadata']['scraping_errors'])
        
        # Zapisz do pliku JSON
        logger.info("5. Zapisywanie danych do pliku JSON...")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info("=" * 60)
            logger.info("SCRAPOWANIE ZAKOŃCZONE SUKCESEM!")
            logger.info(f"Plik wyjściowy: {output_file}")
            logger.info(f"Czas scrapowania: {duration:.2f} sekund")
            logger.info(f"Pobranych planów: {total_schedules}")
            logger.info(f"Błędów: {len(data['metadata']['scraping_errors'])}")
            if data['metadata']['scraping_errors']:
                logger.info("Błędy:")
                for error in data['metadata']['scraping_errors']:
                    logger.info(f"  - {error}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisywania do pliku: {e}")
            return False

if __name__ == '__main__':
    scraper = ScheduleScraper()
    
    # Test połączenia
    logger.info("Testowanie połączenia...")
    if not scraper.test_connection():
        logger.warning("Problemy z połączeniem - kontynuuję z danymi mockowym")
    
    # Rozpocznij pełne scrapowanie - użyj nazwy pliku z .env
    success = scraper.scrape_all_data_to_json(scraper.output_file)
    
    if success:
        logger.info(f"✅ Scrapowanie zakończone. Plik {scraper.output_file} został utworzony.")
    else:
        logger.error("❌ Scrapowanie nie powiodło się.")