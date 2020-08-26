from src import cw
from operator import itemgetter
from datetime import timedelta, datetime
from src.model import AutoScalingConfig
from src.instances import get_serving_instances
from src.util import return_label_values
import numpy as np


def get_cpu_utilization_30(id):
    cpu = cw.get_metric_statistics(
        Period=1*60,
        StartTime=datetime.utcnow() - timedelta(seconds=30*60),
        EndTime=datetime.utcnow() - timedelta(seconds=0),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    return return_label_values(cpu, 'Average')


def get_avg_cpu_utilization_30():
    avg_cpu = cw.get_metric_statistics(
        Period=60,
        StartTime=datetime.utcnow() - timedelta(seconds=30*60),
        EndTime=datetime.utcnow() - timedelta(seconds=0),
        MetricName='avg-cpu-util',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': 'i-078f69c8c9c0097d6'}]
    )
    return return_label_values(avg_cpu, 'Average')


def get_single_instance_cpu_util(id, seconds):
    cpu = cw.get_metric_statistics(
        Period=60,
        StartTime=datetime.utcnow() - timedelta(seconds=seconds),
        EndTime=datetime.utcnow() - timedelta(seconds=0),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    cpu_stats = []
    for point in cpu['Datapoints']:
        cpu_stats.append(point['Average'])
    print(cpu_stats)
    return cpu_stats


def get_avg_cpu_utilization_2():
    cpu_stats_list = []
    inservice_instances_id, num_workers = get_serving_instances()
    if len(inservice_instances_id) == 0:
        return
    for instance_id in inservice_instances_id:
        cpu_stats = get_single_instance_cpu_util(instance_id, 120)
        print(str(instance_id) + ": " + str(cpu_stats))
        if len(cpu_stats) != 0:
            cpu_stats_list.append(np.mean(cpu_stats))
    if len(cpu_stats_list) != 0:
        avg_cpu_util = np.mean(cpu_stats_list)
        return avg_cpu_util
    return 
