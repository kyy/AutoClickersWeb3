import logging
import os

from arq import cron, run_worker, Worker
from arq.connections import RedisSettings

from games.captainsbay import process_captainsbay
from games.gemz import process_gemz


PATH_TO_GAMES = "games"


def games_fu():
    """
    :return: импортируем функции
    """
    files = os.listdir(PATH_TO_GAMES)
    fu = [i.split(".")[0] for i in files if "__" not in i]

    games = {}
    for module_name in fu:
        try:
            module = __import__(PATH_TO_GAMES + "." + module_name)
            func = getattr(module, module_name)
            games[module_name] = func
        except Exception as e:
            logging.warning(f"не удалось импортировать i >> {e}")
    return games


class Work(Worker):
    redis_settings = RedisSettings(host='127.0.0.1', port=6379)

    functions = []

    cron_jobs = [
        cron(process_captainsbay,
             hour={i for i in range(1, 24, 3)},
             minute={00},
             run_at_startup=True,
             max_tries=3,
             timeout=30*60,
             unique=True,
             ),

        cron(process_gemz,
             hour={i for i in range(1, 24, 2)},
             minute={00},
             run_at_startup=True,
             max_tries=3,
             timeout=60*60,
             unique=True,
             ),
    ]


def worker():
    logging.getLogger('arq.worker')
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
        filename='logs/worker.log',
        filemode='a'
    )
    run_worker(Work)  # noqa


if __name__ == "__main__":
    try:
        worker()
    except (KeyboardInterrupt, SystemExit):
        print("Worker stopped")
