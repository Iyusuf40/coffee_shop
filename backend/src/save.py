import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all
from .database.models import setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM
SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''


# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks":
    drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def drinks_available(methods=["GET"]):
    try:
        all_drinks = Drink.query.all()
        if not len(all_drinks):
            return jsonify({
                    "success": True,
                    "drinks": None
                }), 200
        drinks = [drink.short() for drink in all_drinks]
        return jsonify({
                "success": True,
                "drinks": drinks
            }), 200
    except Exception as e:
        print(e)
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def details_of_drinks(token):
    try:
        all_drinks = Drink.query.all()
        if not len(all_drinks):
            return jsonify({
                    "success": True,
                    "drinks": "not found"
                }), 200
        print("long")
        drinks = [drink.long() for drink in all_drinks]
        print("lll")
        return jsonify({
                "success": True,
                "drinks": drinks
            }), 200
    except Exception as e:
        print(e)
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks":
    drink} where drink an array containing only the newly
    created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_new_drink(token):
    try:
        title = request.get_json().get("title")
        recipe = request.get_json().get("recipe")
        # print(recipe)
        recipe_list_str = ''
        recipe = f"{recipe}"
        for char in recipe:
            if char == "'":
                recipe_list_str += '"'
            else:
                recipe_list_str += char
        # print(recipe_list_str)
        drink = Drink(title=title, recipe=recipe_list_str)
        drink.insert()
        drinks = Drink.query.filter(Drink.id == drink.id).all()
        new_drink = [drink.long() for drink in drinks]
        return jsonify({
                "success": True,
                "drinks": new_drink
            }), 200
    except Exception as e:
        # print(e)
        abort(422)
   

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink_data(token, id):
    try:
        title = request.get_json().get("title")
        recipe = request.get_json().get("recipe")
        # print(recipe)
        recipe_list_str = ''
        recipe = f"{recipe}"
        for char in recipe:
            if char == "'":
                recipe_list_str += '"'
            else:
                recipe_list_str += char
        # print(id)
        drink = Drink.query.filter(Drink.id == id).first()
        # print(drink.title)
        drink.title = title
        drink.recipe = recipe_list_str
        drink.update()
        drinks = Drink.query.filter(Drink.id == id).all()
        return jsonify({
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            }), 200
    except Exception as e:
        # print(e)
        abort(404)
 

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def remove_drink(token, id):
    try:
        drink = Drink.query.filter(Drink.id == id).first()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
                "success": True,
                "delete": id
            }), 200
    except Exception:
        abort(404)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404



'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def autherror_response(error):
    return jsonify({
        "success": False,
        "error": str(error.status_code),
        "message": str(error.error["code"])
    }), error.status_code


