document.addEventListener('DOMContentLoaded', async () => {
    const typeSelector = document.getElementById('settings-selector');
    const valueSelector = document.getElementById('default-selector');

    let allData = null;

    // Pobranie danych z data.json do wypełnienia drugiego selektora
    try {
        const response = await fetch('./data.json');
        if (response.ok) {
            allData = await response.json();
        }
    } catch (e) {
        console.error('Błąd wczytywania danych:', e);
    }

    // Mapowanie wartości selektora na klucze w data.json
    const typeMap = {
        'class': 'klasa',
        'teacher': 'nauczyciel',
        'room': 'sala'
    };

    // Funkcja wypełniająca listę wartości na podstawie wybranego typu
    function populateValueSelector(selectedType, selectedValue = '') {
        valueSelector.innerHTML = '<option value="">Wybierz...</option>';

        const jsonKey = typeMap[selectedType];
        if (!allData || !allData.available_items || !allData.available_items[jsonKey]) {
            return;
        }

        const items = allData.available_items[jsonKey];
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            if (item === selectedValue) {
                option.selected = true;
            }
            valueSelector.appendChild(option);
        });
    }

    // Odczyt z localStorage przy inicjalizacji
    const savedType = localStorage.getItem('default_type') || 'class';
    const savedValue = localStorage.getItem('default_value') || '';

    typeSelector.value = savedType;
    populateValueSelector(savedType, savedValue);

    // Reakcja na zmianę kategorii (Klasa / Sala / Nauczyciel)
    typeSelector.addEventListener('change', (e) => {
        const newType = e.target.value;
        localStorage.setItem('default_type', newType);
        localStorage.removeItem('default_value'); // reset wartości po zmianie typu
        populateValueSelector(newType);
    });

    // Reakcja na zmianę konkretnej wartości
    valueSelector.addEventListener('change', (e) => {
        const newValue = e.target.value;
        if (newValue) {
            localStorage.setItem('default_value', newValue);
        } else {
            localStorage.removeItem('default_value');
        }
    });
});