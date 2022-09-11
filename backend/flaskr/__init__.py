import json
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from collections import defaultdict
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [q.format() for q in selection]
    current_questions = questions[start:end]

    return current_questions

# https://www.codegrepper.com/code-examples/python/how+to+set+an+empty+array+in+python+of+a+key-value+pair
def formated_categories():
    data = Category.query.order_by(Category.id).all()
    categories = defaultdict(list)
    for category in data:
        categories[category.id] = (category.type)
    return categories

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r'/*' : {'origins':'*'}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def categories_list():
        
        try:
            categories = formated_categories()
            return jsonify({
            'categories': categories
            })
        except:
            abort(404)
        
        



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        questions = Question.query.order_by(Question.id).all()
        # formated_question = [ q.format() for q in questions ]
        current_questions = pagination_questions(request, questions)        
        categories = formated_categories()

        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': categories,
            'current_category': 'ALL'
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            
            question.delete()
            return jsonify({
                'success': True
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def post_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)

            if search_term is not None:
                questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).\
                    order_by(Question.id).all()
                if len(questions) == 0:
                    abort(404)
                paginated_questions = pagination_questions(request, questions)
                return jsonify({
                    'success': True,
                    'questions': paginated_questions,
                    'totalQuestions': len(questions),
                    'currentCategory': 'ALL'
                })
            else:
                question_to_submit = Question(
                    question=question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty
                )
                question_to_submit.insert()
                return jsonify({
                    'success': True
                })
        except:
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id)\
            .order_by(Question.id).all()
        current_questions = pagination_questions(request, questions)
        current_category = Category.query.get(category_id)
        return jsonify({
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': current_category.type
            })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def create_quiz():
        try:
            data = request.get_json()
            question = None
            questions = None
            category_id = data.get('quiz_category', None).get('id')
            previous_question = data.get('previous_questions')
            category = Category.query.filter(Category.id == category_id).one_or_none()
            if category is None:
                questions = Question.query.filter(Question.id.not_in(previous_question)).all()
            else:
                questions = Question.query.filter(Question.category == category_id)\
                    .filter(Question.id.not_in(previous_question)).all()
            
            if len(questions) != 0:
                random_question = random.choice(questions)
                question = random_question.format()

            # previous_question = [ q.id for q in questions]
            return jsonify({
                'previousQuestions': previous_question,
                'question': question
            })
        except:
            abort(400)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                'success': False,
                'error': 400,
                'message': 'Bad Request'
            }),
            400
        )
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                'success': False,
                'error': 404,
                'message': 'Resource Not Found'
            }),
            404
        )
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                'success': False,
                'error': 422,
                'message': 'Unprocessable'
            }),
            422
        )
    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({
                'success': False,
                'error': 500,
                'message': 'Internal Server Error'
            }),
            500
        )

    return app

