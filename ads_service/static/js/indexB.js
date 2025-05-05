// // Динамическая подгрузка категорий на главной странице

document.addEventListener('DOMContentLoaded', async function() {
    const categoriesRow = document.getElementById('qwe');
    if (!categoriesRow) return;
    try {
      const res = await fetch('/ads/categories/all');
      if (res.ok) {
        const categories = await res.json();
        categoriesRow.innerHTML = '';
        categories.forEach(cat => {
            categoriesRow.innerHTML += `
            <div class="col">
              <a href=""><button class="buttonProduct" style="height: 70px; width: 100%;"><span class="buttonCategories buttonProductText">${cat.name}</span></button></a>
            </div>
            `;
        });
      }
    } catch (e) {
        console.error('Ошибка загрузки категорий', e);
    }
}); 