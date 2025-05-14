// // Динамическая подгрузка найденных объявлений на главной странице по конкретной категории
document.addEventListener('DOMContentLoaded', function() {
  fetch(`/ads/get_product_by_category?category_id=${categoryId}`)
      .then(response => response.json())
      .then(data => {
          const allProduct = document.getElementById('allProduct');
          allProduct.innerHTML = '';
          data.forEach(ad => {
              const col = document.createElement('div');
              col.className = 'col product';
              col.innerHTML = ` 
                  <div class="overflow-hidden productBorder d-flex flex-column" style="width: 100%; height: 650px;">
                      <div class="d-flex flex-column h-100">
                        <div class="img-wrapper flex-grow-1 overflow-hidden">
                          <img src="${ad.photos && ad.photos[0] ? ad.photos[0] : 'static/image/noLogoItem900.png'}" alt="" class="w-100 h-100 object-fit-cover">
                        </div>
                        <div class="p-3">
                          <span>${ad.title}</span>
                          <p>${ad.price} ₽</p>
                          <a href="/ads/products?id=${ad.id}" ><button class="buttonProduct" ><span class="buttonProductText">Просмотр</span></button></a>
                        </div>  
                      </div>
                  </div>
              `;
              allProduct.appendChild(col);
          });
      });
});