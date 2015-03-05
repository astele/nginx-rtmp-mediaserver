# -*- coding: utf-8 -*-
import os
from celery import Celery
from celery.utils.log import get_task_logger
import redis


celery = Celery('tasks')
celery.config_from_object('celeryconfig')
logger = get_task_logger(__name__)
pool = redis.ConnectionPool(host='redis', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
fname_parts = [
        base.split('_') for base, ext in
        [os.path.splitext(f) for f in os.listdir('/host_www/media/rec')]
        if ext == '.mp4'
    ]


@celery.task(name='tasks.parse-archive-dates')
def parse_archive_dates():
    logger.info('Parse hourly archives task')

    date_keys = r.keys('dates:*')
    pipe = r.pipeline(transaction=True)
    for key in date_keys:
        pipe.delete(key)

    [pipe.zadd('dates:{site}'.format(site=d[0]), d[3], 0) for d in fname_parts]
    [pipe.zadd('dates:{site}:{sp}'.format(site=d[0], sp=d[1]), d[3], 0) for d in fname_parts]
    pipe.execute(raise_on_error=True)


@celery.task(name='tasks.parse-records-by-date')
def parse_records_by_date():
    logger.info('Parse records by date task')

    rec_keys = r.keys('recs:*')
    pipe = r.pipeline(transaction=True)
    for key in rec_keys:
        pipe.delete(key)

    [
        pipe.sadd(
            'recs:{site}:{rec_date}'.format(site=d[0], rec_date=d[3]),
            d[1].lstrip('sp')
        ) for d in fname_parts
    ]
    pipe.execute(raise_on_error=True)


@celery.task(name='clean_stale_media')
def clean_stale_media():
    pass
