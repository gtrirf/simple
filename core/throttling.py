from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache
from rest_framework.exceptions import Throttled

class LeadPostThrottle(SimpleRateThrottle):
    scope = 'lead_post'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        return self.get_ident(request)

    def allow_request(self, request, view):
        ip = self.get_ident(request)
        blocked = cache.get(f"blocked:{ip}")
        if blocked:
            raise Throttled(detail="IP bloklangan. 1 soatdan keyin urinib ko‘ring.")
        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        self.history = [timestamp for timestamp in self.history if timestamp > self.now - self.duration]

        if len(self.history) >= 10:
            cache.set(f"blocked:{ip}", True, timeout=3600)
            raise Throttled(detail="IP haddan tashqari ko'p murojaat qildi va 1 soatga bloklandi.")

        return True

    def throttle_success(self):
        self.history.append(self.now)
        self.cache.set(self.key, self.history, self.duration)
