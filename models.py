from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import UserMixin  # Import UserMixin

db = SQLAlchemy()

class UserLogin(db.Model, UserMixin):  # Inherit from UserMixin
    id = db.mapped_column(db.Integer, primary_key=True)
    username = db.mapped_column(db.String(100), nullable=False, unique=True)  # Ensure usernames are unique
    password = db.mapped_column(db.Text, nullable=False)
    created_at = db.mapped_column(db.DateTime, default=datetime.utcnow)
    
    # Specify the table name and add extend_existing to resolve any conflicts
    __tablename__ = 'user_login'
    __table_args__ = {'extend_existing': True}  # Allow redefinition if needed

    # This relationship can be left in the BlogPost model, so remove from UserLogin
    # posts = db.relationship('BlogPost', backref='user', cascade='all, delete-orphan', single_parent=True)

    def __str__(self):
        return f'User {self.username} created on {self.created_at:%Y-%m-%d}'

class BlogPost(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    title = db.mapped_column(db.String(100), nullable=False)
    content = db.mapped_column(db.Text, nullable=False)
    created_at = db.mapped_column(db.DateTime, default=datetime.utcnow)
    author = db.mapped_column(db.String(100), nullable=False)

    # Foreign key to link the blog post to a user (author)
    user_id = db.mapped_column(db.Integer, db.ForeignKey('user_login.id'))

    # Relationship to UserLogin model with a unique backref
    user = db.relationship('UserLogin', backref='blog_posts', single_parent=True)

    def __str__(self):
        return f'"{self.title}" by {self.author} ({self.created_at:%Y-%m-%d})'

    @staticmethod
    def get_post_lengths():
        sql = text("SELECT length(title) + length(content) FROM blog_post")
        return db.session.execute(sql).scalars().all()  # Returns just the integers
