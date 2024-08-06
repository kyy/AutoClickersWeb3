import logging

from arq import cron, run_worker, Worker
from arq.connections import RedisSettings
from fu import get_fu_process


class Work(Worker):
    redis_settings = RedisSettings(host='127.0.0.1', port=6379)

    functions = []
    cron_jobs = [cron(**i) for i in get_fu_process()]


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
