// Динамическая подгрузка категорий на главной странице

document.addEventListener('DOMContentLoaded', async function() {
    const categoriesRow = document.querySelector('.row.row-cols-1.row-cols-lg-6.align-items-stretch.g-4.py-5');
    if (!categoriesRow) return;
    try {
        const res = await fetch('/ads/categories/all');
        if (res.ok) {
            const categories = await res.json();
            categoriesRow.innerHTML = '';
            categories.forEach(cat => {
                categoriesRow.innerHTML += `
                <div class="col">
                  <div class="overflow-hidden itemBorder">
                    <div class="d-flex flex-column h-100">
                      <img src="static/image/noLogoItem900.png" alt="" class="">
                      <p class="itemText">${cat.name}</p>
                    </div>
                  </div>
                </div>
                `;
            });
        }
    } catch (e) {
        console.error('Ошибка загрузки категорий', e);
    }
}); 