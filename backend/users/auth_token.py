from knox.auth import TokenAuthentication as KnoxTokenAuth

class TokenAuthSupportCookie(KnoxTokenAuth):
    """
    Extend Knox TokenAuthentication to support token from cookies.
    Priority: Authorization header > Cookie
    """
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' in request.META:
            return super().authenticate(request)

        token = request.COOKIES.get('auth_token')
        if token:
            return self.authenticate_credentials(token.encode("utf-8"))
        return None