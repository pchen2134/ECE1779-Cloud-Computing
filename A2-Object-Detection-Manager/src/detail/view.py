from flask import Blueprint, url_for, render_template, redirect
from src import ec2, cw
from operator import itemgetter
from datetime import timedelta, datetime
from config import config
from src.worker import get_http_rate, destroy_a_worker
from src.cpu import get_cpu_utilization_30


detail_blueprint = Blueprint('detail', __name__)

@detail_blueprint.route('/<id>', methods=['GET'])
def worker_view(id):
    instance = ec2.Instance(id)
    CPUlabels, CPUvalues, CPUmax = get_cpu_utilization_30(id)
    HTTPlabels, HTTPvalues, HTTPmax = get_http_rate(id)
    return render_template('detail.html', title='Instance Info', 
        CPUlabels=CPUlabels, 
        CPUvalues=CPUvalues, 
        CPUmax=CPUmax, 
        HTTPlabels=HTTPlabels,
        HTTPvalues=HTTPvalues,
        HTTPmax=HTTPmax,
        instance=instance)



@detail_blueprint.route('/delete/<id>', methods=['POST'])
def destroy_worker(id):
    destroy_a_worker(id)
    return redirect(url_for('panel.list_workers'))


@detail_blueprint.route('/delete/all', methods=['POST'])
def destroy_all():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': ['worker']}])
    for instance in instances:
        destroy_a_worker(instance.id)
    return redirect(url_for('panel.list_workers'))





