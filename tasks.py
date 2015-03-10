# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os
from os.path import splitext
from pprint import pprint
from celery import Celery
from celery.utils.log import get_task_logger
from itertools import chain, ifilter
import redis
import subprocess32

RECORDS_DIR = os.getenv('RECORDS_DIR', '/host_www/media/rec')
RECORDS_MAX_AGE = 30

celery = Celery('tasks')
celery.config_from_object('celeryconfig')
logger = get_task_logger(__name__)
pool = redis.ConnectionPool(host='redis', port=6379, db=0)
r = redis.Redis(connection_pool=pool)


def parse_file_names():
    return [
        base.split('_') for base, ext in
        [os.path.splitext(f) for f in os.listdir(RECORDS_DIR)]
        if ext == '.mp4'
    ]


@celery.task(name='tasks.parse-archive-dates')
def parse_archive_dates():
    logger.info('Parse hourly archives task')
    date_keys = r.keys('dates:*')
    pipe = r.pipeline(transaction=True)
    for key in date_keys:
        pipe.delete(key)

    for d in parse_file_names():
        try:
            pipe.zadd('dates:{site}'.format(site=d[0]), d[3], 0)
            pipe.zadd('dates:{site}:{sp}'.format(site=d[0], sp=d[1]), d[3], 0)
        except IndexError, e:
            logger.warn('Parsing archive dates error: {}: {}'.format('_'.join(d), e.message))

    pipe.execute(raise_on_error=True)


@celery.task(name='tasks.parse-records-by-date')
def parse_records_by_date():
    logger.info('Parse records by date task')
    rec_keys = r.keys('recs:*')
    pipe = r.pipeline(transaction=True)
    for key in rec_keys:
        pipe.delete(key)

    for d in parse_file_names():
        try:
            pipe.sadd(
                'recs:{site}:{rec_date}'.format(site=d[0], rec_date=d[3]),
                d[1].lstrip('sp')
            )
        except IndexError, e:
            logger.warn('Parsing record by date error: {}: {}'.format('_'.join(d), e.message))

    pipe.execute(raise_on_error=True)


@celery.task(name='tasks.clean-stale-media')
def clean_stale_media():
    """
    Формат файла архива: kam_sp100_kamera-1_02-03-2015_23:00.mp4
    """
    start_hour = 8
    end_hour = 21
    for fname in get_media_files():
        try:
            base, ext = os.path.splitext(fname)
            fdatetime = datetime.strptime('_'.join(base.split('_')[-2:]), '%d-%m-%Y_%H:%M')
            fhour = fdatetime.hour
            if fhour not in range(start_hour, end_hour):
                os.remove(fname)
            if (datetime.now() - fdatetime).days > RECORDS_MAX_AGE:
                os.remove(fname)
        except ValueError, e:
            logger.warn(e.message)


def get_media_files(types=[]):
    chkext = None
    if types:
        chkext = lambda x: splitext(x)[1] in types

    for dpath, dirs, files in os.walk(os.getenv('MEDIA_DIR', '/host_www/media')):
        for fname in ifilter(chkext, files):
            yield os.path.join(dpath, fname)


@celery.task(name='tasks.clean-tmp-media')
def clean_tmp_media():
    max_hours = 1
    for fname in get_media_files(types=['.flv']):
        try:
            base, ext = os.path.splitext(fname)
            fdatetime = datetime.strptime('_'.join(base.split('_')[-2:]), '%d-%m-%Y_%H:%M')
            if fdatetime < datetime.now() - timedelta(hours=max_hours):
                os.remove(fname)
        except ValueError, e:
            logger.warn(e.message)


@celery.task(name='tasks.extract-video-preview')
def extract_video_preview():
    try:
        subprocess32.call('/host_bin/extract_preview.sh', shell=False)
    except OSError, e:
        logger.error(e.message)