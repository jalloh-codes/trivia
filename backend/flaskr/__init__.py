import os
from flask import Flask, request, abort, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, data):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * 10
    end = start + 10

    questions = [question.format() for question in data]
    current_question =  questions[start:end]
    return current_question

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/':{'origins': '*'}})

  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categoris():
    categories =  Category.query.all()
    if categories is None:
      abort(404)
  
    categories_data = {}
    for category in categories:
      categories_data[category.id] = category.type

    return jsonify({
      'success': True,
      'categories': categories_data #{category.id: category.type for category in categories}
    })
  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''


  @app.route('/questions', methods=['GET'])
  def get_questions():

    questions =  Question.query.order_by(Question.id).all()
    categories =  Category.query.order_by(Category.id).all()
    current_questions = paginate(request, questions)


    if questions is None:
      abort(404)

    current_questions
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': {category.id: category.type for category in categories},
    })

  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      del_question = Question.query.get(question_id)
      del_question.delete()
      questions = Question.query.order_by(Question.id).all()
      if del_question is None:
        abort(404)
      return jsonify({
        'success': True,
        'deleted': question_id,
        'total_questions': len(questions),
      })
    except:
      abort(422)


  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    question = body.get('question')
    answer = body.get('answer')
    difficulty =  body.get('difficulty')
    category = body.get('category')

    if(question == '' or answer == '' or difficulty == '' or category == ''):
      return jsonify({
        'success': False,
        'massage': 'Empty field'
      }), 422 
    try:
      Question(question, answer, difficulty, category).insert()
      return jsonify({
        'success': True,
        'message': 'Question created!'
      }), 200
    except:
      abort(422)

  '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    
    word = request.get_json().get('searchTerm')
    if len(word) == 0:
      abort(422)
    try:
      search_question = Question.query.filter(Question.question.ilike(f'%{word}%')).all()
      return jsonify({
        'success': True,
        'questions': paginate(request, search_question),
        'total_questions': len(search_question),
        'total_questions': None
      }), 200
    except:
      abort(404)
    

  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  #____________ quetions by category______________#
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def questions_by_category(category_id):

    categor = Category.query.get(category_id);
    questions =  Question.query.filter_by(category=categor.type).all()
  
    if categor is None or questions is None:
      abort(422)
    try:
      return jsonify({
        'success': True,
        'questions': paginate(request, questions),
        'total_questions': len(questions),
        'current_category': category_id
      }), 200
    except:
      abort(404)
    #order_by(Question.id).filter(Question.category == category.type)




  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  #____________ quiz route______________#
  @app.route('/quizzes', methods=['POST'])
  def get_quiz():
    body  =  request.get_json()
    category = body.get('quiz_category')
    previous_questions =  body.get('previous_questions')

    if(category is None or previous_questions is None):
      abort(422)
 
   
    if  category['type'] == 'click':
      available_q =  Question.query.filter(
        Question.id.notin_((previous_questions))).all()
  
    else:
      available_q =  Question.query.filter_by(
        category= category['type']).filter(Question.id.notin_((previous_questions))).all()
   

    new_q =  available_q[random.randrange(
      0, len(available_q))].format() if len(available_q) > 0 else None

    try:
      return jsonify({
        'success': True,
        'question': new_q
      }), 200
    except:
      abort(422)




      

  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  #____________ error handleing______________#
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'data not found'
    })
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable entity'
    })

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'server error'
    })


  return app

# export FLASK_APP=flaskr 
# export FLASK_ENV=development