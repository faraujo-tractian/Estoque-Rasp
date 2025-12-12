// Search Bar Component
const SearchBar = {
    searchInput: null,
    searchResults: null,
    debounceTimer: null,
    currentItems: [],

    init() {
        this.searchInput = document.getElementById('itemSearch');
        this.searchResults = document.getElementById('searchResults');

        // Add event listeners
        this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        
        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.searchResults.contains(e.target)) {
                this.hideResults();
            }
        });
    },

    handleSearch(event) {
        const query = event.target.value;

        // Clear previous timer
        clearTimeout(this.debounceTimer);

        // Debounce search
        this.debounceTimer = setTimeout(async () => {
            if (query.trim().length < 2) {
                this.hideResults();
                return;
            }

            try {
                const items = await API.searchItems(query);
                this.displayResults(items);
            } catch (error) {
                console.error('Search error:', error);
                App.showToast('Erro ao buscar itens', 'error');
            }
        }, CONFIG.SEARCH_DEBOUNCE);
    },

    displayResults(items) {
        this.currentItems = items;

        if (items.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-no-results">
                    Nenhum item encontrado
                </div>
            `;
            this.searchResults.classList.remove('hidden');
            return;
        }

        this.searchResults.innerHTML = items.map(item => `
            <div class="search-result-item" data-item-id="${item.id}">
                <div class="search-result-name">${item.nome}</div>
                <div class="search-result-info">
                    ${item.categoria || ''} • 
                    Disponível: ${item.quantidade_disponivel} un
                </div>
            </div>
        `).join('');

        // Add click handlers
        this.searchResults.querySelectorAll('.search-result-item').forEach(element => {
            element.addEventListener('click', () => {
                const itemId = element.dataset.itemId;
                const item = this.currentItems.find(i => i.id == itemId);
                if (item) {
                    this.selectItem(item);
                }
            });
        });

        this.searchResults.classList.remove('hidden');
    },

    selectItem(item) {
        // Update selected item in main app
        ItemCard.display(item);
        
        // Clear search and hide results
        this.searchInput.value = '';
        this.hideResults();
    },

    hideResults() {
        this.searchResults.classList.add('hidden');
        this.searchResults.innerHTML = '';
    }
};

