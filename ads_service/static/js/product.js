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
            await loadUserData(ad.user_id);
        }
    } catch (e) {
        console.error('Ошибка загрузки объявления', e);
    }
});

// Функция для загрузки данных пользователя
async function loadUserData(userId) {
    try {
        // Use the full URL to the user service
        let userRes = await fetch(`http://localhost:8002/user/profile/json/${userId}`);

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
function setUserPhoto(userPhotoElement, userPhotoPath) {
    // Если у пользователя нет фото или путь пустой, устанавливаем дефолтное изображение
    if (!userPhotoPath || userPhotoPath.trim() === '' || userPhotoPath === '/static/img/noLogoItem900.png') {
        // Дефолтное изображение из другого микросервиса
        userPhotoElement.src = '/user_service/static/img/noLogoItem900.png';
        userPhotoElement.alt = 'Аватар по умолчанию';

        // Обработка ошибки загрузки дефолтного изображения
        userPhotoElement.onerror = function() {
            console.error('Ошибка загрузки дефолтного аватара');
            // Попробуем альтернативный путь для дефолтного изображения
            this.src = 'http://localhost:8002/static/img/noLogoItem900.png';
            this.onerror = null; // Убираем обработчик, чтобы избежать бесконечного цикла
        };
        return;
    }

    let photoSrc = userPhotoPath;

    // Варианты обработки пути к аватару
    if (photoSrc.startsWith('/static/')) {
        // Заменяем /static/ на путь к микросервису пользователей
        photoSrc = photoSrc.replace('/static/', '/user_service/static/');
    } else if (photoSrc.startsWith('http')) {
        // Если уже полный URL, оставляем как есть
        photoSrc = photoSrc;
    } else {
        // Если только имя файла, добавляем полный путь
        photoSrc = `/user_service/static/uploads/avatars/${photoSrc}`;
    }

    userPhotoElement.src = photoSrc;
    userPhotoElement.alt = 'Фото продавца';

    // Добавляем обработку ошибки загрузки изображения
    userPhotoElement.onerror = function() {
        console.log(`Ошибка загрузки аватара: ${photoSrc}`);

        // Если это не дефолтное изображение, попробуем альтернативные пути
        if (!photoSrc.includes('noLogoItem900')) {
            // Попробуем прямой порт микросервиса (например, 8080)
            const fileName = userPhotoPath.split('/').pop();
            const alternativeUrl = `http://localhost:8002/static/uploads/avatars/${fileName}`;

            if (this.src !== alternativeUrl) {
                this.src = alternativeUrl;
                return;
            }
        }

        // Если все попытки не удались, устанавливаем дефолтное изображение
        console.log('Устанавливаем дефолтное изображение после неудачных попыток');
        this.src = '/user_service/static/img/noLogoItem900.png';
        this.alt = 'Аватар по умолчанию';

        // Последняя попытка для дефолтного изображения
        this.onerror = function() {
            this.src = 'http://localhost:8002/static/img/noLogoItem900.png';
            this.onerror = null; // Убираем обработчик
        };
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