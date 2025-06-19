
document.querySelectorAll('input[type="text"], input[type="number"]').forEach(input => {
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') e.preventDefault();
  });
});

// ====== Цена: только цифры + диапазон ======
(function() {
const input = document.getElementById('price');
const error = document.getElementById('price-error');
const MIN   = Number(input.min);
const MAX   = Number(input.max);

input.addEventListener('keypress', e => {
    if (!/[0-9]/.test(e.key)) e.preventDefault();
});
input.addEventListener('input', () => {
    const cleaned = input.value.replace(/[^0-9]/g, '');
    if (cleaned !== input.value) input.value = cleaned;
});
input.addEventListener('blur', () => {
    let val = Number(input.value);
    if (isNaN(val) || val < MIN) val = MIN;
    else if (val > MAX)        val = MAX;
    input.value = val;
    error.style.display = (val < MIN || val > MAX) ? 'block' : 'none';
});
input.addEventListener('wheel', e => e.preventDefault());
})();

(function(){
  const input     = document.getElementById('photos');
  const btnSelect = document.getElementById('btn-select');
  const preview   = document.getElementById('preview');
  const errCount  = document.getElementById('error-count');
  const errFormat = document.getElementById('error-format');
  const errSize   = document.getElementById('error-size');

  const MAX_FILES = 5;
  const MAX_SIZE  = 10 * 1024 * 1024; // 10 МБ
  const ALLOWED   = ['image/jpeg','image/png'];

  // Массив всех выбранных файлов
  let allFiles = [];

  btnSelect.addEventListener('click', () => input.click());

  function updateInputFiles(files) {
    const dt = new DataTransfer();
    files.forEach(f => dt.items.add(f));
    input.files = dt.files;
  }

  function renderPreviews(files) {
    preview.innerHTML = '';
    files.forEach((file, idx) => {
      const reader = new FileReader();
      const box = document.createElement('div');
      box.className = 'preview-box';
      box.draggable = true;
      box.dataset.index = idx;
      Object.assign(box.style, {
        width: '100px',
        height: '100px',
        border: '1px solid #ccc',
        borderRadius: '4px',
        overflow: 'hidden',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        position: 'relative',
        cursor: 'move'
      });
      
      // Кнопка удаления
      const delBtn = document.createElement('button');
      delBtn.textContent = '×';
      Object.assign(delBtn.style, {
        position: 'absolute',
        top: '2px',
        right: '2px',
        background: 'rgba(0,0,0,0.5)',
        color: '#fff',
        border: 'none',
        borderRadius: '50%',
        width: '20px',
        height: '20px',
        cursor: 'pointer',
        padding: '0',
        lineHeight: '20px',
        textAlign: 'center'
      });
      delBtn.addEventListener('click', () => {
        allFiles.splice(idx,1);
        updateInputFiles(allFiles);
        renderPreviews(allFiles);
      });
      box.appendChild(delBtn);

      reader.onload = () => box.style.backgroundImage = `url(${reader.result})`;
      reader.readAsDataURL(file);
      preview.appendChild(box);
    });
  }

  input.addEventListener('change', () => {
    [errCount, errFormat, errSize].forEach(e=>e.style.display='none');
    let newFiles = Array.from(input.files);

    // Формат
    const badFormat = newFiles.filter(f => !ALLOWED.includes(f.type));
    if (badFormat.length) {
      errFormat.style.display = 'block';
      input.value = '';
      return;
    }
    // Размер
    const tooBig = newFiles.filter(f => f.size > MAX_SIZE);
    if (tooBig.length) {
      errSize.style.display = 'block';
      input.value = '';
      return;
    }
    // Дубли
    newFiles = newFiles.filter(nf => !allFiles.some(af => af.name === nf.name && af.size === nf.size));

    if (!newFiles.length) {
      input.value = '';
      return;
    }
    // Доступные слоты
    const slots = MAX_FILES - allFiles.length;
    if (slots <= 0) {
      errCount.style.display = 'block';
      input.value = '';
      return;
    }
    if (newFiles.length > slots) {
      errCount.style.display = 'block';
      newFiles = newFiles.slice(0, slots);
    }

    // Добавляем новые файлы
    allFiles = allFiles.concat(newFiles);
    updateInputFiles(allFiles);
    renderPreviews(allFiles);
    // Не очищаем input.files, чтобы поле отражало выбранные файлы
  });

  // Drag & Drop
  let dragSrc = null;
  preview.addEventListener('dragstart', e => {
    if (e.target.classList.contains('preview-box')) {
      dragSrc = Number(e.target.dataset.index);
      e.dataTransfer.effectAllowed = 'move';
    }
  });
  preview.addEventListener('dragover', e => e.preventDefault());
  preview.addEventListener('drop', e => {
    e.preventDefault();
    const tgt = e.target.closest('.preview-box');
    if (!tgt) return;
    const dropIdx = Number(tgt.dataset.index);
    const moved = allFiles.splice(dragSrc,1)[0];
    allFiles.splice(dropIdx,0,moved);
    updateInputFiles(allFiles);
    renderPreviews(allFiles);
  });
})();

