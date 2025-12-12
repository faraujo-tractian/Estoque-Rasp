// Modal Component for History
const Modal = {
    modal: null,
    modalBody: null,
    closeBtn: null,
    historyBtn: null,

    init() {
        this.modal = document.getElementById('modalHistorico');
        this.modalBody = document.getElementById('modalBody');
        this.closeBtn = document.getElementById('modalClose');

        // Add event listeners
        this.closeBtn.addEventListener('click', () => this.close());
        
        // Close on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.close();
            }
        });
    },

    async open() {
        try {
            App.showLoading(true);
            const history = await API.getHistory();
            this.displayHistory(history);
            this.modal.classList.remove('hidden');
        } catch (error) {
            App.showToast('Erro ao carregar histórico', 'error');
        } finally {
            App.showLoading(false);
        }
    },

    close() {
        this.modal.classList.add('hidden');
    },

    displayHistory(history) {
        if (!history || history.length === 0) {
            this.modalBody.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--color-text-secondary);">
                    📋 Nenhuma movimentação registrada ainda
                </div>
            `;
            return;
        }

        this.modalBody.innerHTML = history.map(item => {
            const isRetirada = item.tipo === 'retirada';
            const emoji = isRetirada ? '🔴' : '🟢';
            const typeText = isRetirada ? 'RETIRADA' : 'DEVOLUÇÃO';
            const date = new Date(item.timestamp);
            const dateStr = date.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            return `
                <div class="history-item ${item.tipo}">
                    <div class="history-header">
                        <span class="history-type">${emoji} ${typeText}</span>
                        <span class="history-date">${dateStr}</span>
                    </div>
                    <div class="history-details">
                        <strong>${item.item_nome}</strong><br>
                        Quantidade: ${item.quantidade} un<br>
                        Responsável: ${item.nome_pessoa}<br>
                        Saldo após: ${item.saldo_apos} un
                    </div>
                </div>
            `;
        }).join('');
    }
};

