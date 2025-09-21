/**
 * Dyżury Nauczycieli ZSEIL - Frontend JavaScript
 * Komunikuje się z backendem Flask przez API endpoints
 */

class DutyApp {
    constructor() {
        this.availableTeachers = null;
        this.currentDuties = null;
        this.loading = false;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Inicjalizacja aplikacji dyżurów nauczycieli');
        
        // Test połączenia z API
        await this.testConnection();
        
        // Pobierz dostępnych nauczycieli
        await this.loadAvailableTeachers();
        
        // Ustaw event listenery
        this.setupEventListeners();
    }
    
    async testConnection() {
        try {
            console.log('🔌 Testowanie połączenia z API dyżurów...');
            const response = await fetch('/api/test-connection');
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Połączenie z API dyżurów działa');
            } else {
                console.warn('⚠️ Problem z połączeniem:', data.message);
            }
        } catch (error) {
            console.error('❌ Błąd połączenia z API dyżurów:', error);
        }
    }
    
    async loadAvailableTeachers() {
        try {
            console.log('📡 Pobieranie dostępnych nauczycieli z API...');
            
            const response = await fetch('/api/available-teachers');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Nieznany błąd API');
            }
            
            this.availableTeachers = data.teachers;
            
            console.log('✅ Załadowano dostępnych nauczycieli:', {
                nauczyciele: this.availableTeachers?.length || 0
            });
            
            // Wypełnij selector
            this.populateTeacherSelector();
            
        } catch (error) {
            console.error('❌ Błąd pobierania dostępnych nauczycieli:', error);
            this.showError('Nie udało się załadować listy nauczycieli. Sprawdź połączenie z serwerem.');
            
            // Załaduj dane przykładowe jako fallback
            this.loadFallbackData();
        }
    }
    
    loadFallbackData() {
        console.log('⚠️ Ładowanie danych przykładowych');
        this.availableTeachers = [
            'BANASZEK IRMINA', 'BODZAK ANDRZEJ', 'BUDZIŃSKA ALEKSANDRA',
            'SCHIFFER PIOTR', 'KOWALSKI JAN', 'NOWAK ANNA'
        ];
        this.populateTeacherSelector();
    }
    
    populateTeacherSelector() {
        const selector = document.getElementById('teacher-selector');
        const loadBtn = document.getElementById('load-btn');
        
        // Wyczyść selector
        selector.innerHTML = '<option value="">Wybierz nauczyciela...</option>';
        loadBtn.disabled = true;
        
        if (!this.availableTeachers) {
            console.warn('⚠️ Brak danych nauczycieli');
            return;
        }
        
        // Dodaj opcje - posortuj alfabetycznie
        const sortedTeachers = [...this.availableTeachers].sort();
        sortedTeachers.forEach(teacher => {
            const option = document.createElement('option');
            option.value = teacher;
            option.textContent = teacher;
            selector.appendChild(option);
        });
        
        console.log(`✅ Załadowano ${sortedTeachers.length} nauczycieli do selectora`);
    }
    
    setupEventListeners() {
        // Przycisk ładowania dyżurów
        const loadBtn = document.getElementById('load-btn');
        loadBtn.addEventListener('click', () => {
            this.loadDuties();
        });
        
        // Enter w selektorze
        const selector = document.getElementById('teacher-selector');
        selector.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.loadDuties();
            }
        });
        
        // Zmiana wyboru w selektorze
        selector.addEventListener('change', () => {
            const loadBtn = document.getElementById('load-btn');
            loadBtn.disabled = !selector.value;
        });
    }
    
    async loadDuties() {
        if (this.loading) {
            console.log('⏳ Już trwa ładowanie...');
            return;
        }
        
        const teacher = document.getElementById('teacher-selector').value;
        
        if (!teacher) {
            this.showError('Wybierz nauczyciela do wyświetlenia dyżurów.');
            return;
        }
        
        console.log(`👮‍♂️ Ładowanie dyżurów: ${teacher}`);
        
        this.setLoading(true);
        this.hideError();
        
        try {
            const response = await fetch('/api/duty', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    teacher: teacher
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Nieznany błąd API');
            }
            
            console.log('✅ Załadowano dyżury z API:', data);
            
            this.currentDuties = data.duties;
            this.displayDuties(teacher);
            
        } catch (error) {
            console.error('❌ Błąd ładowania dyżurów:', error);
            this.showError(`Nie udało się załadować dyżurów dla "${teacher}". ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    displayDuties(teacher) {
        console.log('🎨 Wyświetlanie dyżurów nauczyciela');
        
        // Pokaż informację o nauczycielu
        const teacherInfo = document.getElementById('teacher-info');
        const selectedTeacher = document.getElementById('selected-teacher');
        const dutySchedule = document.getElementById('duty-schedule');
        
        selectedTeacher.textContent = teacher;
        teacherInfo.classList.remove('hidden');
        
        if (!this.currentDuties) {
            this.showError('Brak danych dyżurów do wyświetlenia.');
            return;
        }
        
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        const dayNames = {
            'monday': 'Poniedziałek',
            'tuesday': 'Wtorek',
            'wednesday': 'Środa',
            'thursday': 'Czwartek',
            'friday': 'Piątek'
        };
        
        // Wyczyść poprzednie dyżury
        days.forEach(day => {
            const dayColumn = document.querySelector(`[data-day="${day}"] .duties-list`);
            if (dayColumn) {
                dayColumn.innerHTML = '';
            }
        });
        
        let totalDuties = 0;
        
        // Wypełnij dyżury dla każdego dnia
        days.forEach(day => {
            const dayColumn = document.querySelector(`[data-day="${day}"] .duties-list`);
            const dayDuties = this.currentDuties[day] || [];
            
            if (dayDuties.length === 0) {
                // Brak dyżurów w tym dniu
                const noDutiesDiv = document.createElement('div');
                noDutiesDiv.className = 'no-duties';
                noDutiesDiv.textContent = 'Brak dyżurów';
                dayColumn.appendChild(noDutiesDiv);
            } else {
                // Dodaj dyżury
                dayDuties.forEach(duty => {
                    const dutyDiv = this.createDutyElement(duty);
                    dayColumn.appendChild(dutyDiv);
                    totalDuties++;
                });
            }
        });
        
        // Pokaż harmonogram
        dutySchedule.classList.remove('hidden');
        
        console.log(`✅ Wyświetlono ${totalDuties} dyżurów dla nauczyciela: ${teacher}`);
    }
    
    createDutyElement(duty) {
        const dutyDiv = document.createElement('div');
        dutyDiv.className = 'duty-item';
        
        // Czas dyżuru
        const timeDiv = document.createElement('div');
        timeDiv.className = 'duty-time';
        timeDiv.textContent = duty.time || '';
        dutyDiv.appendChild(timeDiv);
        
        // Strefa dyżuru
        const zoneDiv = document.createElement('div');
        zoneDiv.className = 'duty-zone';
        zoneDiv.textContent = duty.zone || '';
        dutyDiv.appendChild(zoneDiv);
        
        // Szczegóły dyżuru
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'duty-details';
        
        const durationSpan = document.createElement('span');
        durationSpan.className = 'duty-duration';
        durationSpan.textContent = duty.duration || '';
        
        const lessonSpan = document.createElement('span');
        lessonSpan.className = 'duty-lesson';
        lessonSpan.textContent = duty.lesson_hour ? `Lekcja ${duty.lesson_hour}` : '';
        
        detailsDiv.appendChild(durationSpan);
        detailsDiv.appendChild(lessonSpan);
        dutyDiv.appendChild(detailsDiv);
        
        return dutyDiv;
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
            loadBtn.textContent = 'Pokaż dyżury';
        }
    }
    
    showError(message) {
        console.error('💥 Błąd:', message);
        
        const errorDiv = document.getElementById('error-message');
        const dutySchedule = document.getElementById('duty-schedule');
        const teacherInfo = document.getElementById('teacher-info');
        
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        dutySchedule.classList.add('hidden');
        teacherInfo.classList.add('hidden');
    }
    
    hideError() {
        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.add('hidden');
    }
}

// Uruchom aplikację po załadowaniu DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌟 Uruchamianie aplikacji dyżurów nauczycieli ZSEIL');
    new DutyApp();
});

// Debug info
console.log('👮‍♂️ Dyżury Nauczycieli ZSEIL - Wersja Flask');
console.log('🔗 GitHub Repository: https://github.com/c14b7/zsei');
console.log('⚡ Powered by Flask + Playwright');