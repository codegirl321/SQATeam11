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

    def __str__(self):
        return f'"{self.title}" by {self.author} ({self.created_at:%Y-%m-%d})'
    
    @staticmethod
    def get_post_lengths():
        # An example of how to use raw SQL inside a model
        sql = text("SELECT length(title) + length(content) FROM blog_post")
        return db.session.execute(sql).scalars().all() # Returns just the integers