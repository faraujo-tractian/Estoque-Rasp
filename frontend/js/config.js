// Configuration file
const CONFIG = {
    // API Base URL - adjust this to your backend URL
    API_BASE_URL: window.location.origin + '/api',
    
    // Sync interval in milliseconds (5 minutes)
    SYNC_INTERVAL: 5 * 60 * 1000,
    
    // Toast duration in milliseconds
    TOAST_DURATION: 3000,
    
    // Debounce delay for search in milliseconds
    SEARCH_DEBOUNCE: 300,
    
    // API Endpoints
    ENDPOINTS: {
        ITEMS: '/items',
        SEARCH: '/items/search',
        TRANSACTION: '/transactions',
        HISTORY: '/history',
        SYNC: '/sync'
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

