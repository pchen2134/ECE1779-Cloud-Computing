from config import config
from datetime import timedelta, datetime
from operator import itemgetter
from src import s3, cw
import pymysql
import random
from src.instances import get_serving_instances
from src.loadbalancer import register_instance_to_elb, deregister_from_elb


def delete_s3_data():
    bucket = s3.Bucket('odwa')
    bucket.objects.delete()


def delete_rds_data():
    con = pymysql.connect(config.DB_ENDPOINT, config.DB_MASTER,
                          config.DB_PASSWORD, config.DB_NAME)

    with con:
        cur = con.cursor()
        cur.execute("DELETE FROM users")
        cur.execute("DELETE FROM photos")
    

def return_label_values(stats, specification):
    storage_list = []
    for point in stats['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        storage_list.append(["%d:%02d" % (hour, minute), point[specification]])
    storage_list = sorted(storage_list, key=itemgetter(0))
    labels = [
        item[0] for item in storage_list
    ]
    values = [
        item[1] for item in storage_list
    ]
    max_val = 0
    if len(storage_list) != 0:
        max_val = max(storage_list, key=itemgetter(1))[1]

    return labels, values, max_val
