import secrets, string, os

class utils:
    def generate_random_key(self, length):
        alphabet = string.ascii_letters + string.digits
        key = ''.join(secrets.choice(alphabet) for _ in range(length))
        return key

    def get_secret_key(self):
        secret_key = secrets.token_urlsafe(128)
        return secret_key
