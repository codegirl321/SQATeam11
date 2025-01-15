from flask import Flask, request, render_template
from flask_login import LoginManager, UserMixin, login_user
from flask_bcrypt import Bcrypt
from models import UserLogin, db  # Import UserLogin model and db instance
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_username(username):
        """Retrieve user data by username from the UserLogin database table."""
        try:
            user_data = UserLogin.query.filter_by(username=username).first()  # Query the UserLogin table
            if user_data:
                return {'id': user_data.id, 'username': user_data.username, 'password': user_data.password}
            return None
        except NoResultFound:
            print(f"User {username} not found in the database.")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve user data by ID from the UserLogin database table."""
        try:
            user_data = UserLogin.query.get(user_id)  # Query the UserLogin table using ID
            if user_data:
                return {'id': user_data.id, 'username': user_data.username, 'password': user_data.password}
            return None
        except NoResultFound:
            print(f"User with ID {user_id} not found in the database.")
            return None

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login based on user_id."""
    return User.get_user_by_id(user_id)

def authenticate_user(username, password):
    """Authenticate user by comparing hashed password."""
    user_data = User.get_user_by_username(username)
    if not user_data:
        print(f"User {username} not found.")
        return None, "User not found"

    # Verify the password
    if bcrypt.check_password_hash(user_data['password'], password):
        print(f"Password for {username} is correct.")
        return User(user_data['id'], user_data['username'], user_data['password']), None
    else:
        print(f"Password for {username} is incorrect.")
        return None, "Password incorrect"

@app.route('/login', methods=['POST'])
def login():
    """Login route to handle POST request for login."""
    username = request.form.get('username')
    password = request.form.get('password')

    user, error = authenticate_user(username, password)
    if user:
        login_user(user)
        return "Login successful", 200
    else:
        return error, 401

if __name__ == "__main__":
    app.run(debug=True)

