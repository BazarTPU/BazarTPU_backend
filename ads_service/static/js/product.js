// Динамическая подгрузка информации об объявлении на странице product.html

document.addEventListener('DOMContentLoaded', async function() {
    // Получаем id объявления из query-параметра
    const params = new URLSearchParams(window.location.search);
    const adId = params.get('id');
    if (!adId) return;

    try {
        const res = await fetch(`/ads/one_ad_json/${adId}`);
        if (res.ok) {
            const ad = await res.json();
            // const ad = ads.find(a => a.id == adId);
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
            let blockPhotos = document.getElementById('blockPhotos');
            photos.forEach((photo, idx) => {
                // const thumb = document.getElementById('currentPhoto' + idx);
                // if (thumb) thumb.src = photo;
                let button =``;
                button = `
                    <button class="allPhotos" onclick="clickPhoto(${idx})" type="button" style="display: inline-block; width: 100px; height: 100px;">
                        <img src="${photo}" id="currentPhoto${idx}" alt="" style="width: 100%; height: 100%; object-fit: contain; border-radius: 3px;">
                    </button>
                `;
                if(idx == 0) {
                    button = `
                        <button class="allPhotos" onclick="clickPhoto(${idx})" type="button" style="display: inline-block; width: 100px; height: 100px;">
                            <img src="${photo}" id="currentPhoto${idx}" alt="" style="width: 100%; height: 100%; object-fit: contain; border-radius: 3px; border: 3px solid rgb(40,190,70);">
                        </button>
                    `;
                }
                blockPhotos.innerHTML += button;
            });
        }
    } catch (e) {
        console.error('Ошибка загрузки объявления', e);
    }
}); 