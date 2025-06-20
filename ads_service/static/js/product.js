// Динамическая подгрузка информации об объявлении на странице product.html

document.addEventListener('DOMContentLoaded', async function () {
    // Получаем id объявления из query-параметра
    const params = new URLSearchParams(window.location.search);
    const adId = params.get('id');
    if (!adId) return;

    try {
        const res = await fetch(`/ads/one_ad_json/${adId}`);
        if (res.ok) {
            const ad = await res.json();
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
                let button = ``;
                button = `
                    <button class="allPhotos" onclick="clickPhoto(${idx})" type="button" style="display: inline-block; width: 100px; height: 100px;">
                        <img src="${photo}" id="currentPhoto${idx}" alt="" style="width: 100%; height: 100%; object-fit: contain; border-radius: 3px;">
                    </button>
                `;
                if (idx == 0) {
                    button = `
                        <button class="allPhotos" onclick="clickPhoto(${idx})" type="button" style="display: inline-block; width: 100px; height: 100px;">
                            <img src="${photo}" id="currentPhoto${idx}" alt="" style="width: 100%; height: 100%; object-fit: contain; border-radius: 3px; border: 3px solid rgb(40,190,70);">
                        </button>
                    `;
                }
                blockPhotos.innerHTML += button;
            });
            await loadUserData(ad.user_id);
        }
    } catch (e) {
        console.error('Ошибка загрузки объявления', e);
    }
});

// Функция для загрузки данных пользователя
async function loadUserData(userId) {
    try {
        // Use the proxy endpoint from ads service
        let userRes = await fetch(`/ads/profile/json/${userId}`);

        if (userRes.ok) {
            const userData = await userRes.json();

            // Обновляем данные продавца в card body
            const cardTitle = document.querySelector('.card-title.chatTextNameSaler');
            const emailTgLabels = document.querySelectorAll('.card-text.chatTextNameProduct');
            const userPhoto = document.querySelector('.card .rounded-start');

            // Имя продавца
            if (cardTitle) {
                const fullName = `${userData.first_name || ''} ${userData.last_name || ''}`.trim();
                cardTitle.textContent = fullName || 'Имя не указано';
            }

            // Email/Tg и контактные данные
            if (emailTgLabels.length >= 2) {
                // Первый элемент - заголовок "Email/Tg"
                emailTgLabels[0].textContent = 'Контакты:';

                // Второй элемент - сами контакты
                let contacts = [];
                if (userData.email) contacts.push(userData.email);
                if (userData.telegram_id) contacts.push(`${userData.telegram_id}`);
                if (userData.phone) contacts.push(userData.phone);

                emailTgLabels[1].textContent = contacts.length > 0 ? contacts.join(' / ') : 'Контакты не указаны';
            }

            // Обновляем информацию об общежитии
            const addressDivs = document.querySelectorAll('.col-12 > div > span');
            if (addressDivs.length > 1) {
                if (userData.dormitory) {
                    addressDivs[1].textContent = userData.dormitory.startsWith('Общежитие №')
                        ? userData.dormitory
                        : `Общежитие №${userData.dormitory}`;
                } else {
                    addressDivs[1].textContent = '';
                }
            }

            // Фото пользователя
            if (userPhoto) {
                setUserPhoto(userPhoto, userData.user_photo);
            }
        } else {
            console.error('Ошибка загрузки данных пользователя:', userRes.status);
            // Устанавливаем данные по умолчанию при ошибке
            setDefaultUserData();
        }
    } catch (error) {
        console.error('Ошибка при запросе данных пользователя:', error);
        setDefaultUserData();
    }
}

// Функция для установки фото пользователя с обработкой дефолтного изображения
// Функция для установки фото пользователя с обработкой дефолтного изображения
function setUserPhoto(userPhotoElement, userPhotoPath) {
    // Если у пользователя нет фото, устанавливаем дефолтное изображение
    if (!userPhotoPath || userPhotoPath.trim() === '' || userPhotoPath.includes('noLogoItem900.png')) {
        // Дефолтное изображение из сервиса пользователей
        userPhotoElement.src = '/user_service/static/img/noLogoItem900.png';
        userPhotoElement.alt = 'Аватар по умолчанию';
        userPhotoElement.onerror = function () {
            // Резервный путь при ошибке
            this.src = 'http://localhost:8002/static/img/noLogoItem900.png';
            this.onerror = null;
        };
        return;
    }

    let finalSrc = userPhotoPath;

    // Пути, начинающиеся с /media/ (например, /media/avatars/...), уже являются
    // правильными корневыми путями, которые обрабатывает Nginx.
    // Мы не должны их изменять.
    if (finalSrc.startsWith('/media/')) {
        // Оставляем как есть, например: /media/avatars/some-uuid.png
    }
        // Для статических путей из user_service, которые бэкенд может вернуть как /static/...,
    // нам нужно добавить префикс, чтобы Nginx правильно направил запрос.
    else if (finalSrc.startsWith('/static/')) {
        finalSrc = '/user_service' + finalSrc;
    }
    // Если это полный URL, оставляем как есть.
    else if (finalSrc.startsWith('http')) {
        // Оставляем как есть
    }
    // Этот блок был основной причиной ошибки, теперь он не нужен для /media/ путей.

    userPhotoElement.src = finalSrc;
    userPhotoElement.alt = 'Фото продавца';

    // Обработка ошибки загрузки основного фото
    userPhotoElement.onerror = function () {
        console.error(`Ошибка загрузки аватара по основному пути: ${this.src}`);
        // В случае ошибки показываем дефолтное изображение
        this.src = '/user_service/static/img/noLogoItem900.png';
        this.alt = 'Аватар по умолчанию';
        this.onerror = null; // Убираем обработчик, чтобы избежать бесконечного цикла
    };
}

// Функция для установки данных по умолчанию при ошибке
function setDefaultUserData() {
    const cardTitle = document.querySelector('.card-title.chatTextNameSaler');
    const emailTgLabels = document.querySelectorAll('.card-text.chatTextNameProduct');
    const userPhoto = document.querySelector('.card .rounded-start');

    if (cardTitle) {
        cardTitle.textContent = 'Информация недоступна';
    }

    if (emailTgLabels.length >= 2) {
        emailTgLabels[0].textContent = 'Контакты:';
        emailTgLabels[1].textContent = 'Информация недоступна';
    }

    // Устанавливаем дефолтное изображение при ошибке загрузки данных пользователя
    if (userPhoto) {
        setUserPhoto(userPhoto, null);
    }
}