from web.security.model import User
from web.security.auth import get_password_hash

# Фейковая база пользователей
fake_users_db = {
    "dnaumov09@gmail.com": {
        "email": "dnaumov09@gmail.com",
        "password": get_password_hash("newPass5"),
        "active": True,
    }
}

def get_user(email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return User(**user_dict)