#!/usr/bin/env python3
"""
Skrypt do pobierania danych z planu lekcji ZSEIL i zapisywania do JSON
Uruchamiany przez GitHub Actions
"""

import json
import logging
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright
import re

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScheduleDataScraper:
    def __init__(self):
        self.base_url = "http://zseil.ikkm.pl/PLAN"
        self.teacher_mapping = {}
        self.data_dir = "data"
        
        # Upewnij się, że katalog data istnieje
        os.makedirs(self.data_dir, exist_ok=True)
        
    def save_json(self, data, filename):
        """Zapisuje dane do pliku JSON"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Zapisano dane do {filepath}")
            return True
        except Exception as e:
            logger.error(f"Błąd zapisywania {filepath}: {e}")
            return False
    
    def get_available_items(self):
        """Pobiera listę dostępnych klas, nauczycieli i sal i zapisuje do JSON"""
        logger.info("=== POBIERANIE DOSTĘPNYCH ELEMENTÓW ===")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info(f"Łączę się z {self.base_url}")
                page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                
                # Pobierz nauczycieli
                nauczyciele = []
                teacher_elements = page.query_selector_all("#lista-n p[data-id]")
                logger.info(f"Znaleziono {len(teacher_elements)} nauczycieli")
                
                for elem in teacher_elements:
                    teacher_id = elem.get_attribute("data-id")
                    teacher_name = elem.inner_text().strip()
                    if teacher_id and teacher_name:
                        nauczyciele.append({
                            'name': teacher_name,
                            'id': teacher_id
                        })
                
                # Pobierz sale
                sale = []
                room_elements = page.query_selector_all("#lista-s p")
                logger.info(f"Znaleziono {len(room_elements)} sal")
                
                for elem in room_elements:
                    room_name = elem.inner_text().strip()
                    if room_name:
                        sale.append(room_name)
                
                # Pobierz klasy
                klasy = []
                class_elements = page.query_selector_all("#lista-k p")
                logger.info(f"Znaleziono {len(class_elements)} klas")
                
                for elem in class_elements:
                    class_name = elem.inner_text().strip()
                    if class_name:
                        klasy.append(class_name)
                
                browser.close()
                
                # Zapisz mapowanie nauczycieli
                self.teacher_mapping = {t['name']: t['id'] for t in nauczyciele}
                
                # Przygotuj dane do zapisu
                items_data = {
                    'klasa': sorted(klasy),
                    'nauczyciel': sorted([t['name'] for t in nauczyciele]),
                    'sala': sorted(sale),
                    'last_updated': datetime.now().isoformat(),
                    'teacher_mapping': self.teacher_mapping
                }
                
                # Zapisz do pliku JSON
                success = self.save_json(items_data, 'available_items.json')
                
                if success:
                    logger.info(f"SUKCES: klasy={len(klasy)}, nauczyciele={len(nauczyciele)}, sale={len(sale)}")
                    return items_data
                else:
                    raise Exception("Nie udało się zapisać danych")
                    
        except Exception as e:
            logger.error(f"Błąd podczas pobierania elementów: {e}")
            return None
    
    def get_schedule_for_item(self, item_type, item_name):
        """Pobiera plan lekcji dla określonego elementu"""
        logger.info(f"Pobieram plan: {item_type} - {item_name}")
        
        try:
            # Określ URL
            if item_type == 'nauczyciel':
                teacher_id = self.teacher_mapping.get(item_name)
                if not teacher_id:
                    logger.warning(f"Nie znaleziono ID dla nauczyciela: {item_name}")
                    return None
                schedule_url = f"{self.base_url}/N/{teacher_id}"
            elif item_type == 'sala':
                schedule_url = f"{self.base_url}/S/{item_name}"
            elif item_type == 'klasa':
                schedule_url = f"{self.base_url}/K/{item_name}"
            else:
                logger.error(f"Nieznany typ: {item_type}")
                return None
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                logger.info(f"Łączę się z {schedule_url}")
                page.goto(schedule_url, wait_until="networkidle", timeout=30000)
                
                # Pobierz informację z nagłówka
                current_item_info = ""
                header_info = page.query_selector('header h4')
                if header_info:
                    current_item_info = header_info.inner_text().strip()
                
                # Parsuj plan
                schedule = self._parse_schedule_page(page, current_item_info)
                
                browser.close()
                
                # Dodaj metadane
                schedule_data = {
                    'type': item_type,
                    'name': item_name,
                    'schedule': schedule,
                    'last_updated': datetime.now().isoformat(),
                    'source_url': schedule_url
                }
                
                return schedule_data
                
        except Exception as e:
            logger.error(f"Błąd podczas pobierania planu dla {item_type}/{item_name}: {e}")
            return None
    
    def _parse_schedule_page(self, page, current_item_info=""):
        """Parsuje stronę z planem lekcji"""
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
                logger.warning("Nie znaleziono kontenera planu")
                return schedule
            
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
                    continue
                
                lessons_container = day_container.query_selector('.sala.lekcje, .nauczyciel.lekcje, .klasa.lekcje, .lekcje')
                if not lessons_container:
                    continue
                
                container_classes = lessons_container.get_attribute('class') or ''
                is_room_view = 'sala' in container_classes
                is_teacher_view = 'nauczyciel' in container_classes  
                is_class_view = 'klasa' in container_classes
                
                lesson_elements = lessons_container.query_selector_all('div')
                
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
                        except ValueError:
                            pass
                        
                        i += 5
                        
                    except Exception as e:
                        i += 1
            
            return schedule
            
        except Exception as e:
            logger.error(f"Błąd parsowania planu: {e}")
            return schedule
    
    def scrape_all_schedules(self):
        """Pobiera wszystkie plany i zapisuje do plików JSON"""
        logger.info("=== POBIERANIE WSZYSTKICH PLANÓW ===")
        
        # Najpierw pobierz dostępne elementy
        items_data = self.get_available_items()
        if not items_data:
            logger.error("Nie udało się pobrać dostępnych elementów")
            return False
        
        total_success = 0
        total_items = 0
        
        # Pobierz plany dla wszystkich typów
        for item_type in ['klasa', 'nauczyciel', 'sala']:
            items = items_data[item_type]
            logger.info(f"Pobieram plany dla {len(items)} elementów typu {item_type}")
            
            type_success = 0
            
            for item_name in items:
                total_items += 1
                schedule_data = self.get_schedule_for_item(item_type, item_name)
                
                if schedule_data:
                    # Zapisz plan do pliku
                    filename = f"schedule_{item_type}_{item_name.replace('/', '_').replace(' ', '_')}.json"
                    if self.save_json(schedule_data, filename):
                        total_success += 1
                        type_success += 1
                
                # Dodaj małą przerwę między żądaniami
                import time
                time.sleep(0.5)
            
            logger.info(f"Pomyślnie pobrano {type_success}/{len(items)} planów dla typu {item_type}")
        
        # Zapisz metadane
        metadata = {
            'total_items': total_items,
            'successful_items': total_success,
            'last_full_update': datetime.now().isoformat(),
            'success_rate': total_success / total_items if total_items > 0 else 0
        }
        
        self.save_json(metadata, 'metadata.json')
        
        logger.info(f"=== ZAKOŃCZONO: {total_success}/{total_items} planów ===")
        return total_success > 0

def main():
    """Główna funkcja skryptu"""
    logger.info("Rozpoczynam pobieranie danych planu lekcji ZSEIL")
    
    scraper = ScheduleDataScraper()
    
    try:
        success = scraper.scrape_all_schedules()
        
        if success:
            logger.info("✓ Pomyślnie zaktualizowano dane")
            sys.exit(0)
        else:
            logger.error("✗ Nie udało się zaktualizować danych")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Krytyczny błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()