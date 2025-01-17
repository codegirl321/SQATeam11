from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from models import BlogPost, UserLogin, db
from login import authenticate_user  # Import the authenticate_user function
from statistics import median, mean
from sqlalchemy.exc import IntegrityError  # Import IntegrityError for database constraint violations

# Initialize the Flask app
app = Flask(__name__)

app.config.from_object('config')  # Ensure secret key is loaded from config

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize Flask-Login for managing user sessions
login_manager = LoginManager()
login_manager.init_app(app)

# Configure login view
login_manager.login_view = 'user_login_action'  # Redirect to login page if user is not logged in

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return UserLogin.query.get(int(user_id))  # Retrieve user by ID

# Initialize the app with the database context
with app.app_context():
    db.init_app(app)
    db.create_all()  # Create database tables for models

# Home route to display all blog posts
@app.route("/")
def index():
    return render_template("index.html", posts=BlogPost.query.all())  # Pass all posts to template

# Route to show the create post form
@app.route("/create", methods=["GET"])
def create_post_page():
    return render_template("create.html")

@app.route("/create", methods=["POST"])
def create_post_action():
    title = request.form["title"]
    content = request.form["content"]
    author = current_user.username  # Use current_user's username for the author field

    post = BlogPost(
        title=title,
        content=content,
        author=author,  # Set the author to the current user's username
        user_id=current_user.id  # Link the post to the current logged-in user
    )
    db.session.add(post)  # Add post to database
    db.session.commit()  # Commit changes
    return redirect(url_for("index"))  # Redirect to the home page

# Register user route (GET)
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

# Route to handle user registration (POST)
@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        raw_password = request.form['password']

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        # Create a new user and add to the database
        new_user = UserLogin(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('user_login_action'))  # Redirect to login page
    except IntegrityError:
        db.session.rollback()  # Rollback the transaction if a database error occurs
        error_message = "Username already exists. Please choose a different one."
        return render_template("register.html", error=error_message)  # Return with error message
    except Exception as error:
        db.session.rollback()  # Rollback for any other unexpected errors
        return f'An error occurred during registration: {error}', 500  # Handle errors gracefully

# User login route (GET and POST)
@app.route("/login", methods=["GET", "POST"])
def user_login_action():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Authenticate the user
        user, error = authenticate_user(username, password)  # Use the imported authenticate_user function
        if user:
            # Log the user in via Flask-Login
            login_user(user)

            return redirect(url_for("index"))  # Redirect to the homepage after successful login
        else:
            return render_template("login.html", error=error)

    return render_template("login.html", error=None)

# Route to display individual blog post
@app.route("/post/<int:post_id>")
def post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template("post.html", post=post)

# Route to show the edit post form (GET)
@app.route("/edit/<int:post_id>", methods=["GET"])
def edit_page(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template("edit.html", post=post)

# Route to show the edit post form (GET) and handle editing (POST)
@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required  # Ensure user is logged in before editing
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if the logged-in user is the author of the post
    if post.user_id != current_user.id:
        return "You are not authorized to edit this post.", 403  # Forbidden

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()  # Commit changes to the post
        return redirect(url_for("post", post_id=post.id))  # Redirect to the updated post page

    return render_template("edit.html", post=post)

# Route to handle editing a blog post (POST)
@app.route("/edit/<int:post_id>", methods=["POST"])
@login_required  # Ensure user is logged in before editing
def edit_action(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.title = request.form["title"]
    post.content = request.form["content"]
    db.session.commit()  # Commit changes
    return redirect(url_for("post", post_id=post.id))  # Redirect to updated post

# Protect the delete post route with login_required to ensure the user is logged in
@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required  # Ensure the user is logged in before deleting a post
def delete_post(post_id):  # Ensure the route function name is delete_post
    post = BlogPost.query.get_or_404(post_id)

    # Check if the logged-in user is the author of the post
    if post.user_id != current_user.id:
        return "You are not authorized to delete this post.", 403  # Forbidden

    db.session.delete(post)  # Delete the post
    db.session.commit()  # Commit changes
    return redirect(url_for("index"))  # Redirect to the home page

# Route to display post statistics
@app.route("/stats")
def stats():
    post_lengths = BlogPost.get_post_lengths()

    return render_template(
        "stats.html",
        average_length=mean(post_lengths),
        median_length=median(post_lengths),
        max_length=max(post_lengths),
        min_length=min(post_lengths),
        total_length=sum(post_lengths),
    )

# Account route
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # Retrieve all the posts created by the current user
    user_posts = BlogPost.query.filter_by(user_id=current_user.id).all()

    return render_template('account.html', posts=user_posts)

@app.route("/logout")
def logout():
    logout_user()  # Flask-Login will handle session termination
    return redirect(url_for("index"))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
