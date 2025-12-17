// Inventory Panel Component - List View with Real-time Filtering
const InventoryPanel = {
    allItems: [],
    filteredItems: [],
    selectedItem: null,
    currentFilter: 'all',
    searchQuery: '',
    debounceTimer: null,

    async init() {
        console.log('Initializing Inventory Panel...');
        
        // Load all items
        await this.loadItems();
        
        // Setup search
        const searchInput = document.getElementById('itemSearch');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        
        // Setup filters
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.handleFilter(e.target.dataset.filter));
        });
        
        console.log('Inventory Panel initialized!');
    },

    async loadItems() {
        try {
            this.allItems = await API.getAllItems();
            this.filteredItems = [...this.allItems];
            this.updateItemsCount();
            this.renderItemsList();
        } catch (error) {
            console.error('Error loading items:', error);
            document.getElementById('itemsList').innerHTML = `
                <div class="items-loading">
                    <p style="color: var(--color-danger);">❌ Erro ao carregar itens</p>
                    <button onclick="location.reload()" class="btn btn-secondary">Recarregar</button>
                </div>
            `;
        }
    },

    handleSearch(query) {
        this.searchQuery = query.toLowerCase();
        
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.filterItems();
        }, 200);
    },

    handleFilter(filter) {
        this.currentFilter = filter;
        
        // Update active tab
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.filter === filter);
        });
        
        this.filterItems();
    },

    filterItems() {
        this.filteredItems = this.allItems.filter(item => {
            // Filter by search query
            const matchesSearch = !this.searchQuery || 
                item.nome.toLowerCase().includes(this.searchQuery) ||
                (item.codigos_originais || '').toLowerCase().includes(this.searchQuery);
            
            // Filter by category
            const matchesFilter = this.currentFilter === 'all' || 
                item.aba_origem === this.currentFilter;
            
            return matchesSearch && matchesFilter;
        });
        
        this.updateItemsCount();
        this.renderItemsList();
    },

    updateItemsCount() {
        const count = this.filteredItems.length;
        const itemsCountEl = document.getElementById('itemsCount');
        if (itemsCountEl) {
            itemsCountEl.textContent = `${count} ${count === 1 ? 'item' : 'itens'}`;
        }
    },

    renderItemsList() {
        const listEl = document.getElementById('itemsList');
        
        if (this.filteredItems.length === 0) {
            listEl.innerHTML = `
                <div class="items-loading">
                    <div style="font-size: 3rem; opacity: 0.3;">🔍</div>
                    <p style="color: var(--color-text-muted);">Nenhum item encontrado</p>
                </div>
            `;
            return;
        }
        
        listEl.innerHTML = this.filteredItems.map(item => {
            const totalItems = item.quantidade_total || item.quantidade_disponivel;
            
            return `
                <div class="item-row ${this.selectedItem?.id === item.id ? 'selected' : ''}" data-item-id="${item.id}">
                    <div class="item-row-header">
                        <div class="item-row-name">${item.nome}</div>
                        <div class="item-row-badge">${item.aba_origem || 'Produto'}</div>
                    </div>
                    <div class="item-row-meta">
                        <div class="item-row-stat">
                            <span>📦</span>
                            <span>${item.quantidade_disponivel}/${totalItems}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add click handlers
        listEl.querySelectorAll('.item-row').forEach(row => {
            row.addEventListener('click', () => {
                const itemId = parseInt(row.dataset.itemId);
                const item = this.filteredItems.find(i => i.id === itemId);
                if (item) {
                    this.selectItem(item);
                }
            });
        });
    },

    getItemIcon(aba) {
        switch(aba) {
            case 'Mecânica': return '🔧';
            case 'Eletrônica': return '⚡';
            case 'Produto': return '📦';
            default: return '📦';
        }
    },

    selectItem(item) {
        this.selectedItem = item;
        
        // Update selected state in list
        document.querySelectorAll('.item-row').forEach(row => {
            row.classList.toggle('selected', parseInt(row.dataset.itemId) === item.id);
        });
        
        // Hide empty state
        const emptyState = document.querySelector('.empty-state');
        if (emptyState) emptyState.style.display = 'none';
        
        // Render item details and controls
        this.renderItemDetails(item);
        
        // Scroll to top of details
        const detailPanel = document.querySelector('.detail-panel');
        if (detailPanel) detailPanel.scrollTop = 0;
    },

    renderItemDetails(item) {
        const totalItems = item.quantidade_total || item.quantidade_disponivel;
        const emUso = item.quantidade_em_uso || 0;
        const codigos = item.codigos_originais ? item.codigos_originais.split(',').slice(0, 3) : [];
        const abaOrigem = item.aba_origem || 'Produto';
        const usagePercent = totalItems > 0 ? Math.round((emUso / totalItems) * 100) : 0;

        // Render item info
        document.getElementById('selectedItemCard').innerHTML = `
            <div class="detail-header">
                <div class="detail-title-row">
                    <h2 class="detail-title">${item.nome}</h2>
                    <span class="detail-badge">${abaOrigem}</span>
                </div>
                ${item.categoria ? `
                    <div class="detail-subtitle">
                        <span>📂</span>
                        <span>${item.categoria}</span>
                    </div>
                ` : ''}
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total</div>
                    <div class="stat-value">${totalItems}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Disponível</div>
                    <div class="stat-value">${item.quantidade_disponivel}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Em Uso</div>
                    <div class="stat-value">${emUso}</div>
                </div>
            </div>
            
            ${item.localizacao || codigos.length > 0 ? `
                <div class="meta-section">
                    ${item.localizacao ? `
                        <div class="meta-row">
                            <div class="meta-label">
                                <span>📍</span>
                                <span>Localização</span>
                            </div>
                            <div class="meta-value">${item.localizacao}</div>
                        </div>
                    ` : ''}
                    ${codigos.length > 0 ? `
                        <div class="meta-row">
                            <div class="meta-label">
                                <span>🏷️</span>
                                <span>Códigos</span>
                            </div>
                            <div class="meta-value">${codigos.slice(0, 2).join(', ')}${codigos.length > 2 ? ` +${codigos.length - 2}` : ''}</div>
                        </div>
                    ` : ''}
                    <div class="meta-row">
                        <div class="meta-label">
                            <span>📊</span>
                            <span>Taxa de Uso</span>
                        </div>
                        <div class="meta-value">${usagePercent}%</div>
                    </div>
                </div>
            ` : ''}
            
        `;
        
        // Render action controls
        document.getElementById('itemDetailsContent').innerHTML = `
            <!-- User Input Section -->
            <div class="user-section">
                <div class="section-label">
                    <span>👤</span>
                    <span>Seu Nome</span>
                </div>
                <input 
                    type="text" 
                    id="userName" 
                    class="input-field" 
                    placeholder="Digite seu nome completo"
                    value="${localStorage.getItem('userName') || ''}"
                >
            </div>

            <!-- Quantity Controls -->
            <div class="quantity-section">
                <div class="section-label">
                    <span>🔢</span>
                    <span>Quantidade</span>
                </div>
                <div class="quantity-controls">
                    <button class="btn-quantity" id="btnDecrease">−</button>
                    <input 
                        type="number" 
                        id="quantity" 
                        class="quantity-display" 
                        value="1" 
                        min="1"
                        readonly
                    >
                    <button class="btn-quantity" id="btnIncrease">+</button>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="action-buttons">
                <button class="btn btn-danger" id="btnRetirar">
                    <span class="btn-icon">📤</span>
                    <span>Retirar</span>
                </button>
                <button class="btn btn-success" id="btnDevolver">
                    <span class="btn-icon">📥</span>
                    <span>Devolver</span>
                </button>
            </div>
        `;
        
        // Re-attach event listeners after rendering
        document.getElementById('btnIncrease')?.addEventListener('click', () => this.changeQuantity(1));
        document.getElementById('btnDecrease')?.addEventListener('click', () => this.changeQuantity(-1));
        document.getElementById('btnRetirar')?.addEventListener('click', () => this.handleRetirada());
        document.getElementById('btnDevolver')?.addEventListener('click', () => this.handleDevolucao());
        
        // Save user name on change
        document.getElementById('userName')?.addEventListener('blur', (e) => {
            if (e.target.value.trim()) {
                localStorage.setItem('userName', e.target.value.trim());
            }
        });
    },

    changeQuantity(delta) {
        const input = document.getElementById('quantity');
        const current = parseInt(input.value) || 1;
        const newValue = Math.max(1, current + delta);
        input.value = newValue;
    },

    async handleRetirada() {
        if (!this.selectedItem) {
            App.showToast('Selecione um item primeiro', 'warning');
            return;
        }

        const userName = document.getElementById('userName').value.trim();
        const quantity = parseInt(document.getElementById('quantity').value);

        if (!userName) {
            App.showToast('Digite seu nome', 'warning');
            document.getElementById('userName').focus();
            return;
        }

        if (quantity > this.selectedItem.quantidade_disponivel) {
            App.showToast('Quantidade indisponível em estoque!', 'error');
            return;
        }

        // Show custom confirmation modal
        const confirmed = await this.showConfirmModal(
            'Confirmar Retirada',
            `Deseja retirar ${quantity} unidade(s) de <strong>${this.selectedItem.nome}</strong>?`,
            'Confirmar',
            'Cancelar'
        );

        if (!confirmed) {
            return;
        }

        try {
            App.showLoading(true);

            const response = await API.createTransaction({
                tipo: 'retirada',
                item_id: this.selectedItem.id,
                quantidade: quantity,
                nome_pessoa: userName
            });

            App.showToast(`Retirada realizada com sucesso!`, 'success');

            // Update item
            this.selectedItem.quantidade_disponivel = response.novo_saldo;
            this.selectedItem.quantidade_em_uso = (this.selectedItem.quantidade_em_uso || 0) + quantity;
            
            // Refresh display
            this.renderItemDetails(this.selectedItem);
            this.renderItemsList();
            
            // Reset quantity
            document.getElementById('quantity').value = 1;

        } catch (error) {
            App.showToast(`Erro: ${error.message}`, 'error');
        } finally {
            App.showLoading(false);
        }
    },

    async handleDevolucao() {
        if (!this.selectedItem) {
            App.showToast('Selecione um item primeiro', 'warning');
            return;
        }

        const userName = document.getElementById('userName').value.trim();
        const quantity = parseInt(document.getElementById('quantity').value);

        if (!userName) {
            App.showToast('Digite seu nome', 'warning');
            document.getElementById('userName').focus();
            return;
        }

        // Show custom confirmation modal
        const confirmed = await this.showConfirmModal(
            'Confirmar Devolução',
            `Deseja devolver ${quantity} unidade(s) de <strong>${this.selectedItem.nome}</strong>?`,
            'Confirmar',
            'Cancelar'
        );

        if (!confirmed) {
            return;
        }

        try {
            App.showLoading(true);

            const response = await API.createTransaction({
                tipo: 'devolucao',
                item_id: this.selectedItem.id,
                quantidade: quantity,
                nome_pessoa: userName
            });

            App.showToast(`Devolução realizada com sucesso!`, 'success');

            // Update item
            this.selectedItem.quantidade_disponivel = response.novo_saldo;
            this.selectedItem.quantidade_em_uso = Math.max(0, (this.selectedItem.quantidade_em_uso || 0) - quantity);
            
            // Refresh display
            this.renderItemDetails(this.selectedItem);
            this.renderItemsList();
            
            // Reset quantity
            document.getElementById('quantity').value = 1;

        } catch (error) {
            App.showToast(`Erro: ${error.message}`, 'error');
        } finally {
            App.showLoading(false);
        }
    },

    /**
     * Show custom confirmation modal
     */
    showConfirmModal(title, message, confirmText = 'Confirmar', cancelText = 'Cancelar') {
        return new Promise((resolve) => {
            const modal = document.getElementById('modal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            const modalConfirm = document.getElementById('modalConfirm');
            const modalCancel = document.getElementById('modalCancel');
            
            if (!modal || !modalTitle || !modalBody || !modalConfirm || !modalCancel) {
                // Fallback to browser confirm if modal not found
                resolve(confirm(message));
                return;
            }
            
            // Set content
            modalTitle.textContent = title;
            modalBody.innerHTML = `<p style="font-size: 1rem; line-height: 1.6;">${message}</p>`;
            modalConfirm.textContent = confirmText;
            modalCancel.textContent = cancelText;
            
            // Show modal
            modal.classList.add('active');
            
            // Handle confirm
            const handleConfirm = () => {
                modal.classList.remove('active');
                cleanup();
                resolve(true);
            };
            
            // Handle cancel
            const handleCancel = () => {
                modal.classList.remove('active');
                cleanup();
                resolve(false);
            };
            
            // Cleanup listeners
            const cleanup = () => {
                modalConfirm.removeEventListener('click', handleConfirm);
                modalCancel.removeEventListener('click', handleCancel);
            };
            
            // Add listeners
            modalConfirm.addEventListener('click', handleConfirm);
            modalCancel.addEventListener('click', handleCancel);
        });
    }
};

