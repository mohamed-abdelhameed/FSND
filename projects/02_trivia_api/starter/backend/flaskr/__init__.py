import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def getCategories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) == 0:
      abort(404)
    categories_dictionary = { category.id : category.type for category in categories }
    return jsonify({
      'success': True,
      'categories': categories_dictionary
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def getQuestions():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', 0, type=int)
    if category_id!=0 :
      results = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    else :
      results = Question.query.order_by(Question.id).all()
    if len(results) == 0:
      abort(404)
    start = QUESTIONS_PER_PAGE*(page-1)
    end = QUESTIONS_PER_PAGE*page
    total_questions = len(results)
    paginated_results = results[start:end]
    if len(paginated_results) == 0:
      abort(404)
    questions = [question.format() for question in paginated_results]
    categories = Category.query.order_by(Category.id).all()
    categories_dictionary = { category.id : category.type for category in categories }
    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': total_questions,
      'categories': categories_dictionary,
      'current_category': category_id
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def removeQuestion(question_id):
    try:
      question = Question.query.get(question_id)
      db.session.delete(question)
      db.session.commit()
    except:
      abort(422)
    return jsonify({
      'success': True
    })

  '''
  @TODO: 
  Create an endpoint to Overwrite question. 

  TEST: as no frontend for this request , it can be tested only using curl
  example: curl -X PUT -H "Content-Type: application/json" -d '{"question":"What is that ?","answer":"A question","category":1,"difficulty":1}'  http://localhost:3000/questions/23 
  '''
  @app.route('/questions/<question_id>', methods=['PUT'])
  def overwriteQuestion(question_id):
    try:
      data = request.get_json()
      question = data.get('question', None)
      if question is None:
        raise
      answer = data.get('answer', None)
      if answer is None:
        raise
      category = data.get('category', None)
      if category is None:
        raise
      difficulty = data.get('difficulty', None)
      if difficulty is None:
        raise

      question_record = Question.query.get(question_id)
      
      question_record.question = question
      question_record.answer = answer
      question_record.category = category
      question_record.difficulty = difficulty
      db.session.commit()
    except:
      abort(422)
    return jsonify({
      'success': True
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def addQuestion():
    try:
      data = request.get_json()
      question = data.get('question', None)
      if question is None:
        raise
      answer = data.get('answer', None)
      if answer is None:
        raise
      category = data.get('category', None)
      if category is None:
        raise
      difficulty = data.get('difficulty', None)
      if difficulty is None:
        raise

      question = Question(question,answer,category,difficulty)

      db.session.add(question)
      db.session.commit()
    except:
      abort(422)
    return jsonify({
      'success': True
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #edited the endpoints by adding 'searches' to differentiate it from POST request for adding new question
  @app.route('/questions/searches',methods=['POST'])
  def searchQuestions():
    data = request.get_json()
    if data is None:
      abort(400)
    searchTerm = data.get('searchTerm', None)
    if searchTerm is None:
      abort(400)
    results = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).order_by(Question.id).all()
    if len(results) == 0:
      abort(404)
    questions = [question.format() for question in results]
    return jsonify({
      'success': True,
      'questions': questions
    })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<cat_id>/questions')
  def getQuestionsByCategory(cat_id):
    results = Question.query.filter(Question.category == cat_id).order_by(Question.id).all()
    if len(results) == 0:
      abort(404)
    questions = [question.format() for question in results]
    category = Category.query.filter(Category.id == cat_id).order_by(Category.id).one()
    return jsonify({
      'success': True,
      'questions': questions,
      'current_category': category.format()
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def playQuiz():
    data = request.get_json()
    if data is None:
      abort(400)
    print(data)
    previous_questions = data.get('previous_questions')
    quiz_category = data.get('quiz_category')
    if quiz_category.get('id')!=0:
      questions = Question.query.filter(Question.category == quiz_category.get('id')).filter(Question.id.notin_(previous_questions)).all()
    else:
      questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
    if len(questions) == 0:
      abort(404)
    question = random.choice(questions).format()
    
    return jsonify({
      'success': True,
      'question': question
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422
    
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    }), 405
  
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'server error'
    }), 500
    
  return app

    