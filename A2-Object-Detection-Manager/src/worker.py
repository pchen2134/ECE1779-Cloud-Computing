from config import config
from datetime import timedelta, datetime
from src import ec2, cw
from src.instances import get_serving_instances
from src.loadbalancer import register_instance_to_elb, deregister_from_elb
from src.util import return_label_values
import random


def celery_create_worker():
    startup_script = config.STARTUP_SCRIPT
    instance = ec2.create_instances(
        ImageId=config.AMI,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.small',
        UserData=startup_script,
        KeyName='odwa',
        SecurityGroupIds=config.SECURITY_GROUP_IDS,
        TagSpecifications=[{'ResourceType': 'instance',
                            'Tags': [{'Key': 'Name', 'Value': 'worker'}]}],
        Monitoring={'Enabled': True}
    )[0]

    print('new instance created!')
    register_instance_to_elb.apply_async(args=[instance.id])


def random_destroy_worker(to_destroy):
    print("destroying worker!")
    workers_id, num_running_workers = get_serving_instances()

    if num_running_workers == 0:
        return False
    else:
        workers_to_destroy_id = random.sample(workers_id, to_destroy)
        for worker_id in workers_to_destroy_id:
            destroy_a_worker(worker_id)


def destroy_a_worker(id):
    deregister_from_elb(id)
    instance = list(ec2.instances.filter(InstanceIds=[id]))[0]
    instance.terminate()


def get_num_workers_30():
    workers = cw.get_metric_statistics(
        Period=1*60,
        StartTime=datetime.utcnow() - timedelta(seconds=30*60),
        EndTime=datetime.utcnow() - timedelta(seconds=0),
        MetricName='num-workers-average',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': 'i-078f69c8c9c0097d6'}]
    )

    return return_label_values(workers, 'Average')


def get_http_rate(id):
    http = cw.get_metric_statistics(
        Period=1*60,
        StartTime=datetime.utcnow() - timedelta(seconds=30*60),
        EndTime=datetime.utcnow() - timedelta(seconds=0),
        MetricName='httpRequestRate',
        Namespace='AWS/EC2',
        Statistics=['Sum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    return return_label_values(http, 'Sum')
