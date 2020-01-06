import logging
import os
import shutil
import subprocess
import sys
from collections import defaultdict

import click
from flask.cli import AppGroup, FlaskGroup

import loggers
from api.models import *
from config import get_active_config
from ihs import create_app

logger = logging.getLogger()


CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"], ignore_unknown_options=False
)
STATUS_COLOR_MAP = defaultdict(
    lambda: "white",
    {"success": "green", "error": "red", "timeout": "yellow", "failed": "red"},
)

conf = get_active_config()
app = create_app()
cli = FlaskGroup(create_app=create_app, context_settings=CONTEXT_SETTINGS)
run_cli = AppGroup("run")
test_cli = AppGroup("test")
delete_cli = AppGroup("delete")


def update_logger(level: int):
    if level is not None:
        loggers.config(level=level)


def get_terminal_columns():
    return shutil.get_terminal_size().columns


def hr():
    return "-" * get_terminal_columns()


@cli.command()
def ipython_embed():
    """Runs a ipython shell in the app context."""
    try:
        import IPython
    except ImportError:
        click.echo("IPython not found. Install with: 'pip install ipython'")
        return
    from flask.globals import _app_ctx_stack

    app = _app_ctx_stack.top.app
    banner = "Python %s on %s\nIPython: %s\nApp: %s%s\nInstance: %s\n" % (
        sys.version,
        sys.platform,
        IPython.__version__,
        app.import_name,
        app.debug and " [debug]" or "",
        app.instance_path,
    )

    ctx = {}

    # Supports the regular Python interpreter startup script if it's being used
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup, "r") as f:
            eval(compile(f.read(), startup, "exec"), ctx)  # pylint: disable=eval-used

    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def web(args):
    cmd = ["gunicorn", "wsgi",] + list(args)
    subprocess.call(cmd)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("celery_args", nargs=-1, type=click.UNPROCESSED)
def worker(celery_args):
    cmd = ["celery", "-E", "-A", "celery_queue.worker:celery", "worker",] + list(
        celery_args
    )
    subprocess.call(cmd)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("celery_args", nargs=-1, type=click.UNPROCESSED)
def cron(celery_args):
    cmd = ["celery", "-A", "celery_queue.worker:celery", "beat",] + list(celery_args)
    subprocess.call(cmd)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("celery_args", nargs=-1, type=click.UNPROCESSED)
def monitor(celery_args):
    cmd = ["celery", "-A", "celery_queue.worker:celery", "flower",] + list(celery_args)
    subprocess.call(cmd)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("task")
def task(task: str):
    "Run a one-off task. Pass the name of the scoped task to run.  Ex. endpoint_name.task_name"
    from celery_queue.tasks import sync_endpoint

    endpoint, task = task.split(".")
    if not endpoint or not task:
        click.secho("endpoint name is missing. try specifying ENDPOINT_NAME.TASK_NAME")
        sys.exit(0)
    # sync_endpoint.apply((endpoint, task), countdown=3)
    sync_endpoint.delay(endpoint, task)


@delete_cli.command(context_settings=dict(ignore_unknown_options=True))
def exports():
    """ Purge all completed exports from the backing IHS remote account"""

    from celery_queue.tasks import cleanup_remote_exports

    cleanup_remote_exports.run()


@test_cli.command()
def sentry():
    import sentry

    conf.SENTRY_ENABLED = True
    conf.SENTRY_EVENT_LEVEL = 10
    sentry.load()
    logger.error("Sentry Integration Test")


@test_cli.command()
def smoke_test():
    from celery_queue.tasks import smoke_test

    result = smoke_test()
    assert result == "verified"
    print(result)


def main(argv=sys.argv):  # pylint: disable=unused-argument
    """
    Args:
        argv (list): List of arguments
    Returns:
        int: A return code
    Does stuff.
    """

    cli()
    return 0


# @cli.command()
# def test():
#     """Runs the tests without code coverage"""
#     tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         return 0
#     sys.exit(result)


# @cli.command()
# def cov():
#     """Runs the unit tests with coverage."""
#     tests = unittest.TestLoader().discover('project/tests')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         COV.stop()
#         COV.save()
#         print('Coverage Summary:')
#         COV.report()
#         COV.html_report()
#         COV.erase()
#         return 0
#     sys.exit(result)

cli.add_command(run_cli)
cli.add_command(test_cli)
cli.add_command(delete_cli)


if __name__ == "__main__":
    cli()
