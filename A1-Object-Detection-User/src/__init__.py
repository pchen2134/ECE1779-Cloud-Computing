__author__ = 'Pengyu Chen'

import boto3
import threading
import os
from celery import Celery
from config import config
from datetime import timedelta, datetime
from flask import Flask, render_template, jsonify, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_session import Session
from yolo.yolo import init_yolo
from src.util import record_http_request


app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()
s3 = boto3.resource('s3')
cw_client = boto3.client('cloudwatch', region_name='us-east-1')
net, LABELS, COLORS = init_yolo()
lock = threading.Lock()
instanceId = os.popen('ec2metadata --instance-id').read().strip()
print(instanceId)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.config')
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)
        print('request!!')
        record_http_request(datetime.now(), instanceId, cw_client)
    # Initialize Plugins
    db.init_app(app)
    Bootstrap(app)
    login_manager.init_app(app)

    with app.app_context():
        from .landing.view import landing_blueprint
        from .users.view import user_blueprint
        from .upload.view import upload_blueprint
        from .api.api import api_blueprint

        # register blueprints
        app.register_blueprint(landing_blueprint)
        app.register_blueprint(user_blueprint, url_prefix='/users')
        app.register_blueprint(upload_blueprint)
        app.register_blueprint(api_blueprint, url_prefix='/api')
        # Create Database Models
        db.create_all()

        return app


app = create_app()
