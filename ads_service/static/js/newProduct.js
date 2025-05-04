// Динамическая подгрузка категорий и общежитий для формы создания объявления

document.addEventListener('DOMContentLoaded', async function() {
    // Категории
    const categorySelect = document.getElementById('country');
    if (categorySelect) {
        try {
            const res = await fetch('/ads/categories/all');
            if (res.ok) {
                const categories = await res.json();
                // Очищаем старые опции, кроме первой
                categorySelect.innerHTML = '<option value="">Категория</option>';
                categories.forEach((cat, idx) => {
                    // Если есть id, используйте его, иначе индекс
                    categorySelect.innerHTML += `<option value="${cat.id || idx + 1}">${cat.name}</option>`;
                });
            }
        } catch (e) {
            console.error('Ошибка загрузки категорий', e);
        }
    }

    // Общежития
    const dormSelect = document.getElementById('state');
    if (dormSelect) {
        try {
            const res = await fetch('/ads/dormitories/all');
            if (res.ok) {
                const dorms = await res.json();
                dormSelect.innerHTML = '<option value="">Выберите номер общежития</option>';
                dorms.forEach((dorm, idx) => {
                    dormSelect.innerHTML += `<option value="${dorm.id || idx + 1}">${dorm.name}</option>`;
                });
            }
        } catch (e) {
            console.error('Ошибка загрузки общежитий', e);
        }
    }
}); 