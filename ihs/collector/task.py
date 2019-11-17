from typing import Union, List, Dict
from celery.schedules import crontab


class OptionMatrix:
    def __init__(self, matrix: dict = None, **kwargs):
        # self.matrix = matrix if isinstance(matrix, list) else [matrix or {}]
        self.matrix = matrix or {}
        self.kwargs = kwargs

    def __repr__(self):
        return str(self.to_list())

    def __iter__(self):
        for d in self._cross_apply():
            yield d

    def _cross_apply(self) -> List[Dict]:
        if len(self.matrix):
            values = [
                {"name": key, **self.kwargs, **value}
                for key, value in self.matrix.items()
            ]
        else:
            values = [self.kwargs or {}]

        return values

    def to_list(self) -> List[Dict]:
        return self._cross_apply()


class Task:
    """ A yaml defined task object to be passed to Celery """

    def __init__(
        self,
        model_name: str,
        task_name: str,
        cron: dict = None,
        seconds: int = None,
        mode: str = None,
        options: dict = None,
        enabled: bool = True,
        **kwargs,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.cron = self.parse_cron(cron or {})
        self.seconds = seconds
        self.mode = mode
        self.options = OptionMatrix(**(options or {}))
        self.enabled = enabled

        if not any([self.cron, self.seconds]):
            raise ValueError("Either seconds or cron must be specified")

    def __repr__(self):
        status = "***DISABLED***" if not self.enabled else ""
        s = self.schedule
        sch = (
            f"{s._orig_minute} {s._orig_hour} {s._orig_day_of_week} {s._orig_day_of_month} {s._orig_month_of_year}"
            if self.seconds is None
            else f"({self.schedule} seconds)"
        )
        return f"{status} {self.qualified_name} {sch}"

    @property
    def qualified_name(self):
        return f"{self.model_name}/{self.task_name}"

    @property
    def schedule(self) -> Union[crontab, int]:
        """ The scheduling expression to be used for task creation. Prefers seconds over cron expressions. """
        return self.seconds or self.cron

    @staticmethod
    def parse_cron(cron: dict):
        """ Return a crontab object if the passed dict has any non-null values """
        notnull = {k: v for k, v in cron.items() if v is not None}
        if len(notnull) > 0:
            return crontab(**notnull)
        else:
            return None


if __name__ == "__main__":

    from config import get_active_config
    from attrdict import AttrDict

    conf = get_active_config()
    endpoints = conf.endpoints
    tasks = endpoints.wells.tasks
    # t = AttrDict(list(tasks.items())[1][1])
    t = tasks.driftwood
    task = Task("wells", "sync", **t)
    to = task.options
    print(to)

