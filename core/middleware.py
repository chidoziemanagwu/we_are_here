from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            ip = self.get_client_ip(request)
            if not self.is_rate_allowed(ip):
                return HttpResponseTooManyRequests()
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def is_rate_allowed(self, ip):
        cache_key = f'rate_limit_{ip}'
        requests = cache.get(cache_key, [])
        now = time.time()

        # Keep only requests from the last minute
        requests = [req for req in requests if now - req < 60]

        if len(requests) >= 60:  # 60 requests per minute
            return False

        requests.append(now)
        cache.set(cache_key, requests, 60)
        return True

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = self.get_csp_policy()
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    def get_csp_policy(self):
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self'"
        ])