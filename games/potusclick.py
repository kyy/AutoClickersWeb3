import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_URL, CRON_RUN_AT_STARTUP_TAP

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@potusclick_bot"
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    URL = os.getenv(f"{NAME.upper()}_URL")
    browser, page = await start_page_at_phone(url=URL, playwright=playwright, timeout=3)
    start_time = time.time()
    duration = 20 * 60
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > duration:
            await browser.close()
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator('//*[@id="app"]/div[1]/main/section/div[3]/div[3]/span').text_content()
            energy_current = energy_current.split("/")[0]

            await multy_tap(
                page=page,
                semaphore=3,
                taps=3,
                locator='//*[@id="app"]/div[1]/main/section/div[3]/button/div[1]',
            )

            count += 1

            if count == TAP_PAUSE - 1:
                time.sleep(1)
            if int(energy_current) < 15:
                time.sleep(1)
                await browser.close()
                return True


async def main(ctx=None):
    try:
        async with async_playwright() as playwright:
            await run(playwright)
    except Error as e:
        logging.error(f"{NAME} >> {e}")


def game():
    asyncio.run(main())


async def process(ctx=None):
    return create_proccess(target=game)


async def refresh_game_url(playwright: Playwright, run=CRON_RUN_AT_STARTUP_URL):
    """
    :param playwright:
    :return: обновляем ссылки игр содержащих временный токен
    """
    if run is True:
        browser, page = await start_page_at_phone(
            url=TELEGRAM_URL,
            mobile=False,
            playwright=playwright,
            browser_context={"storage_state": "web_telegram.json"},
        )
        return await get_canonic_full_game_url(page, browser)
    elif run is False:
        return False


cron_config: cron = dict(
    coroutine=process,
    hour={i for i in range(0, 25, 2)},
    minute={39},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    timeout=5 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await refresh_game_url(playwright)


    asyncio.run(main())
