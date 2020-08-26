from flask import Blueprint, request, url_for, render_template, redirect, flash
from src import ec2, cw, elb, background_task, ec2_client, db
from src.model import AutoScalingConfig

autoscaling_blueprint = Blueprint('autoscaling', __name__)
'''
    auto scaling panel
'''

@autoscaling_blueprint.route('/', methods=['GET'])
def index():
    autoScalingConfig = AutoScalingConfig.query.first()
    print(autoScalingConfig)
    return render_template('autoscaling.html', autoScalingConfig=autoScalingConfig)

@autoscaling_blueprint.route('/apply', methods=['POST'])
def apply():
    expand_threshold = request.form.get('expand-threshold')
    shrink_threshold = request.form.get('shrink-threshold')
    expand_ratio = request.form.get('expand-ratio')
    shrink_ratio = request.form.get('shrink-threshold')

    autoScalingConfig = AutoScalingConfig.query.first()
    if not autoScalingConfig:
        new_config = AutoScalingConfig(
            isOn=True, 
            shrink_ratio=shrink_ratio, 
            expand_ratio=expand_ratio, 
            shrink_threshold=shrink_threshold, 
            expand_threshold=expand_threshold)
        db.session.add(new_config)
        db.session.commit()
    else:
        autoScalingConfig.isOn=True
        autoScalingConfig.shrink_ratio = shrink_ratio
        autoScalingConfig.expand_ratio = expand_ratio
        autoScalingConfig.shrink_threshold = shrink_threshold
        autoScalingConfig.expand_threshold = expand_threshold
        db.session.commit()

    flash('new auto scaling policy applied', 'success')
    return redirect(url_for('autoscaling.index'))
