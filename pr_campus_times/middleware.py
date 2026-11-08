class FlutterCorsMiddleware:
    """Allow local Flutter Web in development and configured origins in production."""
    DEVELOPMENT_ORIGINS = {
        'http://localhost:5000', 'http://127.0.0.1:5000',
        'http://localhost:5500', 'http://127.0.0.1:5500',
        'http://localhost:3000', 'http://127.0.0.1:3000',
    }
    def __init__(self, get_response): self.get_response = get_response
    def _allowed(self, origin):
        import os
        configured = {value.strip() for value in os.environ.get('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',') if value.strip()}
        if origin in configured: return True
        if os.environ.get('DJANGO_DEBUG', '1').lower() not in {'1', 'true', 'yes'}: return False
        if origin in self.DEVELOPMENT_ORIGINS: return True
        # Development LAN support for Flutter Web opened from another device.
        if origin.startswith(('http://192.168.', 'http://10.', 'http://172.16.', 'http://172.17.', 'http://172.18.', 'http://172.19.', 'http://172.2', 'http://172.3')): return True
        return False
    def __call__(self, request):
        from django.http import HttpResponse
        origin = request.headers.get('Origin', '')
        allowed = self._allowed(origin)
        response = HttpResponse(status=204) if request.method == 'OPTIONS' and allowed else self.get_response(request)
        if allowed:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, Accept'
            response['Access-Control-Max-Age'] = '86400'
            response['Vary'] = 'Origin'
        return response
