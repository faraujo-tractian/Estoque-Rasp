// Main Application
const App = {
    syncInterval: null,
    currentPage: 'home',

    /**
     * Initialize the application
     */
    async init() {
        console.log('🚀 Iniciando aplicação...');

        // Initialize sidebar
        this.initSidebar();

        // Initialize components
        SearchBar.init();
        ItemCard.init();
        Modal.init();

        // Check connection
        await this.checkConnection();

        // Start auto-sync
        this.startAutoSync();

        // Load saved user name from localStorage
        const savedName = localStorage.getItem('userName');
        if (savedName) {
            document.getElementById('userName').value = savedName;
        }

        // Save user name on change
        document.getElementById('userName').addEventListener('blur', (e) => {
            if (e.target.value.trim()) {
                localStorage.setItem('userName', e.target.value.trim());
            }
        });

        console.log('✅ Aplicação iniciada com sucesso!');
    },

    /**
     * Initialize sidebar navigation
     */
    initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const navItems = document.querySelectorAll('.nav-item');

        // Toggle sidebar (desktop)
        sidebarToggle?.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });

        // Toggle sidebar (mobile)
        mobileMenuToggle?.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
        });

        // Navigation
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                
                // Update active state
                navItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                // Navigate to page
                this.navigateTo(page);
                
                // Close mobile menu
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('mobile-open');
                }
            });
        });

        // Set home as active by default
        navItems[0]?.classList.add('active');
    },

    /**
     * Navigate to different pages
     */
    navigateTo(page) {
        this.currentPage = page;
        
        // Hide all sections first
        document.getElementById('quickStats')?.classList.add('hidden');
        
        switch(page) {
            case 'home':
                // Show main functionality (always visible)
                break;
                
            case 'dashboard':
                this.showToast('Dashboard em desenvolvimento', 'info');
                document.getElementById('quickStats')?.classList.remove('hidden');
                break;
                
            case 'items':
                this.showToast('Gerenciamento de itens em desenvolvimento', 'info');
                break;
                
            case 'reports':
                this.showToast('Relatórios em desenvolvimento', 'info');
                break;
                
            case 'history':
                Modal.open();
                break;
                
            case 'settings':
                this.showToast('Configurações em desenvolvimento', 'info');
                break;
        }
    },

    /**
     * Check connection with backend
     */
    async checkConnection() {
        const isOnline = await API.checkConnection();
        const statusIndicator = document.getElementById('syncStatus');
        const statusText = document.getElementById('syncText');

        if (isOnline) {
            statusIndicator.className = 'status-indicator status-online';
            statusText.textContent = 'Online';
        } else {
            statusIndicator.className = 'status-indicator status-offline';
            statusText.textContent = 'Offline';
        }

        return isOnline;
    },

    /**
     * Start automatic synchronization with Google Sheets
     */
    startAutoSync() {
        // Initial sync
        this.syncWithSheets();

        // Periodic sync
        this.syncInterval = setInterval(() => {
            this.syncWithSheets();
        }, CONFIG.SYNC_INTERVAL);
    },

    /**
     * Sync data with Google Sheets
     */
    async syncWithSheets() {
        try {
            await API.syncWithSheets();
            console.log('✅ Sincronização concluída');
            await this.checkConnection();
        } catch (error) {
            console.error('❌ Erro na sincronização:', error);
        }
    },

    /**
     * Show loading overlay
     */
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');

        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.remove('hidden');

        // Auto hide after duration
        setTimeout(() => {
            toast.classList.add('hidden');
        }, CONFIG.TOAST_DURATION);
    }
};

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

