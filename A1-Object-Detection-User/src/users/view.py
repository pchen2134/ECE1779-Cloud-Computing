from flask import jsonify, Blueprint, request, session, url_for, render_template, redirect, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from .form import SignupForm, LoginForm
from ..models import User, Photo
from src import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config.config import IMAGE_URL_PREFIX

user_blueprint = Blueprint('users', __name__)

'''
    sign up route
'''
@user_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == "POST":
        if form.validate():
            can_register = register(request.form['password'], request.form['username'])
            if can_register:
                return (redirect(url_for('users.login')))

            flash('A user already exists with that name.')

    return render_template('/signup.html', form=form)


'''
    log in route
'''
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if current_user.is_authenticated:
        return redirect(url_for('users.gallery'))
    if request.method == "POST":
        if form.validate():
            if login(request.form['password'], request.form['username']):
                return redirect(url_for('users.profile'))
                    
            flash('Invalid username/password combination')
    return render_template('login.html', form=form)

'''
    user's gallery route, login required
'''
@user_blueprint.route('/gallery', methods=['GET'])
@login_required
def gallery():
    picnames = get_picnames()
    return render_template("gallery.html", picnames=picnames, prefix=IMAGE_URL_PREFIX)


'''
    log out route, login required
'''
@user_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing.landing'))


'''
    profile route, login required
'''
@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', user=current_user.username)


'''
    img route, login required
'''
@user_blueprint.route('/img/<string:picname>', methods=['GET'])
@login_required
def img(picname):
    picnames = (IMAGE_URL_PREFIX + picname,
                IMAGE_URL_PREFIX + 'detected-' + picname)
    return render_template("img.html", picnames=picnames)

'''
    actual register helper function
'''
def register(password, username):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user is None:
        user = User(username=username,
                    password_hash=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return True
    return False


'''
    actual log in helper function
'''
def login(password, username):
    # check username
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        if check_password_hash(existing_user.password_hash, password):
            login_user(existing_user)
            return True
    return False


'''
    helper function for getting all uploaded pic names of a user
'''
def get_picnames():
    picnames = Photo.query.with_entities(Photo.picname).filter_by(userid=current_user.id).all()
    return picnames
