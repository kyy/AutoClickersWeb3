import logging

from arq import run_worker, Worker

from fu_arq import refresh_url, REDIS_SETTINGS, cron_j


class Work(Worker):
    redis_settings = REDIS_SETTINGS
    functions = [refresh_url]
    cron_jobs = cron_j


def worker():
    logging.getLogger('arq.worker')
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
        # filename='logs/worker.log',
        # filemode='a'
    )
    run_worker(Work)  # noqa


if __name__ == "__main__":
    try:
        worker()
    except (KeyboardInterrupt, SystemExit):
        print("Worker stopped")
