from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

class BlogPost(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    title = db.mapped_column(db.String(100), nullable=False)
    content = db.mapped_column(db.Text, nullable=False)
    created_at = db.mapped_column(db.DateTime, default=datetime.utcnow)
    author = db.mapped_column(db.String(100), nullable=False)

    # Foreign key to link the blog post to a user (author)
    user_id = db.mapped_column(db.Integer, db.ForeignKey('user_login.id'))

    # Relationship to UserLogin model
    # This allows accessing the user's blog posts using user.posts
    user = db.relationship('UserLogin', backref='posts', cascade='all, delete-orphan')

    def __str__(self):
        return f'"{self.title}" by {self.author} ({self.created_at:%Y-%m-%d})'

    @staticmethod
    def get_post_lengths():
        # Use raw SQL to get the total length of the title and content of all blog posts
        sql = text("SELECT length(title) + length(content) FROM blog_post")
        return db.session.execute(sql).scalars().all()  # Returns just the integers

class UserLogin(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    username = db.mapped_column(db.String(100), nullable=False, unique=True)  # Ensure usernames are unique
    password = db.mapped_column(db.Text, nullable=False)  # Store hashed passwords, never plain text
    created_at = db.mapped_column(db.DateTime, default=datetime.utcnow)
    logged_in = db.mapped_column(db.Boolean, default=False)  # Add a 'logged_in' field to track login status
    
