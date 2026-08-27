// Konfiguracja Twojej bazy danych Appwrite
const APPWRITE_CONFIG = {
    e
    collectionId: 'info_up'
};
const APPWRITE_CONFIG = {
    endpoint: 'https://fra.cloud.appwrite.io/v1', 
    projectId: '687abe96000d2d31f914', 
    databaseId: '6a90ac4e002c0ce017c6',
    
    // Dwie osobne kolekcje
    infoCollectionId: 'info_up',
    techCollectionId: 'tech_up'
};

const { Client, Databases, Query } = window.Appwrite;
const client = new Client()
    .setEndpoint(APPWRITE_CONFIG.endpoint)
    .setProject(APPWRITE_CONFIG.projectId);

const databases = new Databases(client);

// ==========================================
// 1. BANNER INFORMACYJNY (STAŁY NAD PLANEM)
// ==========================================
async function loadInfoBanner() {
    const container = document.getElementById('info-banner-container');
    if (!container) return;

    try {
        const response = await databases.listDocuments(
            APPWRITE_CONFIG.databaseId,
            APPWRITE_CONFIG.infoCollectionId,
            [Query.limit(1)]
        );

        if (response.documents.length > 0) {
            const data = response.documents[0];

            // Pobieramy kolory lub stosujemy domyślne akcenty niebieskie
            const bgColor = data.bgColor || 'rgba(30, 58, 138, 0.85)';
            const textColor = data.textColor || '#f8fafc';
            const title = data.title || '';
            const content = data.content || '';
            const icon = data.icon || 'info';
            const linkUrl = data.linkUrl || null;
            const linkText = data.linkText || 'Dowiedz się więcej';

            let html = `
                <div class="info-banner" style="background-color: ${escapeHTML(bgColor)}; color: ${escapeHTML(textColor)};">
                    <div class="info-banner-header">
                        <i data-lucide="${escapeHTML(icon)}"></i>
                        <h3 class="info-banner-title">${escapeHTML(title)}</h3>
                    </div>
                    <p class="info-banner-content">${escapeHTML(content)}</p>
            `;

            if (linkUrl) {
                html += `
                    <a href="${escapeHTML(linkUrl)}" target="_blank" rel="noopener noreferrer" class="info-banner-btn">
                        ${escapeHTML(linkText)}
                        <i data-lucide="external-link" style="width:14px; height:14px;"></i>
                    </a>
                `;
            }

            html += `</div>`;
            container.innerHTML = html;
        }
    } catch (error) {
        console.error('Błąd ładowania bannera informacyjnego:', error);
    }
}

// ==========================================
// 2. BANNER TECHNICZNY (ZAMYKANY NA GÓRZE)
// ==========================================
async function loadTechBanner() {
    const container = document.getElementById('technical-banner-container');
    if (!container) return;

    try {
        const response = await databases.listDocuments(
            APPWRITE_CONFIG.databaseId,
            APPWRITE_CONFIG.techCollectionId,
            [Query.limit(1)]
        );

        if (response.documents.length > 0) {
            const data = response.documents[0];

            const bgColor = data.bgColor || '#dc2626';
            const textColor = data.textColor || '#ffffff';
            const title = data.title || 'Problem techniczny';
            const content = data.content || '';
            const icon = data.icon || 'alert-triangle';

            const html = `
                <div id="tech-banner-element" class="dynamic-tech-banner" style="background-color: ${escapeHTML(bgColor)}; color: ${escapeHTML(textColor)};">
                    <div class="dynamic-tech-content">
                        <i data-lucide="${escapeHTML(icon)}" class="dynamic-tech-icon"></i>
                        <div class="dynamic-tech-text">
                            <strong>${escapeHTML(title)}</strong>
                            <span>${escapeHTML(content)}</span>
                        </div>
                        <button id="close-tech-banner" class="dynamic-tech-close" aria-label="Zamknij">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                </div>
            `;

            container.innerHTML = html;
            document.body.classList.add('banner-visible');

            // Obsługa zamykania
            document.getElementById('close-tech-banner')?.addEventListener('click', () => {
                const bannerEl = document.getElementById('tech-banner-element');
                if (bannerEl) {
                    bannerEl.style.display = 'none';
                    document.body.classList.remove('banner-visible');
                }
            });
        }
    } catch (error) {
        console.error('Błąd ładowania bannera technicznego:', error);
    }
}

// Escapowanie znaków pod kątem bezpieczeństwa
function escapeHTML(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag] || tag));
}

// Inicjalizacja obu bannerów i ikon Lucide
document.addEventListener('DOMContentLoaded', async () => {
    await Promise.all([loadInfoBanner(), loadTechBanner()]);

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
