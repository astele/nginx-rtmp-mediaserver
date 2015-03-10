# -*- coding: utf-8 -*-
from celery.schedules import crontab

CELERY_TIMEZONE = 'Europe/Moscow'
BROKER_URL = 'redis://redis:6379/1'
CELERY_RESULT_BACKEND = 'redis://redis:6379/1'

CELERYBEAT_SCHEDULE = {
    'every-minute-dates_1': {
        'task': 'tasks.parse-archive-dates',
        'schedule': crontab(minute='*/1'),
    },
    'every-minute-records_2': {
        'task': 'tasks.parse-records-by-date',
        'schedule': crontab(minute='*/1'),
    },
    'daily-clean-media': {
        'task': 'tasks.clean-stale-media',
        'schedule': crontab(hour=8, minute=23),
    },
    'hourly-clean-tmp': {
        'task': 'tasks.clean-tmp-media',
        'schedule': crontab(minute=3),
    },
    'hourly-extract-preview': {
        'task': 'tasks.extract-video-preview',
        'schedule': crontab(minute=5),
    },
}
