from arq import create_pool, cron
from arq.connections import RedisSettings
from dotenv import set_key
from playwright.async_api import async_playwright
from tqdm import tqdm

from fu import get_fu_refresh_game_urls_name, get_fu_process

REDIS_SETTINGS = RedisSettings(host='127.0.0.1', port=6379)

cron_j = [cron(**i) for i in get_fu_process()]


async def refresh_url(ctx, src, name):
    if src != "" and src is not False:
        set_key(dotenv_path=".env", key_to_set=name.upper() + "_URL",
                value_to_set=src.replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios"))
    elif src == "":
        pass
    elif src is False:
        pass


async def refresh_all_url_job(ctx):
    redis = await create_pool(REDIS_SETTINGS)

    async with async_playwright() as playwright:
        for fu_name in tqdm(get_fu_refresh_game_urls_name(), desc='refresh_all_url_job'):
            try:
                fu, name = fu_name
                src: str = await fu(playwright)
                await redis.enqueue_job(
                    'refresh_url',
                    src, name,
                    # _job_try=3,
                )
            except Exception as e:
                print(name, e)


cron_j.append(
    cron(
        coroutine=refresh_all_url_job,
        hour={23},
        minute={55},
        run_at_startup=True,
        max_tries=3,
        timeout=60 * 60,
        unique=True,
        name='refresh_urls',
        job_id=f'rfrsh_urls_001',
    ),
)
