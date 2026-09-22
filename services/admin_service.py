from werkzeug.security import generate_password_hash
from helper import generate_temp_password

class AdminService:
    def __init__(self, repository):
        self.repository = repository

    def get_admin_overview(self):
        return self.repository.get_all_users()

    def get_audit_logs(self):
        return self.repository.get_audit_logs()

    def reset_password(self, user_id):
        temp_password = generate_temp_password()
        password_hash = generate_password_hash(temp_password)

        self.repository.reset_user_password(user_id, password_hash)
        return temp_password

    def create_user(self, username, name, role):
        temp_password = generate_temp_password()
        password_hash= generate_password_hash(temp_password)

        self.repository.create_user(
            username=username,
            name=name,
            password_hash=password_hash,
            role=role
        )

        return temp_password