from config.config import IMAGE_URL_PREFIX
from datetime import datetime
from flask import Blueprint, request, session, url_for, render_template, redirect, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from src import s3, db
from werkzeug.security import generate_password_hash, check_password_hash
from yolo.detect import detect
from ..models import Photo
import boto3
import copy
import cv2
import numpy as np

upload_blueprint = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'}


'''
    uoload route, login required
'''
@upload_blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    success = False
    pic_path = None
    detected_pic_path = None
    if request.method == 'POST':
        if 'myfile' not in request.files:
            flash('No selected file')
            return redirect(request.url)

        file = request.files['myfile']
        if allowed_file(file.filename):
            pic_path, detected_pic_path = db_save_and_s3_save(file)
            success = True
        else:
            flash('Not a valid image file')

    return render_template('upload.html', success=success, pic1=pic_path, pic2=detected_pic_path)


# cite: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


'''
    actual file saving and db saving function
'''


def db_save_and_s3_save(file):
    content = file.read()
    picname = 'user-' + str(current_user.id) + '-' + file.filename
    detected_picname = 'detected-' + picname
    pic_path = IMAGE_URL_PREFIX + picname
    detected_pic_path = IMAGE_URL_PREFIX + detected_picname
    ext = picname[picname.rfind('.'):]

    detected_img = detect(content, ext)
    # save to sql db
    existing_photo = Photo.query.filter_by(picname=picname).first()
    if not existing_photo:
        photo = Photo(userid=current_user.id, picname=picname)
        db.session.add(photo)
        db.session.commit()

    # save to s3
    s3.Bucket('odwa').put_object(Key=picname, Body=content)
    s3.Bucket('odwa').put_object(Key=detected_picname, Body=detected_img)
    return pic_path, detected_pic_path