document.addEventListener('DOMContentLoaded', () => {
  const form      = document.getElementById('newProductForm');
  const country   = form.querySelector('#country');
  const state     = form.querySelector('#state');
  const title     = form.querySelector('#title');
  const desc      = form.querySelector('#description');
  const photos    = form.querySelector('#photos');
  const errPhoto  = form.querySelector('#error-photo-required');
  const priceErr  = form.querySelector('#price-error');
  const zip   = form.querySelector('#zip');

  const textRule = /^["A-Za-zА-Яа-я "]{2,}[A-Za-zА-Яа-я0-9 \"«»!,№;%:?*()_+-=]*$/;
  // const textRuleTextArea = /^["A-Za-zА-Яа-я "]{2,}[A-Za-zА-Яа-я0-9 \"«»!№;%:?*()_+-=]*$/;
  const textRuleTextArea = /^[A-Za-zА-Яа-я"\s]{2,}[A-Za-zА-Яа-я0-9"\s«»!,№;%:?*()_+\-=\s]*$/;


  function checkField(field, ruleFn) {
    const ok = ruleFn(field.value.trim());
    field.classList.toggle('is-invalid', !ok);
    return ok;
  }

  function checkPhotos() {
    if (photos.files.length > 0) {
      errPhoto.style.display = 'none';
      return true;
    } else {
      errPhoto.style.display = 'block';
      return false;
    }
  }

  function validateLocation() {
    const ok = state.value !== '' || zip.value.trim() !== '';
    state.classList.toggle('is-invalid', !ok);
    zip.classList.toggle('is-invalid',   !ok);
    return ok;
  }
  state.addEventListener('change', validateLocation);
  zip.addEventListener('input',   validateLocation);

  form.addEventListener('submit', async e => {
    e.preventDefault();
    e.stopImmediatePropagation();


    let valid = true;
    // 0) фото
    valid = checkPhotos();

    // 1) категория
    valid = checkField(country, v => v !== '') && valid;

    // 2) название
    valid = checkField(title, v => textRule.test(v)) && valid;

    // 3) описание
    valid = checkField(desc, v => textRuleTextArea.test(v)) && valid;

    // 4) местоположение (общее)
    // valid = checkField(state, v => v !== '') && valid;
    // 
    const locValid = validateLocation();
    valid = valid && locValid;

    const stateEl = form.querySelector('#state');
    stateEl.classList.toggle('is-invalid', !locValid);
    zip.classList.toggle('is-invalid',   !locValid);

    valid = valid && locValid;

    if (!valid) {
      // фокус на первое невалидное
      const bad = form.querySelector('.is-invalid');
      if (bad) bad.focus();
      return;
    }

    if (state.value === '') {
      state.disabled = true;      // public dormitory_id
    } else {
      zip.disabled = true;        // public address
    }

    // всё валидно — собираем и шлём
    const formData = new FormData(form);
    formData.append('user_id', '00000000-0000-0000-0000-000000000001');

    try {
      const resp = await fetch('/ads/create_new_ad', {
        method: 'POST',
        body: formData
      });
      if (resp.ok) {
        window.location.href = '/ads';
      } else {
        alert('Заполните все поля!');
      }
    } catch (err) {
      console.error(err);
      alert('Сетевая ошибка при отправке формы');
    }
    
  });

  // снимаем ошибки «на лету»
  title.addEventListener('input',  () => checkField(title, v => textRule.test(v)));
  desc.addEventListener('input',  () => checkField(desc,  v => textRuleTextArea.test(v)));
  country.addEventListener('change',() => checkField(country, v => v !== ''));
  state.addEventListener('change',() => checkField(state,   v => v !== ''));
  photos.addEventListener('change',() => checkPhotos());
});

