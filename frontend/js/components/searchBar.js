// Search Bar Component - Professional Version
const SearchBar = {
    searchInput: null,
    searchResults: null,
    searchResultsContainer: null,
    searchClear: null,
    debounceTimer: null,
    currentItems: [],
    allItems: [],
    currentFilter: 'all',
    currentSort: 'nome',

    async init() {
        this.searchInput = document.getElementById('itemSearch');
        this.searchResults = document.getElementById('searchResults');
        this.searchResultsContainer = document.getElementById('searchResultsContainer');
        this.searchClear = document.getElementById('searchClear');
        
        // Load all items
        await this.loadAllItems();
        
        // Add event listeners
        this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        this.searchClear.addEventListener('click', () => this.clearSearch());
        
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => this.handleFilter(e));
        });
        
        // Sort
        document.getElementById('sortBy')?.addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.updateResults();
        });
    },
    
    async loadAllItems() {
        try {
            this.allItems = await API.getAllItems();
            document.getElementById('searchStats').innerHTML = `
                <span class="stat-badge">${this.allItems.length} itens</span>
            `;
        } catch (error) {
            console.error('Error loading items:', error);
        }
    },

    handleSearch(event) {
        const query = event.target.value;
        
        // Show/hide clear button
        this.searchClear.style.display = query ? 'block' : 'none';

        // Clear previous timer
        clearTimeout(this.debounceTimer);

        // Debounce search
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, CONFIG.SEARCH_DEBOUNCE);
    },
    
    performSearch(query) {
        if (query.trim().length === 0) {
            this.hideResults();
            return;
        }
        
        // Filter items
        const queryLower = query.toLowerCase();
        this.currentItems = this.allItems.filter(item => {
            const matchesQuery = item.nome.toLowerCase().includes(queryLower);
            const matchesFilter = this.currentFilter === 'all' || item.aba_origem === this.currentFilter;
            return matchesQuery && matchesFilter;
        });
        
        this.updateResults();
    },
    
    handleFilter(event) {
        const chip = event.target;
        const filter = chip.dataset.filter;
        
        // Update active state
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        
        this.currentFilter = filter;
        this.performSearch(this.searchInput.value);
    },
    
    clearSearch() {
        this.searchInput.value = '';
        this.searchClear.style.display = 'none';
        this.hideResults();
    },
    
    updateResults() {
        if (this.currentItems.length === 0 && this.searchInput.value.trim().length > 0) {
            this.displayNoResults();
            return;
        }
        
        // Sort items
        this.sortItems();
        
        // Display
        this.displayResults(this.currentItems);
    },
    
    sortItems() {
        this.currentItems.sort((a, b) => {
            switch (this.currentSort) {
                case 'nome':
                    return a.nome.localeCompare(b.nome);
                case 'disponivel':
                    return b.quantidade_disponivel - a.quantidade_disponivel;
                case 'total':
                    return (b.quantidade_total || 0) - (a.quantidade_total || 0);
                default:
                    return 0;
            }
        });
    },

    displayResults(items) {
        // Update count
        document.getElementById('resultsCount').textContent = `${items.length} resultado${items.length !== 1 ? 's' : ''}`;
        
        // Show container
        this.searchResultsContainer.classList.remove('hidden');
        
        // Render cards
        this.searchResults.innerHTML = items.map(item => {
            const isLowStock = item.quantidade_disponivel <= item.estoque_minimo;
            const badgeClass = item.aba_origem ? item.aba_origem.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') : 'produto';
            
            return `
                <div class="result-card" data-item-id="${item.id}">
                    <div class="result-card-header">
                        <div class="result-card-title">${item.nome}</div>
                        <span class="result-badge ${badgeClass}">${item.aba_origem || 'Produto'}</span>
                    </div>
                    <div class="result-card-info">
                        <div class="result-info-item">
                            <div class="result-info-value">${item.quantidade_total || item.quantidade_disponivel}</div>
                            <div class="result-info-label">Total</div>
                        </div>
                        <div class="result-info-item">
                            <div class="result-info-value ${isLowStock ? 'low' : ''}">${item.quantidade_disponivel}</div>
                            <div class="result-info-label">Disponível</div>
                        </div>
                        <div class="result-info-item">
                            <div class="result-info-value">${item.quantidade_em_uso || 0}</div>
                            <div class="result-info-label">Em Uso</div>
                        </div>
                    </div>
                    ${item.localizacao ? `
                        <div class="result-card-location">
                            📍 ${item.localizacao}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        // Add click handlers
        this.searchResults.querySelectorAll('.result-card').forEach(card => {
            card.addEventListener('click', () => {
                const itemId = card.dataset.itemId;
                const item = this.currentItems.find(i => i.id == itemId);
                if (item) {
                    this.selectItem(item);
                }
            });
        });
    },
    
    displayNoResults() {
        this.searchResultsContainer.classList.remove('hidden');
        document.getElementById('resultsCount').textContent = '0 resultados';
        this.searchResults.innerHTML = `
            <div class="search-no-results">
                <div class="search-no-results-icon">🔍</div>
                <p><strong>Nenhum item encontrado</strong></p>
                <p>Tente usar outros termos de busca ou filtros</p>
            </div>
        `;
    },

    selectItem(item) {
        // Update selected item in main app
        ItemCard.display(item);
        
        // Clear search and hide results
        this.searchInput.value = '';
        this.hideResults();
    },

    hideResults() {
        this.searchResultsContainer.classList.add('hidden');
        this.searchResults.innerHTML = '';
        document.getElementById('resultsCount').textContent = '0 resultados';
    }
};

