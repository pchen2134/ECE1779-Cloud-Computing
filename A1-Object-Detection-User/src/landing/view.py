from flask import Blueprint, request, session, url_for, render_template, redirect
from flask_login import login_required, current_user
from datetime import datetime
landing_blueprint = Blueprint('landing', __name__)
'''
    Landing Page
'''
@landing_blueprint.route('/')
def landing():
    return render_template('landing.html', current_user=current_user)
