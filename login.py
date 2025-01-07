from flask import Flask, request
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt
import requests
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Replace with your actual API key
REST_API_KEY = os.getenv('REST_API_KEY')

# Mock User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_username(username):
        try:
            response = requests.get(
                "sqlite:///db.sqlite3",
                headers={
                    'Content-Type': 'application/json',
                    'x-apikey': REST_API_KEY
                }
            )
            response.raise_for_status()
            users = response.json()
            user_data = next((u for u in users if u['username'] == username), None)
            return user_data
        except Exception as e:
            print(f"Error fetching user by username: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            response = requests.get(
                "https://names-9abc.restdb.io/rest/app-users",
                headers={
                    'Content-Type': 'application/json',
                    'x-apikey': REST_API_KEY
                }
            )
            response.raise_for_status()
            users = response.json()
            user_data = next((u for u in users if u['id'] == user_id), None)
            return user_data
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None

@login_manager.user_loader
def load_user(user_id):
    user_data = User.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['password'])
    return None

def authenticate_user(username, password):
    user_data = User.get_user_by_username(username)
    if not user_data:
        print(f"User {username} not found.")
        return None, "User not found"

    if bcrypt.check_password_hash(user_data['password'], password):
        print(f"Password for {username} is correct.")
        return User(user_data['id'], user_data['username'], user_data['password']), None
    else:
        print(f"Password for {username} is incorrect.")
        return None, "Password incorrect"

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user, error = authenticate_user(username, password)
    if user:
        login_manager.login_user(user)
        return "Login successful", 200
    else:
        return error, 401

if __name__ == "__main__":
    app.run(debug=True)
