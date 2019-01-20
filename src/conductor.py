




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



QUEUE_SIZE = 3

ROOT = '\\\\desktop-dellxps\\c$\\Users\\svc-auto\\Desktop\\Release-BF'


from itertools import islice
import asyncio
from src.tables import Queue
from random import randint
from subprocess import call

async def mycoro(number, api):
    print(f"Starting {api} ({number})")
    await asyncio.sleep(0)
    c = call(['powershell.exe', 'scripts/run', ROOT, api])
        # print(f"Finishing {api} ({number})")
    return f"{api} ({number}) [{c}]"



def wells_from_queue(n: int = 100):

    return list(Queue.head(n = n).api14.values)




async def wells_to_coros(wells: list):
        return [mycoro(i, x) for i, x in enumerate(wells)]

def add_coros(coros, limit: int = None):
    return [
                asyncio.ensure_future(c)
                for c in islice(coros, 0, limit or QUEUE_SIZE)
            ]

def limited_as_completed(coros, limit):
    futures = add_coros(coros, limit)
    # [
    #     asyncio.ensure_future(c)
    #     for c in islice(coros, 0, limit)
    # ]
    async def first_to_finish():
        while True:
            if len(futures) < QUEUE_SIZE:
                pass
                #! Re-enable
                # print(f'futures length: {len(futures)}')
                # coros.append( await wells_to_coros(wells_from_queue(n = QUEUE_SIZE - len(futures))))
                # print(new)
                # await futures.append(add_coros(new))
            # else:
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


async def print_when_done(tasks):
    for res in limited_as_completed(tasks, 3):
        print("Result %s" % await res)


coros = (mycoro(randint(1, 10), x) for i, x in enumerate(wells_from_queue(n = 100)))

loop = asyncio.get_event_loop()

loop.run_until_complete(print_when_done(coros))

# loop.close()