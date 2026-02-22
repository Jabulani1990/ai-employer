class RefreshToken(str):
    """Minimal token object compatible with current serializer usage."""

    @classmethod
    def for_user(cls, user):
        return cls(f"dev-refresh-token-{user.pk}")

    @property
    def access_token(self):
        return f"dev-access-token-{self}"
