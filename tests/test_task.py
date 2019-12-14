import pytest  # pylint: disable=unused-import


from collector.task import Task
from celery.schedules import crontab


class TestTask:
    def test_create_task_with_seconds(self):
        Task("wells", "test_task", seconds=60)

    def test_create_task_with_cron(self):
        cron = dict(minute="*/1")
        t = Task("wells", "test_task", cron=cron)
        assert t.cron == crontab(minute="*/1")

    def test_overlapping_definition(self):
        cron = dict(minute="*/1")
        t = Task("wells", "test_task", seconds=60, cron=cron)
        assert t.schedule == 60
