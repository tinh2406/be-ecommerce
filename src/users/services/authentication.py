from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from users.domains.jwt_domain import JWTDomain


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        if len(auth) < 2:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = JWTDomain.decode(token, 12)
            if not user.is_active:
                raise exceptions.AuthenticationFailed("User inactive or deleted.")
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid token.")

        return user, token
