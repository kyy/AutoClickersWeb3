import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@Doginhood_bot"
URL = os.getenv(f"{NAME.upper()}_URL")


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)
    try:
        await page.get_by_role("button").filter(has_text="tap").tap()
    except:
        pass

    start_time = time.time()
    duration = 10 * 60

    while True:

        elapsed_time = time.time() - start_time
        energy = await page.locator('//*[@id="tabs-navigation"]/div[1]/p').text_content()
        energy = int(energy.split("/")[0])
        if (elapsed_time > duration) or (energy < 10):
            await browser.close()
        try:
            await multy_tap(
                page=page,
                semaphore=10,
                taps=10,
                locator='//*[@id="game_wrapper"]/button',
            )
        except:
            try:
                await page.locator('//*[@id="game_wrapper"]/div[1]/button').tap()
            except:
                await page.reload()


async def main():
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
    minute={2},
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
