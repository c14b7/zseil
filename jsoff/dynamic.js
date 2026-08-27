// Konfiguracja Twojej bazy danych Appwrite
const APPWRITE_CONFIG = {
    endpoint: 'https://fra.cloud.appwrite.io/v1', // Lub Twój własny instancja/IP
    projectId: '687abe96000d2d31f914', 
    databaseId: '6a90ac4e002c0ce017c6',
    collectionId: 'info_up'
};

// Inicjalizacja Appwrite
const { Client, Databases, Query } = window.Appwrite;
const client = new Client()
    .setEndpoint(APPWRITE_CONFIG.endpoint)
    .setProject(APPWRITE_CONFIG.projectId);

const databases = new Databases(client);

async function loadDynamicTile() {
    const container = document.getElementById('dynamic-tile-container');
    if (!container) return;

    try {
        // Pobieramy 1 najnowszy rekord
        const response = await databases.listDocuments(
            APPWRITE_CONFIG.databaseId,
            APPWRITE_CONFIG.collectionId,
            [Query.limit(1)]
        );

        // Jeśli jest przynajmniej jeden rekord – generujemy HTML
        if (response.documents.length > 0) {
            const data = response.documents[0];

            const title = data.title || 'Informacja';
            const text = data.text || '';
            const linkUrl = data.linkUrl || null;
            const linkText = data.linkText || 'Zobacz więcej';

            let html = `
                <div class="dynamic-card">
                    <h3 class="dynamic-card-title">${escapeHTML(title)}</h3>
                    <p class="dynamic-card-content">${escapeHTML(text)}</p>
            `;

            if (linkUrl) {
                html += `
                    <a href="${escapeHTML(linkUrl)}" target="_blank" rel="noopener noreferrer" class="dynamic-card-button">
                        ${escapeHTML(linkText)}
                    </a>
                `;
            }

            html += `</div>`;

            container.innerHTML = html;

            // Odświeżamy ikony Lucide, jeśli są na stronie
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    } catch (error) {
        console.error('Błąd Appwrite:', error);
    }
}

// Zabezpieczenie przed XSS
function escapeHTML(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag] || tag));
}

document.addEventListener('DOMContentLoaded', loadDynamicTile);
