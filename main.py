import logging

from arq import cron, run_worker, Worker
from arq.connections import RedisSettings
from fu import get_fu_process, refresh_all_games_urls


class Work(Worker):
    redis_settings = RedisSettings(host='127.0.0.1', port=6379)

    functions = []
    cron_jobs = [cron(**i) for i in get_fu_process()] + [
        cron(
            coroutine=refresh_all_games_urls,
            hour={1},
            minute={1},
            run_at_startup=False,
            max_tries=3,
            timeout=30 * 60,
            unique=False,
            name='refresh_urls',
            job_id=f'rfrsh_urls_001',
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
