"""A job to run executable programs."""

from subprocess import call
from collections import namedtuple
import asyncio


ROOT = '\\\\desktop-dellxps\\c$\\Users\\svc-auto\\Desktop'

Service = namedtuple('Service', ['name', 'release_dir', 'api', 'args'])

SERVICES = [
    Service('test-bf-recent', ROOT+'Release-BF', '42383402790000', ['']),
    Service('test-mf-existing', ROOT+'Release-MF', '42383402790000')
]


async def ps_run(service: Service):
        print(args)
        return {'returncode': call(['powershell.exe'] + [x for x in args])}


if __name__ == "__main__":
    # You can easily test this job here
    # job = ps_run('')
    ps_run("dir", "C:\\")
    # ['powershell.exe'] + ['dir']