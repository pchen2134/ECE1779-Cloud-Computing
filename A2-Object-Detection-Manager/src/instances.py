from src import ec2, cw
from datetime import timedelta, datetime
from src.model import AutoScalingConfig
import src.loadbalancer as Loadbalancer


def get_all_instances():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': ['worker']}])
    return instances, len(set(instances))


def get_running_instances():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']},
                 {'Name': 'tag:Name', 'Values': ['worker']}])
    return instances, len(set(instances))


def get_non_terminated_instances():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending', 'shutting-down']},
                 {'Name': 'tag:Name', 'Values': ['worker']}])
    return instances, len(set(instances))


def has_pending_instances():
    instances = list(ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['pending']},
                 {'Name': 'tag:Name', 'Values': ['worker']}]))
    if len(instances) == 0:
        return False
    return True


def get_serving_instances():
    response = Loadbalancer.health_check()
    inservice_instances_id = set()
    for instance in response:
        if instance['TargetHealth']['State'] == 'healthy':
            inservice_instances_id.add(instance['Target']['Id'])
        if instance['TargetHealth']['State'] == 'draining' or instance['TargetHealth']['State'] == 'unhealthy':
            print(str(instance['Target']['Id']) + " is " +
                  instance['TargetHealth']['State'])
            
    return inservice_instances_id, len(inservice_instances_id)
