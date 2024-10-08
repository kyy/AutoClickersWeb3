import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@ArtiTapBot"


async def run(playwright: Playwright):
    URL = os.getenv(f"{NAME.upper()}_URL")
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)

    try:
        await page.get_by_role("button", name="Claim").tap(timeout=1500)
    except:
        pass
    time.sleep(2)

    for _ in range(4):
        try:
            await page.get_by_role("button").first.tap(timeout=1500)
            time.sleep(1)
        except:
            pass

    await page.get_by_role("button", name="Start").tap()

    start_time = time.time()
    duration = 3 * 60

    while True:
        energy = await page.locator('.user-energy-stat__value').text_content()
        energy = int(energy.split(" / ")[0].replace(" ", ""))
        elapsed_time = time.time() - start_time
        if any([elapsed_time > duration, energy < 50]):
            await browser.close()
        await multy_tap(
            page=page,
            semaphore=10,
            taps=10,
            locator='#canvas',
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
    minute={50},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    timeout=5 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    pass
