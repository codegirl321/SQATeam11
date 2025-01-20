import unittest
from app import app, db
from models import UserLogin, BlogPost

class FlaskTestCase(unittest.TestCase):
    # This method is called before each test
    def setUp(self):
        # Configure the Flask app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a test database
        self.client = app.test_client()  # This creates a test client to simulate requests

        # Initialize the database tables
        with app.app_context():
            db.create_all()

    # This method is called after each test to clean up
    def tearDown(self):
        # Remove the session and drop all tables
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Test creating a blog post
    def test_create_blog_post(self):
        # Simulate a POST request to create a new blog post
        response = self.client.post('/create', data={
            'title': 'Test Post',
            'content': 'This is a test post',
        })
        # Check that the response status code is 302 (redirect after successful creation)
        self.assertEqual(response.status_code, 302)

    # Test the search functionality
    def test_search_functionality(self):
        # Simulate a GET request to search for posts with the query 'test'
        response = self.client.get('/?search=test')

        # Check if 'Test Post' appears in the search results (it should because we created it)
        self.assertIn('Test Post', response.data.decode())

# This line runs the unit tests
if __name__ == '__main__':
    unittest.main()
