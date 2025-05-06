// Динамическая подгрузка найденных объявлений на странице foundAds.html

document.addEventListener('DOMContentLoaded', function() {
    // 1. Читаем initial search term из URL
    const params = new URLSearchParams(window.location.search);
    let searchTerm = params.get('q') || '';

    // 2. Находим элементы на странице
    const heading = document.querySelector('.announcementAround');
    const allProductContainer = document.getElementById('allProduct');
    const searchInput = document.getElementById('searchInput');
    const searchForm  = document.getElementById('searchForm');

    let debounceTimer;

    // Обновляем заголовок в зависимости от term
    function updateHeading(term) {
      if (!heading) return;
      heading.textContent = term
        ? `Результаты поиска: «${term}»`
        : 'Все объявления';
    }

    // Функция загрузки и отображения объявлений
    function fetchAndDisplayAds(term = '') {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            let apiUrl = '/ads/search_json';
            if (term) {
                apiUrl += `?q=${encodeURIComponent(term)}`;
            }

            console.log(`Fetching from: ${apiUrl}`);
            fetch(apiUrl)
              .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
              })
              .then(data => {
                allProductContainer.innerHTML = '';
                if (data.length === 0) {
                  allProductContainer.innerHTML = '<p class="text-center">Объявлений не найдено.</p>';
                  return;
                }

                data.forEach(ad => {
                  // создаём контейнер для одной карточки
                  const col = document.createElement('div');
                  col.className = 'col product';

                  // выбираем картинку: первая из ad.photos или заглушка
                  const imageUrl = (ad.photos && ad.photos.length > 0 && ad.photos[0])
                                   ? ad.photos[0]
                                   : '/ads/static/image/noLogoItem900.png';

                  // ссылка на страницу товара
                  const productLink = ad.id ? `/ads/products?id=${ad.id}` : '#';

                  // наполняем HTML карточки
                  col.innerHTML = `
                    <div class="overflow-hidden productBorder d-flex flex-column" style="width: 100%; height: 650px;">
                      <div class="d-flex flex-column h-100">
                        <div class="img-wrapper flex-grow-1 overflow-hidden">
                          <img src="${imageUrl}" alt="${ad.title}" class="w-100 h-100 object-fit-cover">
                        </div>
                        <div class="p-3">
                          <span class="fw-bold">${ad.title}</span>
                          <p class="mt-2">${ad.price.toLocaleString('ru-RU')} ₽</p>
                          ${ad.id
                            ? `<a href="${productLink}" class="btn btn-primary buttonProduct">
                                 <span class="buttonProductText">Просмотр</span>
                               </a>`
                            : '<p class="text-muted">Нет ссылки</p>'}
                        </div>
                      </div>
                    </div>
                  `;

                  // добавляем карточку в контейнер
                  allProductContainer.appendChild(col);
                });
              })
              .catch(err => {
                console.error('Ошибка при загрузке объявлений:', err);
                allProductContainer.innerHTML = '<p class="text-center text-danger">Ошибка загрузки.</p>';
              });
        }, 300);
    }

    // Первоначальный рендер при загрузке страницы
    updateHeading(searchTerm);
    fetchAndDisplayAds(searchTerm);

    // Перехватываем сабмит формы, чтобы делать новый поиск без перезагрузки
    if (searchForm) {
      searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        searchTerm = searchInput.value.trim();
        // Обновляем URL в адресной строке без перезагрузки
        const newUrl = `${window.location.pathname}?q=${encodeURIComponent(searchTerm)}`;
        window.history.replaceState({}, '', newUrl);

        updateHeading(searchTerm);
        fetchAndDisplayAds(searchTerm);
      });
    }
});
