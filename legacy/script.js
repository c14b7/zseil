/**
 * Plan Lekcji ZSEIL - Frontend dla Flask API
 * Komunikuje się z backendem Flask przez API endpoints
 */

class ScheduleApp {
    constructor() {
        this.availableItems = null;
        this.currentSchedule = null;
        this.loading = false;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Inicjalizacja aplikacji planu lekcji');
        
        // Test połączenia z API
        await this.testConnection();
        
        // Pobierz dostępne elementy
        await this.loadAvailableItems();
        
        // Ustaw event listenery
        this.setupEventListeners();
        
        // Załaduj domyślną listę klas
        this.updateItemSelector('klasa');
    }
    
    async testConnection() {
        try {
            console.log('🔌 Testowanie połączenia z API...');
            const response = await fetch('/api/test-connection');
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Połączenie z API działa');
            } else {
                console.warn('⚠️ Problem z połączeniem:', data.message);
            }
        } catch (error) {
            console.error('❌ Błąd połączenia z API:', error);
        }
    }
    
    async loadAvailableItems() {
        try {
            console.log('📡 Pobieranie dostępnych elementów z API...');
            
            const response = await fetch('/api/available-items');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Nieznany błąd API');
            }
            
            this.availableItems = data.items;
            
            console.log('✅ Załadowano dostępne elementy:', {
                klasy: this.availableItems.klasa?.length || 0,
                nauczyciele: this.availableItems.nauczyciel?.length || 0,
                sale: this.availableItems.sala?.length || 0
            });
            
        } catch (error) {
            console.error('❌ Błąd pobierania dostępnych elementów:', error);
            this.showError('Nie udało się załadować listy dostępnych opcji. Sprawdź połączenie z serwerem.');
            
            // Załaduj dane przykładowe jako fallback
            this.loadFallbackData();
        }
    }
    
    loadFallbackData() {
        console.log('⚠️ Ładowanie danych przykładowych');
        this.availableItems = {
            klasa: ['1A', '1C', '1D', '1F', '1G', '1H', '2A', '2C', '2D', '2F', '2H'],
            nauczyciel: ['BAJUK JOANNA', 'BANASZEK IRMINA', 'BODZAK ANDRZEJ', 'BUDZIŃSKA ALEKSANDRA'],
            sala: ['101', '104', '108', '112', '113', '116', '117', '120', 'SG1', 'SG2']
        };
    }
    
    setupEventListeners() {
        // Zmiana typu filtru (klasa/nauczyciel/sala)
        const filterRadios = document.querySelectorAll('input[name="filter-type"]');
        filterRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.updateItemSelector(e.target.value);
            });
        });
        
        // Przycisk ładowania planu
        const loadBtn = document.getElementById('load-btn');
        loadBtn.addEventListener('click', () => {
            this.loadSchedule();
        });
        
        // Enter w selektorze
        const selector = document.getElementById('item-selector');
        selector.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.loadSchedule();
            }
        });
        
        // Zmiana wyboru w selektorze
        selector.addEventListener('change', () => {
            const loadBtn = document.getElementById('load-btn');
            loadBtn.disabled = !selector.value;
        });
    }
    
    updateItemSelector(type) {
        console.log(`🔄 Aktualizacja listy dla typu: ${type}`);
        
        const selector = document.getElementById('item-selector');
        const loadBtn = document.getElementById('load-btn');
        
        // Wyczyść selector
        selector.innerHTML = '<option value="">Wybierz...</option>';
        loadBtn.disabled = true;
        
        if (!this.availableItems || !this.availableItems[type]) {
            console.warn(`⚠️ Brak danych dla typu: ${type}`);
            return;
        }
        
        // Dodaj opcje
        const items = this.availableItems[type];
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            selector.appendChild(option);
        });
        
        console.log(`✅ Załadowano ${items.length} opcji dla typu ${type}`);
    }
    
    async loadSchedule() {
        if (this.loading) {
            console.log('⏳ Już trwa ładowanie...');
            return;
        }
        
        const type = document.querySelector('input[name="filter-type"]:checked')?.value;
        const item = document.getElementById('item-selector').value;
        
        if (!type || !item) {
            this.showError('Wybierz typ i element do wyświetlenia planu.');
            return;
        }
        
        console.log(`📅 Ładowanie planu: ${type} - ${item}`);
        
        this.setLoading(true);
        this.hideError();
        
        try {
            const response = await fetch('/api/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    item: item
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Nieznany błąd API');
            }
            
            console.log('✅ Załadowano plan z API:', data);
            
            this.currentSchedule = data.schedule;
            this.displaySchedule(type, item);
            
        } catch (error) {
            console.error('❌ Błąd ładowania planu:', error);
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
            loadBtn.textContent = 'Ładowanie...';
        } else {
            loadingDiv.classList.add('hidden');
            loadBtn.disabled = false;
            loadBtn.textContent = 'Pokaż plan';
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
    console.log('🌟 Uruchamianie aplikacji planu lekcji ZSEIL');
    new ScheduleApp();
});

// Debug info
console.log('📋 Plan Lekcji ZSEIL - Wersja Flask');
console.log('🔗 GitHub Repository: https://github.com/c14b7/zseil');
console.log('⚡ Powered by Flask + Playwright');