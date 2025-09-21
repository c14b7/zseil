# ESP32-C3 Plan Lekcji - MicroPython
# Prosta implementacja web serwera który komunikuje się z głównym serwerem Flask

import network
import socket
import urequests
import json
import time
from machine import Pin, Timer

class ESP32ScheduleServer:
    def __init__(self):
        self.led = Pin(2, Pin.OUT)  # LED na ESP32-C3
        self.main_server = "192.168.1.100:5000"  # Zmień na IP Twojego komputera
        self.cache = {}
        self.cache_timeout = 3600  # 1 godzina
        
    def connect_wifi(self, ssid, password):
        """Połącz z WiFi"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if not wlan.isconnected():
            print(f"Łączę z WiFi: {ssid}")
            wlan.connect(ssid, password)
            
            while not wlan.isconnected():
                self.led.value(not self.led.value())  # Migaj LED
                time.sleep(0.5)
        
        self.led.value(1)  # LED włączony = połączony
        print(f"WiFi połączony! IP: {wlan.ifconfig()[0]}")
        return wlan.ifconfig()[0]
    
    def get_from_main_server(self, endpoint, data=None):
        """Pobierz dane z głównego serwera Flask"""
        try:
            url = f"http://{self.main_server}{endpoint}"
            
            if data:
                response = urequests.post(url, 
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(data))
            else:
                response = urequests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Błąd HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            return None
    
    def get_available_items(self):
        """Pobierz listę dostępnych klas/nauczycieli/sal"""
        cache_key = "available_items"
        
        # Sprawdź cache
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        
        # Pobierz z głównego serwera
        result = self.get_from_main_server("/api/available-items")
        
        if result and result.get('success'):
            # Zapisz w cache
            self.cache[cache_key] = (time.time(), result['items'])
            return result['items']
        
        return None
    
    def get_schedule(self, schedule_type, item_name):
        """Pobierz plan lekcji"""
        cache_key = f"schedule_{schedule_type}_{item_name}"
        
        # Sprawdź cache
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_timeout:
                return data
        
        # Pobierz z głównego serwera
        result = self.get_from_main_server("/api/schedule", {
            "type": schedule_type,
            "item": item_name
        })
        
        if result and result.get('success'):
            # Zapisz w cache
            self.cache[cache_key] = (time.time(), result['schedule'])
            return result['schedule']
        
        return None
    
    def generate_html_page(self, items=None, schedule=None, selected_type="klasa", selected_item=""):
        """Generuj prostą stronę HTML"""
        
        # Opcje dla selecta
        options_html = ""
        if items and selected_type in items:
            for item in items[selected_type]:
                selected = "selected" if item == selected_item else ""
                options_html += f'<option value="{item}" {selected}>{item}</option>'
        
        # Tabela planu
        schedule_html = ""
        if schedule:
            schedule_html = self.generate_schedule_table(schedule, selected_type)
        
        html = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan ZSEIL - ESP32</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .controls {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 10px; }}
        label {{ display: inline-block; width: 80px; }}
        select, button {{ padding: 8px; margin: 5px; }}
        button {{ background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        button:hover {{ background: #2980b9; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #34495e; color: white; }}
        .lesson {{ background: #e8f6f3; margin: 2px; padding: 4px; border-radius: 3px; }}
        .status {{ text-align: center; margin: 20px; padding: 10px; border-radius: 5px; }}
        .error {{ background: #ffebee; color: #c62828; }}
        .info {{ background: #e3f2fd; color: #1565c0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Plan Lekcji ZSEIL</h1>
        <div class="status info">🔧 Serwowane przez ESP32-C3</div>
        
        <form method="get" action="/">
            <div class="controls">
                <div class="form-group">
                    <label>Typ:</label>
                    <label><input type="radio" name="type" value="klasa" {"checked" if selected_type == "klasa" else ""}> Klasa</label>
                    <label><input type="radio" name="type" value="nauczyciel" {"checked" if selected_type == "nauczyciel" else ""}> Nauczyciel</label>
                    <label><input type="radio" name="type" value="sala" {"checked" if selected_type == "sala" else ""}> Sala</label>
                </div>
                
                <div class="form-group">
                    <label>Wybór:</label>
                    <select name="item">
                        <option value="">Wybierz...</option>
                        {options_html}
                    </select>
                    <button type="submit">📅 Pokaż plan</button>
                </div>
            </div>
        </form>
        
        {schedule_html}
    </div>
</body>
</html>
"""
        return html
    
    def generate_schedule_table(self, schedule, view_type):
        """Generuj tabelę z planem lekcji"""
        days = {
            'monday': 'Poniedziałek',
            'tuesday': 'Wtorek', 
            'wednesday': 'Środa',
            'thursday': 'Czwartek',
            'friday': 'Piątek'
        }
        
        times = [
            '7:10-7:55', '8:00-8:45', '8:50-9:35', '9:45-10:30',
            '10:35-11:20', '11:35-12:20', '12:25-13:10', '13:15-14:00'
        ]
        
        html = '<table><thead><tr><th>Godzina</th>'
        for day_name in days.values():
            html += f'<th>{day_name}</th>'
        html += '</tr></thead><tbody>'
        
        max_lessons = max(len(schedule.get(day, [])) for day in days.keys())
        
        for lesson_idx in range(min(max_lessons, 8)):
            html += f'<tr><td><strong>{lesson_idx + 1}.</strong><br>{times[lesson_idx] if lesson_idx < len(times) else ""}</td>'
            
            for day_key in days.keys():
                html += '<td>'
                day_schedule = schedule.get(day_key, [])
                
                if lesson_idx < len(day_schedule) and day_schedule[lesson_idx]:
                    for lesson in day_schedule[lesson_idx]:
                        html += '<div class="lesson">'
                        html += f'<strong>{lesson.get("subject", "")}</strong><br>'
                        
                        if view_type == "klasa":
                            html += f'{lesson.get("teacher", "")}<br>sala {lesson.get("room", "")}'
                        elif view_type == "nauczyciel":
                            html += f'{lesson.get("class", "")}<br>sala {lesson.get("room", "")}'
                        elif view_type == "sala":
                            html += f'{lesson.get("class", "")}<br>{lesson.get("teacher", "")}'
                        
                        if lesson.get("group"):
                            html += f'<br><small>{lesson.get("group")}</small>'
                        
                        html += '</div>'
                
                html += '</td>'
            
            html += '</tr>'
        
        html += '</tbody></table>'
        return html
    
    def handle_request(self, request):
        """Obsłuż żądanie HTTP"""
        try:
            # Parsuj żądanie
            lines = request.decode('utf-8').split('\r\n')
            method_line = lines[0]
            
            if "GET /" in method_line:
                # Parsuj parametry URL
                params = {}
                if "?" in method_line:
                    query = method_line.split("?")[1].split(" ")[0]
                    for param in query.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            params[key] = value.replace("%20", " ")
                
                # Pobierz dostępne elementy
                items = self.get_available_items()
                
                schedule = None
                selected_type = params.get('type', 'klasa')
                selected_item = params.get('item', '')
                
                # Jeśli wybrano element, pobierz plan
                if selected_item and items:
                    schedule = self.get_schedule(selected_type, selected_item)
                
                # Generuj odpowiedź HTML
                html = self.generate_html_page(items, schedule, selected_type, selected_item)
                
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(html.encode('utf-8'))}\r\n\r\n{html}"
                return response.encode('utf-8')
            
            else:
                # 404 dla innych ścieżek
                html = "<h1>404 - Nie znaleziono</h1>"
                response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
                return response.encode('utf-8')
                
        except Exception as e:
            print(f"Błąd obsługi żądania: {e}")
            html = f"<h1>500 - Błąd serwera</h1><p>{e}</p>"
            response = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
            return response.encode('utf-8')
    
    def start_server(self, port=80):
        """Uruchom serwer HTTP"""
        addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)
        
        print(f'Serwer HTTP nasłuchuje na porcie {port}')
        
        while True:
            try:
                cl, addr = s.accept()
                print(f'Połączenie z {addr}')
                
                request = cl.recv(1024)
                response = self.handle_request(request)
                
                cl.send(response)
                cl.close()
                
            except Exception as e:
                print(f"Błąd serwera: {e}")
                try:
                    cl.close()
                except:
                    pass

# Główna funkcja
def main():
    server = ESP32ScheduleServer()
    
    # Podaj dane WiFi
    WIFI_SSID = "TwojeWiFi"
    WIFI_PASSWORD = "TwojeHaslo"
    
    # Podaj IP głównego serwera Flask (Twojego komputera)
    server.main_server = "192.168.1.100:5000"  # ZMIEŃ TO!
    
    try:
        # Połącz z WiFi
        ip = server.connect_wifi(WIFI_SSID, WIFI_PASSWORD)
        
        print("=== ESP32 Plan Lekcji ZSEIL ===")
        print(f"Adres ESP32: http://{ip}")
        print(f"Główny serwer: http://{server.main_server}")
        print("Gotowy do obsługi żądań!")
        
        # Uruchom serwer
        server.start_server(80)
        
    except KeyboardInterrupt:
        print("Zatrzymywanie serwera...")
    except Exception as e:
        print(f"Błąd: {e}")

if __name__ == "__main__":
    main()