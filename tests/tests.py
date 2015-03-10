# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from time import mktime
import os
import shutil
import tempfile
from nose.tools import eq_, ok_, assert_false
from tasks import clean_stale_media, clean_tmp_media, RECORDS_MAX_AGE


class TestTasks(object):
    TEMP_DIR = './tests/testdata'

    def setUp(self):
        if not os.path.exists(self.TEMP_DIR):
            os.mkdir(self.TEMP_DIR)
        os.environ['MEDIA_DIR'] = self.TEMP_DIR

    def tearDown(self):
        try:
            shutil.rmtree(self.TEMP_DIR)
        except OSError:
            pass

    def test_schedule_clean_task(self):
        """
        Тест удаления медиафайлов,
        удаляем все mp4/jpg файлы в соотвествии с расписанием из настроек камеры

        """
        ok_(os.path.exists(self.TEMP_DIR))
        inactive_range = range(21, 24) + range(2, 5)
        active_range = range(13, 16)
        inactive_files = [
            tempfile.NamedTemporaryFile(suffix='_05-03-2015_%d:00.flv' % i, dir=self.TEMP_DIR, delete=False)
            for i in inactive_range
        ]
        active_files = [
            tempfile.NamedTemporaryFile(suffix='_05-03-2015_%d:00.flv' % i, dir=self.TEMP_DIR)
            for i in active_range
        ]

        for tf in inactive_files + active_files:
            ok_(os.path.exists(tf.name))

        clean_stale_media.run()

        for tf in inactive_files:
            assert_false(os.path.exists(tf.name))
        for tf in active_files:
            ok_(os.path.exists(tf.name))

    def test_clean_stale_media(self):
        """
        Тест удаления медиафайлов старше заданного возраста

        """
        ok_(os.path.exists(self.TEMP_DIR))
        actual_date = datetime.now() - timedelta(days=RECORDS_MAX_AGE - 1)
        stale_date = datetime.now() - timedelta(days=RECORDS_MAX_AGE + 1)
        old = tempfile.NamedTemporaryFile(
            suffix='_{}.mp4'.format(stale_date.strftime('%d-%m-%Y_%H:%M')),
            dir=self.TEMP_DIR
        )
        actual = tempfile.NamedTemporaryFile(
            suffix='_{}.mp4'.format(actual_date.strftime('%d-%m-%Y_%H:%M')),
            dir=self.TEMP_DIR
        )
        ok_(os.path.exists(old.name) and os.path.exists(actual.name))

        clean_stale_media.run()

        assert_false(os.path.exists(old.name))
        ok_(os.path.exists(actual.name))

    def test_clean_temp_flv(self):
        """
        Тест удаления временных .flv файлов

        """
        ok_(os.path.exists(self.TEMP_DIR))
        actual = tempfile.NamedTemporaryFile(
            suffix='_{}.flv'.format(datetime.now().strftime('%d-%m-%Y_%H:%M')),
            dir=self.TEMP_DIR
        )
        old_time = datetime.now() - timedelta(hours=3)
        old = tempfile.NamedTemporaryFile(
            suffix='_{}.flv'.format(old_time.strftime('%d-%m-%Y_%H:%M')),
            dir=self.TEMP_DIR
        )
        ok_(os.path.exists(actual.name) and os.path.exists(old.name))

        clean_tmp_media.run()

        assert_false(os.path.exists(old.name))
        ok_(os.path.exists(actual.name))