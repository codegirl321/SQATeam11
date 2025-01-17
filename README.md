# SQATeam11
Software Quality Assurance module work

# Flask Blog Application

This is a simple Flask-based blog application where users can register, log in, create, edit, and delete blog posts. Admin users have access to all blog posts, while regular users can only manage their own posts.

## Features

- **User Registration and Authentication**: Users can register and log in to create and manage their blog posts.
- **Admin Access**: Admin users can view and manage all blog posts.
- **Create, Edit, Delete Posts**: Users can create new blog posts, edit existing posts, and delete them.
- **Post Viewing**: All users can view the blog posts created by others.
- **User-Specific Content**: Users can only edit or delete posts they have created.

## Requirements

- Python 3.x
- Flask
- Flask-Login
- Flask-Bcrypt
- Flask-SQLAlchemy
- SQLite (or any other database supported by SQLAlchemy)

Run the application:

python -m venv venv 
venv\Scripts\activate
pip install -r requirements.txt
flask run
Open your browser and go to http://127.0.0.1:5000/ to start using the application.


Environment Variables
SECRET_KEY: Flask's secret key used for session management. It should be kept secret.
DATABASE_URL: The URL to the database. By default, the app uses SQLite (sqlite:///db.sqlite3).
Application Structure
app.py: Main Flask application file.
models.py: Defines the database models.
templates/: Directory containing HTML templates.
static/: Directory containing static files (CSS, images, JavaScript).
config.py: Configuration settings for the Flask application.
login.py: Handles user authentication logic.
Usage
Register: New users can register by providing a username and password.
Log In: Users can log in using their credentials.
Create a Post: Logged-in users can create blog posts.
Edit a Post: Users can edit posts they have created.
Delete a Post: Users can delete posts they have created.
Admin Access: Admin users can view and manage all posts.
