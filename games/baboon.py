import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@TheBaboon_Bot"


async def run(playwright: Playwright):
    URL = os.getenv(f"{NAME.upper()}_URL")
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)
    try:
        await page.get_by_role("button").filter(has_text="получить").tap()
    except:
        pass

    try:
        await page.get_by_role("link", name="Приз").tap()
        time.sleep(1)
        await page.get_by_role("button").filter(has_text="получить").tap()
    except:
        pass

    start_time = time.time()
    duration = 5 * 60
    energy = await page.locator('//*[@id="root"]/main/div/div[3]/button[2]/div/div').text_content()
    energy = energy.split(".")[0]
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > duration:
            await browser.close()
        await multy_tap(
            page=page,
            semaphore=10,
            taps=10,
            locator='//*[@id="root"]/main/div/div[2]/button/div[2]/div',
        )


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
    minute={23},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    timeout=10 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await refresh_game_url(playwright)


    asyncio.run(main())
