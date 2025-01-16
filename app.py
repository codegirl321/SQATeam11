from flask import Flask, render_template, request, redirect, url_for
from models import BlogPost, UserLogin, db
from login import app, authenticate_user, User, login_manager
from statistics import median, mean
from flask_bcrypt import Bcrypt
from flask_login import logout_user


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object('config')  # Load app configuration

# Initialize the app with the database context
with app.app_context():
    db.init_app(app)  # Connect SQLAlchemy with the Flask app
    db.create_all()  # Create database tables for models

# Home route to display all blog posts
@app.route("/")
def index():
    return render_template("index.html", posts=BlogPost.query.all())  # Pass all posts to template

# Route to show the create post form
@app.route("/create", methods=["GET"])
def create_post_page():
    return render_template("create.html")

# Route to handle the creation of a new post
@app.route("/create", methods=["POST"])
def create_post_action():
    post = BlogPost(
        title=request.form["title"],
        content=request.form["content"],
        author=request.form["author"],
    )
    db.session.add(post)  # Add post to database
    db.session.commit()  # Commit changes
    return redirect(url_for("index"))  # Redirect to the home page

# Register user route
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

# Route to handle user registration
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

        return redirect(url_for('user_login_page'))  # Redirect to login page
    except Exception as error:
        return 'An error occurred during registration.', 500  # Handle errors

@app.route("/login", methods=["GET", "POST"])
def user_login_action():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Authenticate the user
        user, error = authenticate_user(username, password)
        if user:
            # Set the 'logged_in' field to True when the user logs in
            user.logged_in = True
            db.session.commit()

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

# Route to show the edit post form
@app.route("/edit/<int:post_id>", methods=["GET"])
def edit_page(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template("edit.html", post=post)

# Route to handle editing a blog post
@app.route("/edit/<int:post_id>", methods=["POST"])
def edit_action(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.title = request.form["title"]
    post.content = request.form["content"]
    db.session.commit()  # Commit changes
    return redirect(url_for("post", post_id=post.id))  # Redirect to updated post

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required  # Ensure user is logged in before editing
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if the logged-in user is the author of the post and is marked as logged in
    if post.user_id != current_user.id or not current_user.logged_in:
        return "You are not authorized to edit this post.", 403  # Forbidden

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()  # Commit the changes to the post
        return redirect(url_for("post", post_id=post.id))  # Redirect to the updated post page

    return render_template("edit.html", post=post)  

# Protect the delete post route with login_required to ensure the user is logged in
@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required  # Ensure the user is logged in before deleting a post
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    # Check if the logged-in user is the author of the post
    if post.user_id != current_user.id:
        return "You are not authorized to delete this post.", 403  # Forbidden

    db.session.delete(post)  # Delete the post
    db.session.commit()  # Commit the changes
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

# Simulated user data for account
user_data = {  
    'username': 'johndoe',  
    'email': 'johndoe@example.com',  
    'creation_date': '2021-01-01',  
    'bio': 'This is my bio.'  
}

# Route to display and update user account
@app.route('/account', methods=['GET', 'POST'])  
def account():  
    if request.method == 'POST':  
        new_bio = request.form.get('bio')  
        if new_bio:  
            user_data['bio'] = new_bio  # Update bio
            return redirect(url_for('account'))  # Redirect to account page
  
    return render_template('account.html', **user_data)  # Render account page

@app.route("/logout")
def logout():
    # Set the 'logged_in' field to False when the user logs out
    current_user.logged_in = False
    db.session.commit()

    # Log the user out via Flask-Login
    logout_user()

    return redirect(url_for("index"))  # Redirect to the homepage after logout

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
