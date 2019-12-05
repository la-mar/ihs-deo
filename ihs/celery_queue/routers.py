""" Custom routing functions for Celery """
from config import HoleDirection, project, get_active_config

conf = get_active_config()

# base queue definitions
QUEUE_MAP = {
    "celery_queue.tasks.submit_job": f"{project}-submissions",
    "celery_queue.tasks.collect_job_result": f"{project}-collections",
    "celery_queue.tasks.delete_job": f"{project}-deletions",
}


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

    queue_name = conf.CELERY_DEFAULT_QUEUE

    # route to hole_dir specific queue, if hole_dir was passed as routing key
    if args:
        is_horizontal = args[0] == HoleDirection.H.name

        mapped_queue = QUEUE_MAP.get(name)

        # append hole direction to the destination queue name
        if mapped_queue:
            if is_horizontal:
                mapped_queue += "-h"
            else:
                mapped_queue += "-v"

            queue_name = mapped_queue

    return {"queue": queue_name}
