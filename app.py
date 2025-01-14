from flask import Flask, render_template, request, redirect, url_for
from models import BlogPost, UserLogin, db
from login import app, authenticate_user, User, login_manager
from statistics import median, mean
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object('config')  # Load configuration from config.py and particularly the DBMS URI

with app.app_context():
    db.init_app(app)  # It connects the SQLAlchemy db object with the Flask app and the DBMS engine
    db.create_all()  # Create the database tables for all the models

@app.route("/")
def index():
    return render_template("index.html", posts=BlogPost.query.all())

@app.route("/create", methods=["GET"])
def create_post_page():
    return render_template("create.html")

@app.route("/create", methods=["POST"])
def create_post_action():
    post = BlogPost(
        title=request.form["title"],
        content=request.form["content"],
        author=request.form["author"],
    )
    db.session.add(post)
    db.session.commit()
    return redirect(url_for("index"))

#this creates the button for the register page 
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

#process to register a user 
@app.route('/register', methods=['POST'])
def register():
    try:
        # Get the username and password from the form
        username = request.form['username']
        raw_password = request.form['password']

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        # Create a new UserLogin instance
        new_user = UserLogin(username=username, password=hashed_password)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        print(f'Registered new user: {username}')
        return redirect(url_for('user_login_page'))  # Redirect to the login page
    except Exception as error:
        # Handle errors (e.g., username already exists)
        print('Error registering new user:', error)
        return 'An error occurred during registration.', 500


#this creates the button for the login page 
@app.route("/login", methods=["GET"])
def user_login_page():
    return render_template("login.html")

#this creates the login page form 
@app.route("/login", methods=["GET", "POST"])
def user_login_action():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Authenticate the user
        user, error = authenticate_user(username, password)
        if user:
            # Login successful
            return redirect(url_for("index"))
        else:
            # Pass the error message to the template
            return render_template("login.html", error=error)

    # Render the login page with no error by default
    return render_template("login.html", error=None)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template("post.html", post=post)

@app.route("/edit/<int:post_id>", methods=["GET"])
def edit_page(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template("edit.html", post=post)

@app.route("/edit/<int:post_id>", methods=["POST"])
def edit_action(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.title = request.form["title"]
    post.content = request.form["content"]
    db.session.commit()
    return redirect(url_for("post", post_id=post.id))

@app.route("/delete/<int:post_id>", methods=["POST"])
def delete_action(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

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

@app.route('/account')  
def account():  
    user_info = {  
        'username': 'johndoe',  
        'email': 'johndoe@example.com',  
        'creation_date': '2023-01-01'  
    }  
    return render_template('account.html', **user_info)  



if __name__ == "__main__":
    app.run(debug=True)