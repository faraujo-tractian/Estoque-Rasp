// Modal Component
const Modal = {
    modal: null,
    modalTitle: null,
    modalBody: null,
    modalConfirm: null,
    modalCancel: null,
    
    init() {
        this.modal = document.getElementById('modal');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalBody = document.getElementById('modalBody');
        this.modalConfirm = document.getElementById('modalConfirm');
        this.modalCancel = document.getElementById('modalCancel');
        
        // Close modal on cancel or outside click
        this.modalCancel?.addEventListener('click', () => this.hide());
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });
    },
    
    show(title, body, onConfirm) {
        if (!this.modal) return;
        
        this.modalTitle.textContent = title;
        this.modalBody.textContent = body;
        
        // Remove previous listener
        const newConfirmBtn = this.modalConfirm.cloneNode(true);
        this.modalConfirm.parentNode.replaceChild(newConfirmBtn, this.modalConfirm);
        this.modalConfirm = newConfirmBtn;
        
        // Add new listener
        this.modalConfirm.addEventListener('click', () => {
            if (onConfirm) onConfirm();
            this.hide();
        });
        
        this.modal.classList.add('active');
    },
    
    hide() {
        this.modal?.classList.remove('active');
    }
};
