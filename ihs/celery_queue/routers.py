""" Custom routing functions for Celery """
from config import HoleDirection, project, get_active_config

conf = get_active_config()


def hole_direction_router(name, args, kwargs, options, task=None, **kw):
    """ Route tasks based on name and the hole_direction (H or V) given as the first arg in the task signature.

    Results in 6 routable queues:

        Horizontals:
        - ihs-submissions-h
        - ihs-collections-h
        - ihs-deletions-h

        Verticals:
        - ihs-submissions-v
        - ihs-collections-v
        - ihs-deletions-v
    """
    is_horizontal = args[0] == HoleDirection.H.name

    # base queue definitions
    queue_map = {
        "celery_queue.tasks.submit_job": f"{project}-deletions",
        "celery_queue.tasks.collect_job_result": f"{project}-collections",
        "celery_queue.tasks.delete_job": f"{project}-deletions",
    }

    queue_name = queue_map.get(name)

    # append hole direction to the destination queue name
    if queue_name:
        if is_horizontal:
            queue_name += "-h"
        else:
            queue_name += "-v"
    else:
        queue_name = conf.CELERY_DEFAULT_QUEUE

    return {"queue": queue_name}
