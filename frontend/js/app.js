// Main Application
const App = {
    syncInterval: null,
    currentPage: 'home',
    isLoggedIn: false,

    /**
     * Initialize the application
     */
    async init() {
        console.log('🚀 Iniciando aplicação...');

        // Check if user is already logged in
        this.isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        
        // Initialize sidebar
        this.initSidebar();
        
        // Initialize login
        this.initLogin();

        // Initialize components
        await InventoryPanel.init();
        Modal.init();

        // Check connection
        await this.checkConnection();

        console.log('Aplicacao iniciada com sucesso!');
    },

    /**
     * Initialize login system
     */
    initLogin() {
        const loginForm = document.getElementById('loginForm');
        const logoutNavItem = document.getElementById('logoutNavItem');

        // Update UI based on login state
        this.updateLoginUI();

        // Login form handler
        loginForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const username = document.getElementById('loginUsername').value.trim();
            const password = document.getElementById('loginPassword').value.trim();

            if (!username || !password) {
                this.showToast('Preencha usuario e senha', 'error');
                return;
            }

            // Simple auth (for now - later integrate with backend)
            if (username === 'admin' && password === 'admin') {
                this.login();
                this.showToast('Login realizado com sucesso!', 'success');
                loginForm.reset();
                this.navigateTo('home');
            } else {
                this.showToast('Usuario ou senha incorretos', 'error');
            }
        });

        // Logout handler
        logoutNavItem?.addEventListener('click', () => {
            this.logout();
        });
    },

    /**
     * Perform login
     */
    login() {
        this.isLoggedIn = true;
        localStorage.setItem('isLoggedIn', 'true');
        this.updateLoginUI();
    },

    /**
     * Perform logout
     */
    logout() {
        this.isLoggedIn = false;
        localStorage.removeItem('isLoggedIn');
        this.updateLoginUI();
        this.showToast('👋 Logout realizado com sucesso', 'info');
        this.navigateTo('home');
    },

    /**
     * Update UI based on login state
     */
    updateLoginUI() {
        const loginNavItem = document.getElementById('loginNavItem');
        const adminItems = document.querySelectorAll('.admin-only');

        if (this.isLoggedIn) {
            // Hide login, show admin menu
            loginNavItem?.classList.add('hidden');
            adminItems.forEach(item => item.classList.add('visible'));
        } else {
            // Show login, hide admin menu
            loginNavItem?.classList.remove('hidden');
            adminItems.forEach(item => item.classList.remove('visible'));
        }
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

    },

    /**
     * Navigate to different pages
     */
    navigateTo(page) {
        this.currentPage = page;
        
        // Hide all pages
        const pages = document.querySelectorAll('.page-content');
        pages.forEach(p => p.classList.add('hidden'));
        
        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        
        switch(page) {
            case 'home':
                document.getElementById('homePage')?.classList.remove('hidden');
                pageTitle.textContent = 'Retirada / Devolução';
                break;
                
            case 'login':
                document.getElementById('loginPage')?.classList.remove('hidden');
                pageTitle.textContent = 'Login';
                break;
                
            case 'logout':
                this.logout();
                break;
                
            case 'manage':
                if (!this.isLoggedIn) {
                    this.showToast('Faca login para acessar', 'error');
                    this.navigateTo('login');
                    return;
                }
                document.getElementById('managePage')?.classList.remove('hidden');
                pageTitle.textContent = 'Gerenciar Itens';
                this.showToast('Funcionalidade em desenvolvimento', 'info');
                break;
                
            case 'settings':
                if (!this.isLoggedIn) {
                    this.showToast('Faca login para acessar', 'error');
                    this.navigateTo('login');
                    return;
                }
                document.getElementById('settingsPage')?.classList.remove('hidden');
                pageTitle.textContent = 'Configuracoes';
                this.loadItemsCount();
                break;
        }
    },

    /**
     * Check connection with backend
     */
    async checkConnection() {
        return await API.checkConnection();
    },

    /**
     * Start automatic synchronization with Google Sheets
     */
    startAutoSync() {
        // Don't auto-sync for now, only manual sync
        console.log('Auto-sync disabled. Use manual sync from settings.');
    },

    /**
     * Sync data with Google Sheets
     */
    async syncWithSheets(manual = false) {
        try {
            if (manual) {
                this.showToast('Sincronizando...', 'info');
            }
            
            const result = await API.syncWithSheets();
            console.log('Sincronizacao concluida:', result);
            
            if (manual && result.success) {
                this.showToast(
                    `${result.itens_unicos || 0} itens sincronizados! ` +
                    `(${result.items_novos || 0} novos, ${result.items_atualizados || 0} atualizados)`,
                    'success'
                );
            }
        } catch (error) {
            console.error('Erro na sincronizacao:', error);
            if (manual) {
                this.showToast('Erro na sincronizacao: ' + error.message, 'error');
            }
        }
    },

    /**
     * Load items count for settings page
     */
    async loadItemsCount() {
        try {
            const items = await API.getAllItems();
            const totalItemsEl = document.getElementById('totalItems');
            if (totalItemsEl) {
                totalItemsEl.textContent = items.length;
            }
            
            // Setup sync button
            const btnSync = document.getElementById('btnSync');
            btnSync?.addEventListener('click', async () => {
                await this.syncWithSheets(true);
                await InventoryPanel.loadItems();
            });
            
            // Load Slack settings
            await this.loadSlackSettings();
            
            // Setup save Slack button
            const btnSaveSlack = document.getElementById('btnSaveSlack');
            btnSaveSlack?.addEventListener('click', async () => {
                await this.saveSlackSettings();
            });
        } catch (error) {
            console.error('Error loading items count:', error);
        }
    },

    /**
     * Load Slack settings
     */
    async loadSlackSettings() {
        try {
            const settings = await API.getSlackSettings();
            
            // Update UI
            const slackChannel = document.getElementById('slackChannel');
            const slackEnabled = document.getElementById('slackEnabled');
            const slackStatus = document.getElementById('slackStatus');
            
            if (slackChannel) slackChannel.value = settings.channel || 'C09DV1KQS4C';
            if (slackEnabled) slackEnabled.checked = settings.enabled !== false;
            
            // Update status
            if (slackStatus) {
                if (settings.configured) {
                    slackStatus.innerHTML = '<span style="color: var(--color-success);">✓ Configurado</span>';
                } else {
                    slackStatus.innerHTML = '<span style="color: var(--color-error);">✕ Não configurado</span>';
                }
            }
        } catch (error) {
            console.error('Error loading Slack settings:', error);
        }
    },

    /**
     * Save Slack settings
     */
    async saveSlackSettings() {
        try {
            const slackEnabled = document.getElementById('slackEnabled');
            
            const settings = {
                enabled: slackEnabled?.checked || false
            };
            
            const result = await API.saveSlackSettings(settings);
            
            if (result.success) {
                this.showToast('Configuracoes do Slack salvas!', 'success');
                await this.loadSlackSettings();
            } else {
                this.showToast('Erro ao salvar configuracoes', 'error');
            }
        } catch (error) {
            console.error('Error saving Slack settings:', error);
            this.showToast('Erro ao salvar: ' + error.message, 'error');
        }
    },

    /**
     * Show loading overlay
     */
    showLoading(show) {
        // For now, just log. Can add a loading overlay later if needed.
        if (show) {
            console.log('Loading...');
        } else {
            console.log('Loading complete');
        }
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
        
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, CONFIG.TOAST_DURATION);
    }
};

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

