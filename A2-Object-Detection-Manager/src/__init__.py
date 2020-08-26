__author__ = 'victor Cheng, Pengyu Chen, Fang Zhou'

import boto3
from flask import Flask
from config import config
from celery import Celery
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
background_task = Celery(app.name, broker=config.CELERY_BROKER_URL)
ec2 = boto3.resource('ec2', region_name='us-east-1')
ec2_client = boto3.client('ec2', region_name='us-east-1')
cw = boto3.client('cloudwatch', region_name='us-east-1')
elb = boto3.client('elbv2', region_name='us-east-1')

s3 = boto3.resource('s3', region_name='us-east-1')
db = SQLAlchemy()


def create_app():
    app.config.from_object('config.config')
    background_task.conf.update(app.config)
    db.init_app(app)

    with app.app_context():
        from .detail.view import detail_blueprint
        from .panel.view import panel_blueprint
        from .autoscaling.view import autoscaling_blueprint
        from .manualscaling.view import manualscaling_blueprint
        # register blueprints
        app.register_blueprint(detail_blueprint, url_prefix='/detail')
        app.register_blueprint(autoscaling_blueprint,
                               url_prefix='/autoscaling')
        app.register_blueprint(panel_blueprint, url_prefix='/panel')
        app.register_blueprint(manualscaling_blueprint,
                               url_prefix='/manualscaling')
        db.drop_all()
        db.create_all()
        return app


app = create_app()
