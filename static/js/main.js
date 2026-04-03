/**
 * ImóvelPrime — Main JavaScript
 * Inicialização de comportamentos globais.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMessagesDismiss();
    initLazyImages();
    initSmoothScroll();
    initPriceInputs();
});

/** Auto-dismiss Django messages after 5 s */
function initMessagesDismiss() {
    document.querySelectorAll('[data-dismiss-message]').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('[role="alert"]');
            if (alert) fadeRemove(alert);
        });

        setTimeout(() => {
            const alert = btn.closest('[role="alert"]');
            if (alert) fadeRemove(alert);
        }, 5000);
    });
}

function fadeRemove(el) {
    el.style.transition = 'opacity 0.4s ease';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
}

/** Native lazy loading + IntersectionObserver fallback */
function initLazyImages() {
    if (!('loading' in HTMLImageElement.prototype)) {
        // Fallback para browsers antigos
        const images = document.querySelectorAll('img[loading="lazy"]');
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        delete img.dataset.src;
                    }
                    observer.unobserve(img);
                }
            });
        });
        images.forEach(img => observer.observe(img));
    }
}

/** Smooth scroll para âncoras internas */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            const id = anchor.getAttribute('href');
            const target = document.querySelector(id);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

/** Campos de preço: só números inteiros */
function initPriceInputs() {
    document.querySelectorAll('input[data-price-input]').forEach(input => {
        input.addEventListener('input', e => {
            e.target.value = e.target.value.replace(/[^\d]/g, '');
        });
    });
}
