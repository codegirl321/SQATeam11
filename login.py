from flask_bcrypt import Bcrypt
from models import UserLogin
from flask_login import UserMixin

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_username(username):
        """Retrieve user data by username from the UserLogin database table."""
        user_data = UserLogin.query.filter_by(username=username).first()  # Query the UserLogin table
        if user_data:
            return {'id': user_data.id, 'username': user_data.username, 'password': user_data.password}
        return None

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve user data by ID from the UserLogin database table."""
        user_data = UserLogin.query.get(user_id)  # Query the UserLogin table using ID
        if user_data:
            return {'id': user_data.id, 'username': user_data.username, 'password': user_data.password}
        return None


def authenticate_user(username, password):
    """Authenticate user by comparing hashed password."""
    user_data = User.get_user_by_username(username)
    if not user_data:
        return None, "User not found"

    # Verify the password
    if bcrypt.check_password_hash(user_data['password'], password):
        return User(user_data['id'], user_data['username'], user_data['password']), None
    else:
        return None, "Password incorrect"
