import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    drinks_formated = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinks_formated
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    drinks_formated = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_formated
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long(),
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, id):
    drink = Drink.query.filter(
        Drink.id == id).one_or_none()

    if(drink is None):
        abort(404)

    body = request.get_json()
    title = body.get('title', drink.title)
    recipe = body.get('recipe', drink.recipe)

    try:
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()],
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.filter(
            Drink.id == id).one_or_none()

        if(drink is None):
            abort(404)

        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })

    except Exception:
        abort(422)


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


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def AuthError(error):
    return jsonify({
        "success": False,
        "error": error.error['code'],
        "message": error.error['description']
    }), 401
