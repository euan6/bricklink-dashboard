const minifigures = JSON.parse(document.getElementById('minifigure-data').textContent);
const grid = document.getElementById('collection-grid');
const search = document.getElementById('search');
const filterTheme = document.getElementById('filter-theme');
const filterYear = document.getElementById('filter-year');
const filterPrice = document.getElementById('filter-price');
const sortBy = document.getElementById('sort-by');

function priceInRange(price, range) {
    if (!range) return true;
    if (!price) return false;
    const p = parseFloat(price);
    if (range === '0-5') return p < 5;
    if (range === '5-10') return p >= 5 && p < 10;
    if (range === '10-20') return p >= 10 && p < 20;
    if (range === '20+') return p >= 20;
    return true;
}

function renderCards(figures) {
    grid.innerHTML = '';

    if (figures.length === 0) {
        grid.innerHTML = '<p style="color:#666;font-size:13px;">No figures match your filters.</p>';
        return;
    }

    figures.forEach(fig => {
        const card = document.createElement('a');
        card.className = 'col-card';
        card.href = `https://www.bricklink.com/v2/catalog/catalogitem.page?M=${fig.id}`;
        card.target = '_blank';
        card.rel = 'noopener noreferrer'

        const img = fig.image
            ? `<img src="/static/${fig.image}" alt="${fig.name}">`
            : `<div class="col-card-no-image">No image</div>`;

        card.innerHTML = `
            <div class="col-card-img">${img}</div>
            <div class="col-card-body">
                <div class="col-card-id">${fig.id}</div>
                <div class="col-card-name">${fig.name}</div>
                <div class="col-card-footer">
                    <span class="col-card-price">${fig.price ? '£' + fig.price : 'N/A'}</span>
                    <span class="col-card-year">${fig.year || ''}</span>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

function sortFigures(figures) {
    const value = sortBy.value;
    return [...figures].sort((a, b) => {
        if (value === 'year-desc') return (b.year || 0) - (a.year || 0);
        if (value === 'year-asc') return (a.year || 0) - (b.year || 0);
        if (value === 'price-desc') return parseFloat(b.price || 0) - parseFloat(a.price || 0);
        if (value === 'price-asc') return parseFloat(a.price || 0) - parseFloat(b.price || 0);
        if (value === 'name-asc') return a.name.localeCompare(b.name);
        return 0;
    });
}

function applyFilters() {
    const query = search.value.toLowerCase();
    const theme = filterTheme.value;
    const year = filterYear.value;
    const price = filterPrice.value;

    const filtered = minifigures.filter(fig => {
        const matchesSearch = !query ||
            fig.name.toLowerCase().includes(query) ||
            fig.id.toLowerCase().includes(query);
        const matchesTheme = !theme || fig.theme === theme;
        const matchesYear = !year || String(fig.year) === year;
        const matchesPrice = priceInRange(fig.price, price);
        return matchesSearch && matchesTheme && matchesYear && matchesPrice;
    });

    renderCards(sortFigures(filtered));
}

// attach filter listeners
search.addEventListener('input', applyFilters);
filterTheme.addEventListener('change', applyFilters);
filterYear.addEventListener('change', applyFilters);
filterPrice.addEventListener('change', applyFilters);
sortBy.addEventListener('change', applyFilters);

// initial render
renderCards(minifigures);
