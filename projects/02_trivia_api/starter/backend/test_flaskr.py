import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(os.environ['DB_User'], os.environ['DB_Password'],'localhost:5432', self.database_name)
        # username and password read from environment variables
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Test get categories get request"""
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        """Test get questions get request"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        
    def test_get_questions_bad_page(self):
        """Test get questions get request with bad page parameter"""
        res = self.client().get('/questions?page=100000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_questions_bad_current_category(self):
        """Test get questions get request with bad current category parameter"""
        res = self.client().get('/questions?category_id=100000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_remove_question(self):
        """Test remove question delete request"""
        res = self.client().delete('/questions/23')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_remove_question_bad_parameter(self):
        """Test remove question delete request with bad parameter"""
        res = self.client().delete('/questions/100000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
    
    def test_add_question(self):
        """Test add question post request"""
        res = self.client().post('/questions',json={'question':'what\'s your name ?','answer':'Mohamed','category':1,'difficulty':1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_add_question_bad_request(self):
        """Test add question bad post request"""
        res = self.client().post('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_add_question_missed_parameter(self):
        """Test add question post request with missing parameter"""
        res = self.client().post('/questions',json={'answer':'Mohamed','category':1,'difficulty':1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
    
    def test_overwrite_question(self):
        """Test overwrite question put request"""
        res = self.client().put('/questions/5',json={'question':'what is your age ?','answer':'30','category':5,'difficulty':5})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_overwrite_question_bad_request(self):
        """Test overwrite question bad put request"""
        res = self.client().put('/questions/5')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        """Test search questions post request"""
        res = self.client().post('/questions/searches', json={'searchTerm':'title'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_search_questions_bad_request(self):
        """Test search questions bad post request"""
        res = self.client().post('/questions/searches', json={'searchTerm':'!@#$%^'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_questions_missed_parameter(self):
        """Test search questions post request with missing parameter"""
        res = self.client().post('/questions/searches')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
    
    def test_get_questions_by_catergory(self):
        """Test get questions by category get request"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_by_catergory_bad_parameter(self):
        """Test get questions by category get request with bad parameter"""
        res = self.client().get('/categories/100000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        """Test play quiz post request"""
        res = self.client().post('/quizzes', json={'previous_questions':[],'quiz_category':{'type':'All','id':0}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))

    def test_play_quiz_with_missing_parameter(self):
        """Test play quiz post request with missing parameters"""
        res = self.client().post('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
    
    def test_play_quiz_bad_parameter(self):
        """Test play quiz post request with bad parameter"""
        res = self.client().post('/quizzes', json={'previous_questions':[],'quiz_category':{'type':'Fake','id':100000}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()