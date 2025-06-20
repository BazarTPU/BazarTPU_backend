# Файл: user_service/middlewares/auth_middleware.py

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Определяем ТОЧНЫЕ пути, которые нужно защитить.
        # не используем startswith, а проверяем полное совпадение.
        protected_exact_paths = [
            "/user/profile",  # Страница профиля пользователя
            "/ads/newProduct",  # Страница создания объявления (перенаправление на /ads/newProduct)
            "/user/new-product"  # Старый вариант пути, если используется
        ]

        path = request.url.path

        # Проверяем, совпадает ли путь с одним из защищенных.
        if path in protected_exact_paths:
            # Проверяем наличие токена в куках
            token = request.cookies.get("access_token")
            if not token:
                # Если токена нет, перенаправляем на страницу входа
                return RedirectResponse(url="/auth/login", status_code=302)

        # Для всех остальных путей (включая /user/profile/json/{user_id})
        # просто продолжаем обработку запроса.
        response = await call_next(request)
        return response