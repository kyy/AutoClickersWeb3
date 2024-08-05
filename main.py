import logging

from arq import cron, run_worker, Worker
from arq.connections import RedisSettings

from games.captainsbay import process_captainsbay
from games.gemz import process_gemz


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
