/**
 * ImóvelPrime — Filters JavaScript
 * Auto-submit em selects, validação de faixa de preço.
 */

document.addEventListener('DOMContentLoaded', () => {
    initAutoSubmitSelects();
    initPriceRangeValidation();
    initClearFiltersButton();
});

/** Auto-submit ao mudar selects no sidebar */
function initAutoSubmitSelects() {
    const form = document.getElementById('filter-form');
    if (!form) return;

    ['listing_type', 'property_type', 'min_bedrooms'].forEach(name => {
        const field = form.querySelector(`[name="${name}"]`);
        if (field) field.addEventListener('change', () => form.submit());
    });
}

/** Garante min_price <= max_price antes de submeter */
function initPriceRangeValidation() {
    const form = document.getElementById('filter-form');
    if (!form) return;

    const minInput = form.querySelector('[name="min_price"]');
    const maxInput = form.querySelector('[name="max_price"]');
    if (!minInput || !maxInput) return;

    form.addEventListener('submit', e => {
        const min = parseFloat(minInput.value);
        const max = parseFloat(maxInput.value);

        maxInput.setCustomValidity('');

        if (min && max && min > max) {
            e.preventDefault();
            maxInput.setCustomValidity('O preço máximo deve ser maior que o mínimo.');
            maxInput.reportValidity();
        }
    });
}

/** Botão "Limpar filtros" reseta form e redireciona */
function initClearFiltersButton() {
    const btn = document.getElementById('clear-filters-btn');
    if (!btn) return;

    btn.addEventListener('click', e => {
        e.preventDefault();
        const form = document.getElementById('filter-form');
        if (form) {
            form.reset();
            window.location.href = window.location.pathname;
        }
    });
}
