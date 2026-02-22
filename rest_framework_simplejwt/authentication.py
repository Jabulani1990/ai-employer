from rest_framework.authentication import BaseAuthentication


class JWTAuthentication(BaseAuthentication):
    """Fallback authenticator that performs no JWT auth.

    This keeps the project importable in restricted environments.
    """

    def authenticate(self, request):
        return None
