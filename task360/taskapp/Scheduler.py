import traceback
import logging

from multiprocessing.util import Finalize

from celery.beat import Scheduler
from celery.utils.log import get_logger
from celery.result import AsyncResult

from django_celery_beat.schedulers import DatabaseScheduler
from taskapp.models import MyPeriodicTask


logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info,
                               logger.error, logger.warning)

DEFAULT_MAX_INTERVAL = 5


class DatabaseScheduler(DatabaseScheduler):
    """Database-backed Beat Scheduler."""

    Model=MyPeriodicTask

    def __init__(self, *args, **kwargs):
            """Initialize the database scheduler."""
            self._dirty = set()
            Scheduler.__init__(self, *args, **kwargs)
            self._finalize = Finalize(self, self.sync, exitpriority=5)
            self.max_interval = (
                kwargs.get('max_interval')
                or self.app.conf.beat_max_loop_interval
                or DEFAULT_MAX_INTERVAL)

