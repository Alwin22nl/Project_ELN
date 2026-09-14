from werkzeug.security import check_password_hash, generate_password_hash

class AuthenticationService:
    def __init__(self, repository):
        self.repository = repository

    def authenticate(self, username, password):
        user = self.repository.get_active_user_by_username(username)

        if not user:
            return None

        if not check_password_hash(user["password_hash", password]):
            return None

        return user

    def change_password(self, user_id, password1, password2):
        if password1 != password2:
            return False

        password_hash = generate_password_hash(password1)

        self.repository.update_password(user_id, password_hash)

        return True