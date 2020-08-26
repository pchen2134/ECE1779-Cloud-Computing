import os

AMI = 'ami-094bdacfc0033e7a8'
SECURITY_GROUP_IDS = ['sg-05313bb3ee1f2de47']
# CELERY CONFIG
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# IAM ROLE
IAM_INSTANCE_PROFILE = {
    'Arn': 'arn:aws:iam::177015545031:instance-profile/FULL_ACCESS',
    'Name': 'FULL_ACCESS'
}
# LOAD BALANCER
TARGET_GROUP_ARN = 'arn:aws:elasticloadbalancing:us-east-1:177015545031:targetgroup/odwa-group/6ed093f9ee3e5568'
# RDS CONFIG
DB_PASSWORD = 'WBGCI3ElWecukBooRzaH'
DB_ENDPOINT = 'odwa-db.c8he8i54iqnw.us-east-1.rds.amazonaws.com'
DB_MASTER = 'admin'
DB_NAME = 'odwadb'
# APPLICATION SECRET
SECRET_KEY = 'odwa'
BASEDIR = os.path.abspath(os.path.dirname(__file__ + "/../../"))
# LOCAL SQL LITE DB FOR AUTO SCALING CONFIG
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL') or 'sqlite:///' + os.path.join(BASEDIR, 'AUTOCONFIG.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
STARTUP_SCRIPT = """#cloud-config
runcmd:
 - cd /home/ubuntu/ODWA
 - sudo apt-get update
 - sudo apt-get install -y uwsgi
 - sudo apt-get install uwsgi-plugin-python3
 - sudo apt-get install python3-pip
 - sudo pip3 install -r requirements.txt
 - uwsgi uwsgi.ini --plugin python3 --uid ubuntu --binary-path /home/ubuntu/.local/bin/uwsgi --logto mylog.log
"""
