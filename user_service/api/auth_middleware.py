from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Определяем защищенные пути
        protected_paths = ["/user/profile", "/new-product"]

        # Проверяем, является ли текущий путь защищенным
        path = request.url.path
        if any(path.startswith(protected) for protected in protected_paths):
            # Проверяем наличие токена в куках
            token = request.cookies.get("access_token")
            if not token:
                # Если токена нет, перенаправляем на страницу входа
                return RedirectResponse(url="/auth/login", status_code=302)

        # Продолжаем обработку запроса
        response = await call_next(request)
        return response