import contextlib
from flask import Blueprint, url_for, render_template, redirect, flash
from src import ec2
from config import config
from src.util import delete_s3_data, delete_rds_data
from src.worker import get_num_workers_30, destroy_a_worker
from src.cpu import get_avg_cpu_utilization_2, get_avg_cpu_utilization_30
from src.instances import get_serving_instances, get_serving_instances


panel_blueprint = Blueprint('panel', __name__)
'''
    control panel
'''


@panel_blueprint.route('/', methods=['GET'])
def index():
    _, num_serving_instance = get_serving_instances()
    avg_cpu_util = get_avg_cpu_utilization_2()
    return render_template('panel.html', num_serving_instance=num_serving_instance, avg_cpu_util=avg_cpu_util)


@panel_blueprint.route('/workers', methods=['GET'])
def list_workers():
    instances = ec2.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': ['worker']}])
    inservice_instances_id, worker_pool_size = get_serving_instances()
    instances_list = []
    for instance in instances:
        tmp_instance = {
            "id": instance.id,
            "public_ip_address": instance.public_ip_address,
            "instance_type": instance.instance_type,
            "availability_zone": instance.placement['AvailabilityZone'],
            "state": instance.state['Name'],
            "inservice": 'Yes' if instance.id in inservice_instances_id else 'No'
        }
        instances_list.append(tmp_instance)
    workerLabels, workerValues, workerMax = get_num_workers_30()
    cpuLabels, cpuValues, cpuMax = get_avg_cpu_utilization_30()
    return render_template('list.html', 
                           instances=instances_list, 
                           worker_pool_size=len(inservice_instances_id),
                           workerLabels=workerLabels,
                           workerValues=workerValues,
                           workerMax=workerMax,
                           cpuLabels=cpuLabels,
                           cpuValues=cpuValues,
                           cpuMax=cpuMax)


@panel_blueprint.route('/delete_data', methods=['POST'])
def delete_data():
    delete_s3_data()
    delete_rds_data()
    flash("All Data Deleted Successfully")
    return redirect(url_for('panel.index'))
 

@panel_blueprint.route('/stop_manager', methods=['POST'])
def stop_manager():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': ['worker']}])
    for instance in instances:
        destroy_a_worker(instance.id)
    
    managers = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': ['Manager']}]
    )
    for manager in managers:
        manager.stop()


@panel_blueprint.route('/autoscaling', methods=['GET'])
def goto_autoscaling():
    return redirect(url_for('autoscaling.index'));


@panel_blueprint.route('/manualscaling', methods=['GET'])
def goto_manualscaling():
    return redirect(url_for('manualscaling.index'))
