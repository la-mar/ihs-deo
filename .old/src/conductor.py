




# import asyncio
# from subprocess import call
# from src.tables import Queue


# class endpoint:

#     def __init__(self, apis: list, release_dir: str):
#         self.apis = apis
#         self.dir = release_dir




# def wells_from_queue(n: int = 100):
#     pass


# def download_headers(wells: list):
#     pass



QUEUE_SIZE = 50
CONCURRENCY = 25

ROOT = 'C:\\Users\\svc-auto\\Desktop\\'

def alternator():
    """Infinite generator to alternate between endpoints.
    """

    toggle = True
    while True:
        if toggle:
            toggle = not toggle
            yield 'Release-BF'
        else:
            toggle = not toggle
            yield 'Release-MF'


from itertools import islice
import asyncio
from src.tables import Queue
from random import randint
from subprocess import call
import concurrent.futures
import functools

alt = alternator()


async def run_command(api):

    loop = asyncio.get_running_loop()

    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool,
            functools.partial(call, ['powershell.exe', 'scripts/run', ROOT+next(alt), api])
            # call(['powershell.exe', 'scripts/run', ROOT+next(alt), api])
            )
        return f"{api} ({result})"

async def mycoro(api):
    print(f"Starting {api}")
    # await asyncio.sleep(0)

    c = await run_command(api)
    # c = await run_command('powershell.exe', 'scripts/run', ROOT+next(alt), api)
        # print(f"Finishing {api} ({number})")
    return f"{api} ({c})"



def wells_from_queue(n: int = 100):

    # loop = asyncio.get_running_loop()
    # print('Getting new wells.')
    # func = lambda n: list(Queue.head(n = n).api14.values)

    # with concurrent.futures.ProcessPoolExecutor() as pool:
        # result = await loop.run_in_executor(pool, functools.partial(func, n))
    # result = func(n)

    return list(Queue.head(n = n).api14.values)

# asyncio.BaseEventLoop.run

def corogen():

    queue = wells_from_queue(QUEUE_SIZE)

    while len(queue) > 0:

        if len(queue) < QUEUE_SIZE/2:
                queue =  wells_from_queue(QUEUE_SIZE)


        print(f'Queue size: {len(queue)-1}')
        yield mycoro(queue.pop(0))



def wells_to_coros(wells: list):
        return [mycoro(x) for x in enumerate(wells)]

def add_coros(coros, limit: int = None):

    return [
                asyncio.ensure_future(c)
                for c in islice(coros, 0, limit or QUEUE_SIZE)
            ]

def limited_as_completed(coros, limit):

    futures = add_coros(coros, limit)

    async def first_to_finish():
        while True:
            await asyncio.sleep(0) #! How exactly does this make the routine keep going?
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        newf = next(coros)
                        futures.append(
                            asyncio.ensure_future(newf))
                    except StopIteration as e:
                        pass
                    return f.result()

    while len(futures) > 0:
        yield first_to_finish()


async def print_when_done(tasks, concurrency):
    for res in limited_as_completed(tasks, concurrency):
        print("Result %s" % await res)


# coros = (mycoro(api) for api in wells_from_queue(n = 15))
coros = corogen()

loop = asyncio.get_event_loop()

loop.run_until_complete(print_when_done(coros, CONCURRENCY))

# loop.close()