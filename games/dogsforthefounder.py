import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@dogs_for_the_founder_bot"
URL = os.getenv(f"{NAME.upper()}_URL")


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)
    try:
        await page.get_by_role("button", name="Собрать").tap()
    except:
        pass
    start_time = time.time()
    duration = 30 * 60
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > duration:
            await browser.close()

        energy_current = await page.locator(
            '//*[@id="root"]/div/div[1]/div/div[7]/div[1]/div/p[1]').text_content()
        energy_current = energy_current.replace("/", "")

        await multy_tap(
            page=page,
            semaphore=2,
            taps=2,
            locator='//*[@id="root"]/div/div[1]/div/div[6]/div/div[2]',
        )

        if int(energy_current) < 10:
            time.sleep(1)
            await browser.close()
            return True


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
    hour={i for i in range(0, 25, 1)},
    minute={5},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    max_tries=3,
    timeout=30 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await refresh_game_url(playwright)


    asyncio.run(main())
