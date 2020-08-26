from config import config
from datetime import timedelta, datetime
from flask import redirect, url_for
from src.model import AutoScalingConfig
from src import background_task, cw, app
from celery.task import periodic_task
from celery import Celery
import numpy as np
import random
import math
from src.instances import get_serving_instances, get_non_terminated_instances, has_pending_instances, get_running_instances
from src.cpu import get_single_instance_cpu_util
from src.worker import celery_create_worker, random_destroy_worker


@periodic_task(run_every=timedelta(seconds=60))
def record_serving_instances_avg_cpu_util():
    workers_ids, num_workers = get_serving_instances()

    response = cw.put_metric_data(
        Namespace='AWS/EC2',
        MetricData=[
            {
                'MetricName': 'num-workers-average',
                'Timestamp': datetime.now(),
                'Value': num_workers,
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': 'i-078f69c8c9c0097d6'
                    },
                ],
                'StorageResolution': 60,
                'Unit': 'Count'
            },
        ]
    )
    print('Number of healthy instances: ' + str(num_workers))

    cpu_stats_list = []
    avg_cpu_util = 0

    if num_workers != 0:
        for worker_id in workers_ids:
            cpu_stats = get_single_instance_cpu_util(worker_id, 120)
            if len(cpu_stats) != 0:
                cpu_stats_list.append(np.mean(cpu_stats))
        if len(cpu_stats_list) != 0:
            avg_cpu_util = np.mean(cpu_stats_list)

    response = cw.put_metric_data(
        Namespace='AWS/EC2',
        MetricData=[
            {
                'MetricName': 'avg-cpu-util',
                'Timestamp': datetime.now(),
                'Value': avg_cpu_util,
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': 'i-078f69c8c9c0097d6'
                    },
                ],
                'StorageResolution': 60,
                'Unit': 'Count'
            },
        ]
    )


@periodic_task(run_every=timedelta(seconds=10))
def auto_check_avg_cpu_utilization():
    """
        Only Get The Instances SERVING THE APP, NOT JUST RUNNNING
    """

    with app.app_context():
        autoScalingConfig = AutoScalingConfig.query.first()
        print("auto config:  " + str(autoScalingConfig))
    if not autoScalingConfig:
        return

    if autoScalingConfig.isOn and not has_pending_instances():
        print("auto scaling on")
        # only getting the instances that are serving the app
        _, num_workers = get_serving_instances()
        _, num_running_instances = get_running_instances()

        if num_workers != num_running_instances:
            return
        print('all the created instances in service now!')
        _, num_non_terminated_instances = get_non_terminated_instances()
        # avg util > expand_threshold
        all_has_cpu_util, avg_cpu_util = all_instance_has_valid_cpu_util()
        if not all_has_cpu_util:
            print('newly created worker has no cpu util yet, wait!')
            return
        if avg_cpu_util > autoScalingConfig.expand_threshold:
            if num_non_terminated_instances >= 8:
                print('number of instances created reaches limit !')
                return
            to_create = int(
                math.ceil((autoScalingConfig.expand_ratio - 1) * num_workers))
            if to_create + num_non_terminated_instances >= 8:
                to_create = max(8 - num_non_terminated_instances, 0)
                print("max number of workers reached! only creating {} additional workers".format(
                    to_create))
            print("CPU expand threshold: {} reached ---- creating {} new instances --- expand ratio: {}".format(
                autoScalingConfig.expand_threshold, to_create, autoScalingConfig.expand_ratio))
            for i in range(to_create):
                celery_create_worker()

        elif avg_cpu_util < autoScalingConfig.shrink_threshold:
            to_destroy = int(autoScalingConfig.shrink_ratio * num_workers)
            if to_destroy > 0:
                print("CPU shrink threshold: {} reached ---- destorying {} instances --- shrink ratio: {}".format(
                    autoScalingConfig.shrink_threshold, to_destroy, autoScalingConfig.shrink_ratio))
                random_destroy_worker(to_destroy)
        else:
            print("CPU utilization within range")

    elif has_pending_instances():
        print('there are pending instances')
    else:
        print('auto config is off')


def all_instance_has_valid_cpu_util():
    cpu_stats_list = []
    workers_ids, num_workers = get_serving_instances()

    for worker_id in workers_ids:
        cpu_stats = get_single_instance_cpu_util(worker_id, 120)
        # if this instance does not have utilization, that means it has no service
        print(worker_id)
        print(cpu_stats)
        if len(cpu_stats) == 0:
            print(str(worker_id) + " has no cpu util yet")
            return False, 0

        cpu_stats_list.append(np.mean(cpu_stats))
    avg_cpu_util = np.mean(cpu_stats_list)
    return True, avg_cpu_util
