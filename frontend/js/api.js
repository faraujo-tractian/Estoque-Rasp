// API Service - handles all backend communication
const API = {
    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Erro na requisição');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Search items by name
     */
    async searchItems(query) {
        if (!query || query.trim().length < 2) {
            return [];
        }
        
        return this.request(`${CONFIG.ENDPOINTS.SEARCH}?q=${encodeURIComponent(query)}`);
    },

    /**
     * Get all items
     */
    async getAllItems() {
        return this.request(CONFIG.ENDPOINTS.ITEMS);
    },

    /**
     * Get item by ID
     */
    async getItemById(id) {
        return this.request(`${CONFIG.ENDPOINTS.ITEMS}/${id}`);
    },

    /**
     * Create a transaction (retirada or devolucao)
     */
    async createTransaction(data) {
        return this.request(CONFIG.ENDPOINTS.TRANSACTION, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * Get transaction history
     */
    async getHistory(limit = 50) {
        return this.request(`${CONFIG.ENDPOINTS.HISTORY}?limit=${limit}`);
    },

    /**
     * Sync with Google Sheets
     */
    async syncWithSheets() {
        return this.request(CONFIG.ENDPOINTS.SYNC, {
            method: 'POST',
        });
    },

    /**
     * Check connection status
     */
    async checkConnection() {
        try {
            await this.request('/health');
            return true;
        } catch (error) {
            return false;
        }
    },

    /**
     * Get Slack settings
     */
    async getSlackSettings() {
        return this.request(CONFIG.ENDPOINTS.SLACK_SETTINGS);
    },

    /**
     * Save Slack settings
     */
    async saveSlackSettings(settings) {
        return this.request(CONFIG.ENDPOINTS.SLACK_SETTINGS, {
            method: 'POST',
            body: JSON.stringify(settings),
        });
    }
};

