// Item Card Component
const ItemCard = {
    selectedItem: null,
    section: null,
    card: null,
    quantityInput: null,
    btnIncrease: null,
    btnDecrease: null,
    btnRetirar: null,
    btnDevolver: null,

    init() {
        this.section = document.getElementById('selectedItemSection');
        this.card = document.getElementById('selectedItemCard');
        this.quantityInput = document.getElementById('quantity');
        this.btnIncrease = document.getElementById('btnIncrease');
        this.btnDecrease = document.getElementById('btnDecrease');
        this.btnRetirar = document.getElementById('btnRetirar');
        this.btnDevolver = document.getElementById('btnDevolver');

        // Add event listeners
        this.btnIncrease.addEventListener('click', () => this.increaseQuantity());
        this.btnDecrease.addEventListener('click', () => this.decreaseQuantity());
        this.quantityInput.addEventListener('change', () => this.validateQuantity());
        this.btnRetirar.addEventListener('click', () => this.handleRetirada());
        this.btnDevolver.addEventListener('click', () => this.handleDevolucao());
    },

    display(item) {
        this.selectedItem = item;
        const isLowStock = item.quantidade_disponivel <= item.estoque_minimo;

        this.card.innerHTML = `
            <div class="item-name">${item.nome}</div>
            ${item.categoria ? `<div class="item-category">📂 ${item.categoria}</div>` : ''}
            <div class="item-info">
                <div class="item-info-item">
                    <span class="item-info-label">Disponível</span>
                    <span class="item-info-value ${isLowStock ? 'low-stock' : ''}">
                        ${item.quantidade_disponivel} un
                    </span>
                </div>
                <div class="item-info-item">
                    <span class="item-info-label">Estoque Mínimo</span>
                    <span class="item-info-value">${item.estoque_minimo || 0} un</span>
                </div>
                ${item.localizacao ? `
                    <div class="item-info-item">
                        <span class="item-info-label">Localização</span>
                        <span class="item-info-value">📍 ${item.localizacao}</span>
                    </div>
                ` : ''}
            </div>
            ${isLowStock ? `
                <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(245, 158, 11, 0.2); border-radius: 0.5rem; font-size: 0.875rem;">
                    ⚠️ Estoque baixo! Supervisor será notificado.
                </div>
            ` : ''}
        `;

        // Reset quantity
        this.quantityInput.value = 1;

        // Show section
        this.section.classList.remove('hidden');

        // Scroll to section
        this.section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    increaseQuantity() {
        const current = parseInt(this.quantityInput.value) || 1;
        this.quantityInput.value = current + 1;
        this.validateQuantity();
    },

    decreaseQuantity() {
        const current = parseInt(this.quantityInput.value) || 1;
        if (current > 1) {
            this.quantityInput.value = current - 1;
        }
    },

    validateQuantity() {
        const value = parseInt(this.quantityInput.value) || 1;
        if (value < 1) {
            this.quantityInput.value = 1;
        }
    },

    async handleRetirada() {
        const userName = document.getElementById('userName').value.trim();
        const quantity = parseInt(this.quantityInput.value);

        // Validations
        if (!userName) {
            App.showToast('Por favor, digite seu nome', 'warning');
            document.getElementById('userName').focus();
            return;
        }

        if (!this.selectedItem) {
            App.showToast('Selecione um item', 'warning');
            return;
        }

        if (quantity > this.selectedItem.quantidade_disponivel) {
            App.showToast('Quantidade indisponível em estoque!', 'error');
            return;
        }

        // Confirm action
        if (!confirm(`Confirmar retirada de ${quantity} unidade(s) de ${this.selectedItem.nome}?`)) {
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

            App.showToast(`✅ ${quantity} unidade(s) retirada(s) com sucesso!`, 'success');

            // Update item display with new quantity
            this.selectedItem.quantidade_disponivel = response.novo_saldo;
            this.display(this.selectedItem);

            // Reset quantity
            this.quantityInput.value = 1;

        } catch (error) {
            App.showToast(`Erro: ${error.message}`, 'error');
        } finally {
            App.showLoading(false);
        }
    },

    async handleDevolucao() {
        const userName = document.getElementById('userName').value.trim();
        const quantity = parseInt(this.quantityInput.value);

        // Validations
        if (!userName) {
            App.showToast('Por favor, digite seu nome', 'warning');
            document.getElementById('userName').focus();
            return;
        }

        if (!this.selectedItem) {
            App.showToast('Selecione um item', 'warning');
            return;
        }

        // Confirm action
        if (!confirm(`Confirmar devolução de ${quantity} unidade(s) de ${this.selectedItem.nome}?`)) {
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

            App.showToast(`✅ ${quantity} unidade(s) devolvida(s) com sucesso!`, 'success');

            // Update item display with new quantity
            this.selectedItem.quantidade_disponivel = response.novo_saldo;
            this.display(this.selectedItem);

            // Reset quantity
            this.quantityInput.value = 1;

        } catch (error) {
            App.showToast(`Erro: ${error.message}`, 'error');
        } finally {
            App.showLoading(false);
        }
    }
};

