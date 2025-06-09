<h1 align="center">📢 BazarTPU</h1>
<p align="center">
  <strong>Сервис для публикации объявлений для студентов ТПУ</strong><br>
  <a href="https://github.com/BazarTPU/BazarTPU_backend.git">GitHub Repository</a>
</p>

<hr>

<h2>🚀 Описание проекта</h2>

<p>
  <code>BazarTPU</code> — это микросервисное приложение, позволяющее студентам Томского политехнического университета размещать и просматривать объявления. Проект разработан с использованием <strong>FastAPI</strong>, <strong>PostgreSQL</strong>, <strong>Docker</strong>.
</p>

<hr>

<h2>📦 Технологии</h2>

<ul>
  <li>Python 3.13+</li>
  <li>FastAPI</li>
  <li>PostgreSQL</li>
  <li>SQLAlchemy</li>
  <li>Alembic</li>
  <li>Docker + Docker Compose</li>
  <li>Uvicorn</li>
</ul>

<hr>

<h2>⚙️ Установка и запуск</h2>

<h3>1. Клонирование репозитория</h3>

```bash
git clone https://github.com/BazarTPU/BazarTPU_backend.git
```

<h3>2. Базы данных</h3> <p>В папках <code>ads_service/</code> и <code>user_service/</code> не забудьте поменять
конфигурации баз данных (пароль, имя юзера).</p>
<h3>3. Запуск через Docker</h3>

```bash
docker-compose up -d
```

<p>📌 Поднимает все сервисы и базы данных в фоновом режиме.</p> <hr> 
<h2>🧬 Работа с миграциями Alembic</h2> <h3>Создание новой миграции</h3>

```bash
alembic -c .\ads_service\alembic.ini revision --autogenerate -m "Initial migration"
```
<p>📌 Создаёт файл миграции на основе моделей SQLAlchemy.</p> <h3>Применение миграций</h3>

```bash
alembic -c .\ads_service\alembic.ini upgrade head
```
<p>📌 Применяет миграции к базе данных.</p> <hr> 
<h2>🚀 Запуск в режиме разработки</h2> <h3>ads_service (порт 8001)</h3>

```bash
uvicorn ads_service.main:app --port 8001 --reload
```
<h3>user_service (порт 8000)</h3>

```bash
uvicorn user_service.main:app --port 8002 --reload
```

<p>📌 Флаг <code>--reload</code> автоматически перезапускает сервер при изменениях в коде.</p> <hr> <h2>📫 Документация API</h2> <ul> <li><a href="http://localhost:8002/docs" target="_blank">http://localhost:8002/docs</a> — user_service</li> <li><a href="http://localhost:8001/docs" target="_blank">http://localhost:8001/docs</a> — ads_service</li> </ul>