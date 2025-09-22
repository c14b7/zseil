/**
 * Plan Lekcji ZSEIL - JavaScript Only Version
 * Pobiera dane z pliku data.json (generowanego przez app.py)
 */

class ScheduleApp {
    constructor() {
        this.allData = null;
        this.currentSchedule = null;
        this.loading = false;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Inicjalizacja aplikacji planu lekcji (JavaScript Only)');
        
        // Załaduj dane z pliku JSON
        await this.loadDataFromJSON();
        
        // Ustaw event listenery
        this.setupEventListeners();
        
        // Załaduj wszystkie listy
        this.populateAllSelectors();
        
        // Wyświetl metadane
        this.displayMetadata();
    }
    
    async loadDataFromJSON() {
        try {
            console.log('📡 Ładowanie danych z data.json...');
            this.updateDataStatus('Ładowanie danych z JSON...', 'loading');
            
            const response = await fetch('./data.json');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.allData = await response.json();
            
            console.log('✅ Dane JSON załadowane:', {
                klasy: this.allData.available_items?.klasa?.length || 0,
                nauczyciele: this.allData.available_items?.nauczyciel?.length || 0,
                sale: this.allData.available_items?.sala?.length || 0,
                plany_klas: Object.keys(this.allData.schedules?.klasa || {}).length,
                plany_nauczycieli: Object.keys(this.allData.schedules?.nauczyciel || {}).length,
                plany_sal: Object.keys(this.allData.schedules?.sala || {}).length
            });
            
            this.updateDataStatus('Dane załadowane z JSON', 'success');
            this.enableControls();
            
        } catch (error) {
            console.error('❌ Błąd ładowania danych JSON:', error);
            this.updateDataStatus('Błąd ładowania JSON - używam danych testowych', 'error');
            this.loadFallbackData();
            this.enableControls();
        }
    }
    
    loadFallbackData() {
        console.log('⚠️ Ładowanie danych przykładowych');
        this.allData = {
            metadata: {
                scraped_at: new Date().toISOString(),
                source_url: 'http://zseil.ikkm.pl/PLAN',
                total_classes: 11,
                total_teachers: 4,
                total_rooms: 10,
                total_schedules_scraped: 25,
                errors_count: 0,
                scraping_errors: []
            },
            available_items: {
                klasa: ['1A', '1C', '1D', '1F', '1G', '1H', '2A', '2C', '2D', '2F', '2H'],
                nauczyciel: ['BAJUK JOANNA', 'BANASZEK IRMINA', 'BODZAK ANDRZEJ', 'BUDZIŃSKA ALEKSANDRA'],
                sala: ['101', '104', '108', '112', '113', '116', '117', '120', 'SG1', 'SG2']
            },
            schedules: {
                klasa: {},
                nauczyciel: {},
                sala: {}
            }
        };
        
        // Wygeneruj przykładowe plany dla pierwszych kilku klas
        ['1A', '1C', '2A'].forEach(className => {
            this.allData.schedules.klasa[className] = this.generateMockSchedule(className);
        });
    }
    
