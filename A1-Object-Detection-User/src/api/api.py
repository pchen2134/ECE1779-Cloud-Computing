from src import app
from flask import request, jsonify, Blueprint
from ..users.view import register, login
from ..upload.view import db_save_and_s3_save, allowed_file
from datetime import datetime

api_blueprint = Blueprint('api', __name__)


'''
api route for register
'''
@api_blueprint.route('/register', methods=['POST'])
def api_register():
    username = request.form['username']
    password = request.form['password']
    if register(password, username):
        return jsonify({
            "status": 200,
            "text": "New User {} created".format(username)
        }), 200
    else:
        return jsonify({
            "status": 400,
            "text": "Register Failed. User Already Exists"
        }), 400


'''
api route for upload
'''
@api_blueprint.route('/upload', methods=['POST'])
def api_upload():
    username = request.form['username']
    password = request.form['password']
    file = request.files['file']
    if login(password, username):
        if allowed_file(file.filename):
            db_save_and_s3_save(file)
            return jsonify({
                "status": 200,
                "text": "photo uploaded"
            }), 200
        else:
            return jsonify({
                "status": 400,
                "text": "file extension not correct"
            }), 400
    else:
        return jsonify({
            "status": 400,
            "text": "Log in failed"
        }), 400

