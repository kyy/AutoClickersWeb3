import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@kolo"


async def run(playwright: Playwright):
    URL = os.getenv(f"{NAME.upper()}_URL")
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)

    try:
        await page.get_by_role("button").filter(has_text="claim").tap()
    except:
        pass

    try:
        await page.get_by_role("button", name="skip").tap()
    except:
        pass

    start_time = time.time()
    duration = 4 * 60

    elapsed_time = time.time() - start_time

    for i in range(200):
        if elapsed_time > duration:
            await browser.close()

        await multy_tap(
            page=page,
            semaphore=2,
            taps=2,
            locator='g:nth-child(7) > image',
        )

    try:
        for _ in range(7):
            await page.get_by_role("button").filter(has_text="yes").tap()
            time.sleep(2)

    except:
        pass
    finally:
        await page.get_by_role("button").filter(has_text="claim").tap()

    await browser.close()


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
    hour={i for i in range(0, 25, 8)},
    minute={26},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    timeout=4 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await refresh_game_url(playwright)


    asyncio.run(main())
