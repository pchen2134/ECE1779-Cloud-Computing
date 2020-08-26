from src import ec2, elb, ec2_client, cw, background_task
from config import config
from src.model import AutoScalingConfig
from datetime import timedelta, datetime


def health_check():
    response = elb.describe_target_health(
        TargetGroupArn=config.TARGET_GROUP_ARN)
    return response['TargetHealthDescriptions']


def deregister_from_elb(id):
    elb.deregister_targets(
        TargetGroupArn=config.TARGET_GROUP_ARN,
        Targets=[
            {
                'Id': id,
                'Port': 5000,
            },
        ]
    )


@background_task.task
def register_instance_to_elb(id):
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[id])

    IAMresponse = ec2_client.associate_iam_instance_profile(
        IamInstanceProfile=config.IAM_INSTANCE_PROFILE,
        InstanceId=id
    )

    ELBresponse = elb.register_targets(
        TargetGroupArn=config.TARGET_GROUP_ARN,
        Targets=[
            {
                'Id': id,
                'Port': 5000,
            }
        ],
    )
    print('instances registered to elb!')
