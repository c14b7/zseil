document.addEventListener('DOMContentLoaded', function() {
    initTechnicalBanner();
});

function initTechnicalBanner() {
    const banner = document.getElementById('technical-issue-banner');
    const closeBtn = document.getElementById('close-banner');
    const body = document.body;
    
    if (!banner) return;
    
    body.classList.add('banner-visible');
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeTechnicalBanner();
        });
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && banner.style.display !== 'none') {
            closeTechnicalBanner();
        }
    });
}

function closeTechnicalBanner() {
    const banner = document.getElementById('technical-issue-banner');
    const body = document.body;
    
    if (banner) {
        banner.style.animation = 'slideUp 0.3s ease-out forwards';
        
        setTimeout(() => {
            banner.style.display = 'none';
            body.classList.remove('banner-visible');
        }, 300);
    }
}

function updateBannerMessage(message) {
    const messageElement = document.getElementById('banner-message');
    if (messageElement) {
        messageElement.textContent = message;
    }
}

function showTechnicalBanner() {
    const banner = document.getElementById('technical-issue-banner');
    const body = document.body;
    
    if (banner) {
        banner.style.display = 'block';
        banner.style.animation = 'slideDown 0.3s ease-out forwards';
        body.classList.add('banner-visible');
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

class ScheduleApp {
    constructor() {
        this.allData = null;
        this.currentSchedule = null;
        this.loading = false;
        
        this.init();
    }
    
    async init() {
        await this.loadDataFromJSON();
        this.populateAllSelectors();
        this.setupEventListeners();
        this.displayMetadata();
        this.applyUrlParams();
    }
    
    async loadDataFromJSON() {
        try {
            this.updateDataStatus('Ładowanie danych z JSON...', 'loading');
            
            const response = await fetch('./data.json');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.allData = await response.json();
            
            this.updateDataStatus('Dane załadowane z JSON', 'success');
            this.enableControls();
            
        } catch (error) {
            console.error('Błąd ładowania danych JSON:', error);
            this.updateDataStatus('Błąd ładowania JSON - używam danych testowych', 'error');
            this.loadFallbackData();
            this.enableControls();
        }
    }
    
    loadFallbackData() {
        this.allData = {
            metadata: {
                scraped_at: new Date().toISOString(),
                source_url: 'http://dane-dane.pl/PLAN',
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
        
        ['1A', '1C', '2A'].forEach(className => {
            this.allData.schedules.klasa[className] = this.generateMockSchedule(className);
        });
    }
    
    generateMockSchedule(itemName) {
        return {
            'monday': [
                [{'subject': 'Błąd ładowania danych', 'teacher': 'Błąd ładowania danych', 'room': '000', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'A. Błąd ładowania danych', 'room': '000', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'M. Błąd ładowania danych', 'room': '000', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'P. Błąd ładowania danych', 'room': '000', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'E. Błąd ładowania danych', 'room': '000', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'tuesday': [
                [{'subject': 'Błąd ładowania danych', 'teacher': 'T. Błąd ładowania danych', 'room': '000', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'J. Błąd ładowania danych', 'room': '000', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'K. Błąd ładowania danych', 'room': '000', 'time': '9:45-10:30', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'R. Błąd ładowania danych', 'room': '000', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'S. Błąd ładowania danych', 'room': '000', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'wednesday': [
                [{'subject': 'Błąd ładowania danych', 'teacher': 'A. Błąd ładowania danych', 'room': '000', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'M. Błąd ładowania danych', 'room': '000', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'J. Błąd ładowania danych', 'room': '000', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'D. Błąd ładowania danych', 'room': '000', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'B. Błąd ładowania danych', 'room': '000', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'thursday': [
                [{'subject': 'Błąd ładowania danych', 'teacher': 'P. Błąd ładowania danych', 'room': '000', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'T. Błąd ładowania danych', 'room': '000', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'K. Błąd ładowania danych', 'room': '000', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'E. Błąd ładowania danych', 'room': '000', 'time': '10:35-11:20', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'J. Błąd ładowania danych', 'room': '000', 'time': '11:35-12:20', 'class': itemName, 'group': ''}],
                [],
                []
            ],
            'friday': [
                [{'subject': 'Błąd ładowania danych', 'teacher': 'M. Błąd ładowania danych', 'room': '000', 'time': '7:10-7:55', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'S. Błąd ładowania danych', 'room': '000', 'time': '8:00-8:45', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'A. Błąd ładowania danych', 'room': '000', 'time': '8:50-9:35', 'class': itemName, 'group': ''}],
                [{'subject': 'Błąd ładowania danych', 'teacher': 'R. Błąd ładowania danych', 'room': '000', 'time': '9:45-10:30', 'class': itemName, 'group': ''}],
                [],
                [],
                []
            ]
        };
    }
    
    enableControls() {
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        
        if (classSelector) classSelector.disabled = false;
        if (teacherSelector) teacherSelector.disabled = false;
        if (roomSelector) roomSelector.disabled = false;
    }
    
    updateDataStatus(message, status = '') {
        const dataInfo = document.getElementById('data-info');
        const dataStatus = document.getElementById('data-status');
        
        if (dataInfo) dataInfo.textContent = message;
        if (dataStatus) {
            dataStatus.className = 'data-status';
            if (status) dataStatus.classList.add(status);
        }
    }
    
    displayMetadata() {
        if (!this.allData || !this.allData.metadata) return;
        
        const metadata = this.allData.metadata;
        const loadedStatus = document.getElementById('data-loaded-status');
        const lastUpdate = document.getElementById('last-update');
        const totalSchedules = document.getElementById('total-schedules');
        
        if (loadedStatus) loadedStatus.textContent = metadata.errors_count === 0 ? 'Wszystkie dane OK' : `${metadata.errors_count} błędów`;
        if (lastUpdate && metadata.scraped_at) {
            lastUpdate.textContent = new Date(metadata.scraped_at).toLocaleString('pl-PL');
        }
        if (totalSchedules) totalSchedules.textContent = metadata.total_schedules_scraped || 0;
    }
    
        setupEventListeners() {
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        const table = document.getElementById('schedule-table');
        
        if (classSelector) {
            classSelector.addEventListener('change', (e) => {
                if (e.target.value) {
                    if (teacherSelector) teacherSelector.value = '';
                    if (roomSelector) roomSelector.value = '';
                    this.updateUrlParam('class', e.target.value);
                    this.loadSchedule();
                }
            });
        }
        
        if (teacherSelector) {
            teacherSelector.addEventListener('change', (e) => {
                if (e.target.value) {
                    if (classSelector) classSelector.value = '';
                    if (roomSelector) roomSelector.value = '';
                    this.updateUrlParam('teacher', e.target.value);
                    this.loadSchedule();
                }
            });
        }
        
        if (roomSelector) {
            roomSelector.addEventListener('change', (e) => {
                if (e.target.value) {
                    if (classSelector) classSelector.value = '';
                    if (teacherSelector) teacherSelector.value = '';
                    this.updateUrlParam('room', e.target.value);
                    this.loadSchedule();
                }
            });
        }

        // Obsługa kliknięć w elementy planu (klasa / nauczyciel / sala)
        if (table) {
            table.addEventListener('click', (e) => {
                const target = e.target.closest('[data-type][data-value]');
                if (!target) return;

                const type = target.dataset.type;
                const value = target.dataset.value;

                if (type === 'klasa' && classSelector) {
                    teacherSelector.value = '';
                    roomSelector.value = '';
                    classSelector.value = value;
                    this.updateUrlParam('class', value);
                    this.loadSchedule();
                } else if (type === 'nauczyciel' && teacherSelector) {
                    classSelector.value = '';
                    roomSelector.value = '';
                    teacherSelector.value = value;
                    this.updateUrlParam('teacher', value);
                    this.loadSchedule();
                } else if (type === 'sala' && roomSelector) {
                    classSelector.value = '';
                    teacherSelector.value = '';
                    roomSelector.value = value;
                    this.updateUrlParam('room', value);
                    this.loadSchedule();
                }
            });
        }
    }

    // Aktualizacja widocznych parametrów w adresie URL
    updateUrlParam(key, value) {
        const url = new URL(window.location.href);
        url.searchParams.delete('class');
        url.searchParams.delete('teacher');
        url.searchParams.delete('room');
        url.searchParams.set(key, value);
        window.history.pushState({}, '', url);
    }

    // Ładowanie planu na podstawie parametrów URL po wejściu na stronę
   applyUrlParams() {
    const params = new URLSearchParams(window.location.search);
    let classParam = params.get('class');
    let teacherParam = params.get('teacher');
    let roomParam = params.get('room');

    // Jeśli brak parametrów w URL, użyj zapisanych ustawień domyślnych
    if (!classParam && !teacherParam && !roomParam) {
        const defaultType = localStorage.getItem('default_type');
        const defaultValue = localStorage.getItem('default_value');

        if (defaultType && defaultValue) {
            if (defaultType === 'class') classParam = defaultValue;
            if (defaultType === 'teacher') teacherParam = defaultValue;
            if (defaultType === 'room') roomParam = defaultValue;
        }
    }

    const classSelector = document.getElementById('class-selector');
    const teacherSelector = document.getElementById('teacher-selector');
    const roomSelector = document.getElementById('room-selector');

    if (classParam && classSelector) {
        classSelector.value = classParam;
    } else if (teacherParam && teacherSelector) {
        teacherSelector.value = teacherParam;
    } else if (roomParam && roomSelector) {
        roomSelector.value = roomParam;
    }

    if (classParam || teacherParam || roomParam) {
        this.loadSchedule();
    }
}
    
    populateAllSelectors() {
        this.populateSelector('class-selector', 'klasa');
        this.populateSelector('teacher-selector', 'nauczyciel');
        this.populateSelector('room-selector', 'sala');
    }
    
    populateSelector(selectorId, type) {
        const selector = document.getElementById(selectorId);
        if (!selector || !this.allData || !this.allData.available_items || !this.allData.available_items[type]) return;
        
        const placeholder = selector.querySelector('option[value=""]');
        selector.innerHTML = '';
        if (placeholder) {
            selector.appendChild(placeholder);
        }
        
        const items = this.allData.available_items[type];
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            
            const hasSchedule = this.allData.schedules && 
                               this.allData.schedules[type] && 
                               this.allData.schedules[type][item];
            
            if (!hasSchedule) {
                option.textContent += ' (brak planu)';
                option.style.color = '#64748b';
            }
            
            selector.appendChild(option);
        });
    }
    
    loadSchedule() {
        if (this.loading) return;
        
        const classSelector = document.getElementById('class-selector');
        const teacherSelector = document.getElementById('teacher-selector');
        const roomSelector = document.getElementById('room-selector');
        
        let type, item;
        
        if (classSelector && classSelector.value) {
            type = 'klasa';
            item = classSelector.value;
        } else if (teacherSelector && teacherSelector.value) {
            type = 'nauczyciel';
            item = teacherSelector.value;
        } else if (roomSelector && roomSelector.value) {
            type = 'sala';
            item = roomSelector.value;
        } else {
            return;
        }
        
        this.setLoading(true);
        this.hideError();
        
        try {
            if (!this.allData || !this.allData.schedules || !this.allData.schedules[type]) {
                throw new Error('Brak danych o planach w załadowanym JSON');
            }
            
            const schedule = this.allData.schedules[type][item];
            
            if (!schedule) {
                throw new Error(`Brak planu dla "${item}" w kategorii "${type}"`);
            }
            
            this.currentSchedule = schedule;
            this.displaySchedule(type, item);
            
        } catch (error) {
            console.error('Błąd ładowania planu z JSON:', error);
            this.showError(`Nie udało się załadować planu dla "${item}". ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    displaySchedule(type, item) {
        const table = document.getElementById('schedule-table');
        const tbody = document.getElementById('schedule-body');
        
        if (!tbody || !table) return;
        tbody.innerHTML = '';
        
        if (!this.currentSchedule) {
            this.showError('Brak danych planu do wyświetlenia.');
            return;
        }
        
        const lessonTimes = [
            '7:45-8:30', '08:35-9:20', '9:25-10:10',
            '10:20-11:05', '11:20-12:05', '12:15-13:00', '13:20-14:05',
            '14:15-15:00', '15:05-15:50', '15:55-16:40', '16:45-17:30',
            '17:35-18:20'
        ];
        
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
        
        let maxLessons = 0;
        days.forEach(day => {
            if (this.currentSchedule[day]) {
                maxLessons = Math.max(maxLessons, this.currentSchedule[day].length);
            }
        });
        
        for (let lessonIndex = 0; lessonIndex < Math.min(maxLessons, 15); lessonIndex++) {
            const row = document.createElement('tr');
            
            const lessonCell = document.createElement('td');
            lessonCell.className = 'lesson-number';
            lessonCell.textContent = `${lessonIndex + 1}. ${lessonTimes[lessonIndex] || ''}`;
            row.appendChild(lessonCell);
            
            days.forEach(day => {
                const cell = document.createElement('td');
                cell.className = 'lesson-cell';
                
                const daySchedule = this.currentSchedule[day];
                if (daySchedule && daySchedule[lessonIndex] && daySchedule[lessonIndex].length > 0) {
                    daySchedule[lessonIndex].forEach((lesson, index) => {
                        if (index > 0) {
                            cell.appendChild(document.createElement('hr'));
                        }
                        
                        const lessonDiv = document.createElement('div');
                        lessonDiv.className = 'lesson';
                        
                        if (lesson.subject) {
                            lessonDiv.setAttribute('data-subject', lesson.subject.toLowerCase());
                        }
                        
                        const subjectDiv = document.createElement('div');
                        subjectDiv.className = 'subject';
                        subjectDiv.textContent = lesson.subject || '';
                        lessonDiv.appendChild(subjectDiv);
                        
                        const detailsDiv = document.createElement('div');
                        detailsDiv.className = 'details';
                        
                        if (type === 'klasa') {
                        if (lesson.teacher) {
                            detailsDiv.innerHTML += `<span class="teacher" data-type="nauczyciel" data-value="${lesson.teacher}">${lesson.teacher}</span><br>`;
                        }
                        if (lesson.room) {
                            detailsDiv.innerHTML += `<span class="room" data-type="sala" data-value="${lesson.room}">sala ${lesson.room}</span>`;
                        }
                    } else if (type === 'nauczyciel') {
                        if (lesson.class) {
                            detailsDiv.innerHTML += `<span class="class" data-type="klasa" data-value="${lesson.class}">${lesson.class}</span><br>`;
                        }
                        if (lesson.room) {
                            detailsDiv.innerHTML += `<span class="room" data-type="sala" data-value="${lesson.room}">sala ${lesson.room}</span>`;
                        }
                    } else if (type === 'sala') {
                        if (lesson.class) {
                            detailsDiv.innerHTML += `<span class="class" data-type="klasa" data-value="${lesson.class}">${lesson.class}</span><br>`;
                        }
                        if (lesson.teacher) {
                            detailsDiv.innerHTML += `<span class="teacher" data-type="nauczyciel" data-value="${lesson.teacher}">${lesson.teacher}</span>`;
                        }
                    }
                        
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
        
        table.classList.remove('hidden');
    }
    
    setLoading(loading) {
        this.loading = loading;
        const loadingDiv = document.getElementById('loading');
        
        if (loadingDiv) {
            if (loading) {
                loadingDiv.classList.remove('hidden');
            } else {
                loadingDiv.classList.add('hidden');
            }
        }
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        const table = document.getElementById('schedule-table');
        
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
        if (table) table.classList.add('hidden');
    }
    
    hideError() {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) errorDiv.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ScheduleApp();
});



