// Динамическая подгрузка информации об объявлении на странице product.html

document.addEventListener('DOMContentLoaded', async function() {
    // Получаем id объявления из query-параметра
    const params = new URLSearchParams(window.location.search);
    const adId = params.get('id');
    if (!adId) return;

    try {
        const res = await fetch(`/ads/json`);
        if (res.ok) {
            const ads = await res.json();
            const ad = ads.find(a => a.id == adId);
            if (!ad) return;
            // Название
            document.querySelector('h2.mb-3').textContent = ad.title;
            // Описание
            document.querySelector('textarea[readonly]').textContent = ad.description;
            // Цена
            document.querySelector('input[readonly][style]').value = ad.price + ' ₽';
            // Адрес
            const addressDivs = document.querySelectorAll('.col-12 > div > span');
            if (addressDivs.length > 0) addressDivs[0].textContent = ad.address || '';
            if (addressDivs.length > 1) addressDivs[1].textContent = ad.dormitory_id ? `Общежитие №${ad.dormitory_id}` : '';
            // Фото
            const photos = ad.photos && ad.photos.length ? ad.photos : ["/ads/static/image/noLogoItem900.png"];
            // Основное фото
            document.getElementById('currentPhoto').src = photos[0];
            // Миниатюры
            photos.forEach((photo, idx) => {
                const thumb = document.getElementById('currentPhoto' + idx);
                if (thumb) thumb.src = photo;
            });
        }
    } catch (e) {
        console.error('Ошибка загрузки объявления', e);
    }
}); 