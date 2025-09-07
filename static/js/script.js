document.addEventListener('DOMContentLoaded', async () => {
    
    const languageSelect = document.getElementById('language-select');
    let translations = {}; // This will store all our translations

    // Fetch the translations file and store it
    try {
        const response = await fetch("/static/js/translations.json");
        translations = await response.json();
    } catch (error) {
        console.error("Could not load translations:", error);
        return; // Stop if translations can't be loaded
    }

    /**
     * Translates the page to the given language.
     * @param {string} language - The language code (e.g., 'en', 'hi').
     */
    const translatePage = (language) => {
        const languageTranslations = translations[language];
        if (!languageTranslations) {
            console.warn(`No translations found for language: ${language}`);
            return;
        }

        document.querySelectorAll('[data-translate-key]').forEach(element => {
            const key = element.dataset.translateKey;
            const translation = languageTranslations[key];

            if (translation) {
                if (element.placeholder) {
                    element.placeholder = translation;
                } else {
                    element.textContent = translation;
                }
            } else {
                console.warn(`No translation found for key: ${key} in language: ${language}`);
            }
        });
    };

    // Event listener for the language dropdown
    languageSelect.addEventListener('change', (event) => {
        translatePage(event.target.value);
    });

    // Translate the page to English by default when it loads
    translatePage('en');
});