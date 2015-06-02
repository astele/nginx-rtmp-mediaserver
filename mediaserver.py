# -*- coding: utf-8 -*-
# @-k gevent
from datetime import datetime

from flask import Flask, jsonify, abort
from redis import StrictRedis

app = Flask(__name__)
redis = StrictRedis(host='redis', port=6379)


@app.route('/api/archive_dates/<site>/')
@app.route('/api/archive_dates/<site>/spid/<spid>/')
def point_webcam_list(site, spid=None):
    if spid:
        res = redis.zrange('dates:{site}:sp{spid}'.format(site=site, spid=spid), 0, -1)
        return jsonify(result=res)

    res = redis.zrange('dates:{site}'.format(site=site), 0, -1)
    return jsonify(result=res)

    # return Response(response=dumps(res),
    #                 status=200,
    #                 mimetype="application/json")


@app.route('/api/archive_hours/<site>/<webcam>/<rec_date>/')
def hours_by_date(site, webcam, rec_date):
    res = []
    try:
        date = datetime.strptime(rec_date, '%Y-%m-%d').date()
        res = redis.zrange(
            'hours:{site}:{webcam}:{date:%d-%m-%Y}'.format(
                site=site, webcam=webcam, date=date
            ), 0, -1
        )
    except ValueError:
        abort(400, u'Incorrect date format')

    return jsonify(result=res)


@app.route('/api/points_by_date/<site>/<rec_date>/')
def points_by_date(site, rec_date):
    res = []
    try:
        date = datetime.strptime(rec_date, '%Y-%m-%d').date()
        res = redis.smembers(
            'recs:{site}:{date:%d-%m-%Y}'.format(site=site, date=date)
        )
    except ValueError:
        abort(400, u'Incorrect date format')

    return jsonify(result=list(res))

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5011, debug=True)