    generateMockSchedule(itemName) {
        return {
            'monday': [
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Historia', 'teacher': 'P. Wiśniewski', 'room': '202', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Chemia', 'teacher': 'E. Kaczmarek', 'room': 'Lab', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'tuesday': [
                [{'subject': 'Fizyka', 'teacher': 'T. Zieliński', 'room': '103', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'WF', 'teacher': 'K. Adamska', 'room': 'Sala gym', 'time': '9:45-10:30', 'class': itemName, 'group': ''}],
                [{'subject': 'Informatyka', 'teacher': 'R. Nowicki', 'room': 'Prac. inf.', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Geografia', 'teacher': 'S. Lewandowski', 'room': '104', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'wednesday': [
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Biologia', 'teacher': 'D. Jankowski', 'room': '105', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Plastyka', 'teacher': 'B. Kowalczyk', 'room': '106', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'thursday': [
                [{'subject': 'Historia', 'teacher': 'P. Wiśniewski', 'room': '202', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Fizyka', 'teacher': 'T. Zieliński', 'room': '103', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'WF', 'teacher': 'K. Adamska', 'room': 'Sala gym', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Chemia', 'teacher': 'E. Kaczmarek', 'room': 'Lab', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Matematyka', 'teacher': 'J. Kowalski', 'room': '101', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'friday': [
                [{'subject': 'Angielski', 'teacher': 'M. Kozłowska', 'room': '201', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Geografia', 'teacher': 'S. Lewandowski', 'room': '104', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Polski', 'teacher': 'A. Nowak', 'room': '102', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [{'subject': 'Informatyka', 'teacher': 'R. Nowicki', 'room': 'Prac. inf.', 'time': '9:45-10:30', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Religia', 'teacher': 'Ks. M. Kowal', 'room': '107', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ]
        };
    }
    
    enableControls() {
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        const loadBtn = document.getElementById('load-btn');
        
        classSelector.disabled = false;
        teacherSelector.disabled = false;
        roomSelector.disabled = false;
        loadBtn.disabled = false;
        
        // Zaktualizuj placeholder
        classSelector.innerHTML = '<option value="">Wybierz klasę...</option>';
        teacherSelector.innerHTML = '<option value="">Wybierz nauczyciela...</option>';
        roomSelector.innerHTML = '<option value="">Wybierz salę...</option>';
    }
    
    updateDataStatus(message, status = '') {
        const dataInfo = document.getElementById('data-info');
        const dataStatus = document.getElementById('data-status');
        
        dataInfo.textContent = message;
        
        // Usuń poprzednie klasy statusu
        dataStatus.className = 'data-status';
        
        // Dodaj nową klasę statusu
        if (status) {
            dataStatus.classList.add(status);
        }
    }
    
    displayMetadata() {
        if (!this.allData || !this.allData.metadata) {
            return;
        }
        
        const metadata = this.allData.metadata;
        
        // Status danych
        const loadedStatus = document.getElementById('data-loaded-status');
        loadedStatus.textContent = metadata.errors_count === 0 ? 'Wszystkie dane OK' : `${metadata.errors_count} błędów`;
        
        // Data aktualizacji
        const lastUpdate = document.getElementById('last-update');
        if (metadata.scraped_at) {
            const date = new Date(metadata.scraped_at);
            lastUpdate.textContent = date.toLocaleString('pl-PL');
        }
        
        // Liczba planów
        const totalSchedules = document.getElementById('total-schedules');
        totalSchedules.textContent = metadata.total_schedules_scraped || 0;
    }
    
    setupEventListeners() {
        // Event listenery dla wszystkich selektorów
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        const loadBtn = document.getElementById('load-btn');
        
        // Gdy wybieramy klasę, zerujemy pozostałe
        classSelector.addEventListener('change', (e) => {
            if (e.target.value) {
                teacherSelector.value = '';
                roomSelector.value = '';
            }
            this.updateLoadButton();
        });
        
        // Gdy wybieramy nauczyciela, zerujemy pozostałe
        teacherSelector.addEventListener('change', (e) => {
            if (e.target.value) {
                classSelector.value = '';
                roomSelector.value = '';
            }
            this.updateLoadButton();
        });
        
        // Gdy wybieramy salę, zerujemy pozostałe
        roomSelector.addEventListener('change', (e) => {
            if (e.target.value) {
                classSelector.value = '';
                teacherSelector.value = '';
            }
            this.updateLoadButton();
        });
        
        // Przycisk ładowania planu
        loadBtn.addEventListener('click', () => {
            this.loadSchedule();
        });
        
        // Enter w selektorach
        [classSelector, teacherSelector, roomSelector].forEach(selector => {
            selector.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.loadSchedule();
                }
            });
        });
    }
    
    updateLoadButton() {
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        const loadBtn = document.getElementById('load-btn');
        
        // Przycisk aktywny tylko gdy wybrany jest jeden element
        const hasSelection = classSelector.value || teacherSelector.value || roomSelector.value;
        loadBtn.disabled = !hasSelection || this.loading;
    }
    
    populateAllSelectors() {
        console.log('🔄 Wypełnianie wszystkich list rozwijanych');
        
        this.populateSelector('class-selector', 'klasa');
        this.populateSelector('teacher-selector', 'nauczyciel');
        this.populateSelector('room-selector', 'sala');
    }
    
    populateSelector(selectorId, type) {
        const selector = document.getElementById(selectorId);
        
        if (!this.allData || !this.allData.available_items || !this.allData.available_items[type]) {
            console.warn(`⚠️ Brak danych dla typu: ${type}`);
            return;
        }
        
        // Wyczyść selector (zachowaj placeholder)
        const placeholder = selector.querySelector('option[value=""]');
        selector.innerHTML = '';
        if (placeholder) {
            selector.appendChild(placeholder);
        }
        
        // Dodaj opcje
        const items = this.allData.available_items[type];
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            
            // Sprawdź czy dla tego elementu istnieje plan
            const hasSchedule = this.allData.schedules && 
                               this.allData.schedules[type] && 
                               this.allData.schedules[type][item];
            
            if (!hasSchedule) {
                option.textContent += ' (brak planu)';
                option.style.color = '#64748b';
            }
            
            selector.appendChild(option);
        });
        
        console.log(`✅ Załadowano ${items.length} opcji dla typu ${type}`);
    }
    
    loadSchedule() {
        if (this.loading) {
            console.log('⏳ Już trwa ładowanie...');
            return;
        }
        
        // Określ który selektor jest wybrany
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        
        let type, item;
        
        if (classSelector.value) {
            type = 'klasa';
            item = classSelector.value;
        } else if (teacherSelector.value) {
            type = 'nauczyciel';
            item = teacherSelector.value;
        } else if (roomSelector.value) {
            type = 'sala';
            item = roomSelector.value;
        } else {
            this.showError('Wybierz klasę, nauczyciela lub salę.');
            return;
        }
        
        console.log(`📅 Ładowanie planu z JSON: ${type} - ${item}`);
        
        this.setLoading(true);
        this.hideError();
        
        try {
            // Pobierz plan z załadowanych danych JSON
            if (!this.allData || !this.allData.schedules || !this.allData.schedules[type]) {
                throw new Error('Brak danych o planach w załadowanym JSON');
            }
            
            const schedule = this.allData.schedules[type][item];
            
            if (!schedule) {
                throw new Error(`Brak planu dla "${item}" w kategorii "${type}"`);
            }
            
            console.log('✅ Załadowano plan z JSON:', schedule);
            
            this.currentSchedule = schedule;
            this.displaySchedule(type, item);
            
        } catch (error) {
            console.error('❌ Błąd ładowania planu z JSON:', error);
            this.showError(`Nie udało się załadować planu dla "${item}". ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    displaySchedule(type, item) {
        console.log('🎨 Wyświetlanie planu lekcji');
        
        const table = document.getElementById('schedule-table');
        const tbody = document.getElementById('schedule-body');
        
        // Wyczyść tabelę
        tbody.innerHTML = '';
        
        if (!this.currentSchedule) {
            this.showError('Brak danych planu do wyświetlenia.');
            return;
        }
        
        // Godziny lekcji
        const lessonTimes = [
            '7:10-7:55', '8:00-8:45', '8:50-9:35', '9:45-10:30',
            '10:35-11:20', '11:35-12:20', '12:25-13:10', '13:15-14:00',
            '14:05-14:50', '14:55-15:40'
        ];
        
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        
        // Znajdź maksymalną liczbę lekcji
        let maxLessons = 0;
        days.forEach(day => {
            if (this.currentSchedule[day]) {
                maxLessons = Math.max(maxLessons, this.currentSchedule[day].length);
            }
        });
        
        // Generuj wiersze tabeli
        for (let lessonIndex = 0; lessonIndex < Math.min(maxLessons, 10); lessonIndex++) {
            const row = document.createElement('tr');
            
            // Numer lekcji i godzina
            const lessonCell = document.createElement('td');
            lessonCell.className = 'lesson-number';
            lessonCell.textContent = `${lessonIndex + 1}. ${lessonTimes[lessonIndex] || ''}`;
            row.appendChild(lessonCell);
            
            // Komórki dla każdego dnia
            days.forEach(day => {
                const cell = document.createElement('td');
                cell.className = 'lesson-cell';
                
                const daySchedule = this.currentSchedule[day];
                if (daySchedule && daySchedule[lessonIndex] && daySchedule[lessonIndex].length > 0) {
                    // Może być więcej niż jedna lekcja w tym czasie (grupy)
                    daySchedule[lessonIndex].forEach((lesson, index) => {
                        if (index > 0) {
                            cell.appendChild(document.createElement('hr'));
                        }
                        
                        const lessonDiv = document.createElement('div');
                        lessonDiv.className = 'lesson';
                        
                        // Dodaj atrybut data-subject dla kolorowania
                        if (lesson.subject) {
                            lessonDiv.setAttribute('data-subject', lesson.subject.toLowerCase());
                        }
                        
                        // Przedmiot
                        const subjectDiv = document.createElement('div');
                        subjectDiv.className = 'subject';
                        subjectDiv.textContent = lesson.subject || '';
                        lessonDiv.appendChild(subjectDiv);
                        
                        // Szczegóły w zależności od typu widoku
                        const detailsDiv = document.createElement('div');
                        detailsDiv.className = 'details';
                        
                        if (type === 'klasa') {
                            // Dla klasy: pokaż nauczyciela i salę
                            if (lesson.teacher) detailsDiv.innerHTML += `<span class="teacher">${lesson.teacher}</span><br>`;
                            if (lesson.room) detailsDiv.innerHTML += `<span class="room">sala ${lesson.room}</span>`;
                        } else if (type === 'nauczyciel') {
                            // Dla nauczyciela: pokaż klasę i salę
                            if (lesson.class) detailsDiv.innerHTML += `<span class="class">${lesson.class}</span><br>`;
                            if (lesson.room) detailsDiv.innerHTML += `<span class="room">sala ${lesson.room}</span>`;
                        } else if (type === 'sala') {
                            // Dla sali: pokaż klasę i nauczyciela
                            if (lesson.class) detailsDiv.innerHTML += `<span class="class">${lesson.class}</span><br>`;
                            if (lesson.teacher) detailsDiv.innerHTML += `<span class="teacher">${lesson.teacher}</span>`;
                        }
                        
                        // Grupa jeśli istnieje
                        if (lesson.group) {
                            const groupDiv = document.createElement('div');
                            groupDiv.className = 'group';
                            groupDiv.textContent = lesson.group;
                            detailsDiv.appendChild(groupDiv);
                        }
                        
                        lessonDiv.appendChild(detailsDiv);
                        cell.appendChild(lessonDiv);
                    });
                }
                
                row.appendChild(cell);
            });
            
            tbody.appendChild(row);
        }
        
        // Pokaż tabelę
        table.classList.remove('hidden');
        
        console.log(`✅ Wyświetlono plan dla ${type}: ${item}`);
    }
    
    setLoading(loading) {
        this.loading = loading;
        
        const loadingDiv = document.getElementById('loading');
        const loadBtn = document.getElementById('load-btn');
        
        if (loading) {
            loadingDiv.classList.remove('hidden');
            loadBtn.disabled = true;
            loadBtn.textContent = '⏳ Ładowanie...';
        } else {
            loadingDiv.classList.add('hidden');
            this.updateLoadButton(); // Użyj funkcji która sprawdza czy coś jest wybrane
            loadBtn.textContent = '📋 Pokaż plan';
        }
    }
    
    showError(message) {
        console.error('💥 Błąd:', message);
        
        const errorDiv = document.getElementById('error-message');
        const table = document.getElementById('schedule-table');
        
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        table.classList.add('hidden');
    }
    
    hideError() {
        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.add('hidden');
    }
}

// Uruchom aplikację po załadowaniu DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌟 Uruchamianie aplikacji planu lekcji ZSEIL (JavaScript Only)');
    new ScheduleApp();
});

// Debug info
console.log('📋 Plan Lekcji ZSEIL - Wersja JavaScript Only');
console.log('📄 Dane z pliku: data.json');
console.log('🔗 GitHub Repository: https://github.com/c14b7/zsei');
console.log('⚡ Powered by Pure JavaScript + JSON');