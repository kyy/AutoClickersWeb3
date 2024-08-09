import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess
from games.__const import CRON_RUN_AT_STARTUP_URL, CRON_RUN_AT_STARTUP_TAP

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@CaptainsBayBot"
URL = os.getenv(f"{NAME.upper()}_URL")
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright, timeout=2)

    try:
        await page.locator('//*[@id="app"]/div/div/div/div/div[1]/button').tap()  # clime
    except:

        await page.locator('//*[@id="app"]/div/div/div/div/div[1]/button').tap()  # clime
    time.sleep(10)
    try:
        await page.locator('//*[@id="app"]/div/div/div/div/div[1]/button').tap()  # start mining
    except:

        await page.locator('//*[@id="app"]/div/div/div/div/div[1]/button').tap(timeout=5000)  # start mining


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

        await page.wait_for_selector('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]')
        await page.locator('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]/div[1]/div[2]').click(
            force=True, timeout=3000)
        try:
            await page.locator('xpath=/html/body/div[7]/div/div[2]/button[1]/div').click(force=True,
                                                                                         timeout=3000)  # launch
        except Error:
            pass
        iframe = await page.wait_for_selector('iframe')
        src = await iframe.get_attribute('src')
        await browser.close()
        return src
    elif run is False:
        return False


cron_config: cron = dict(
    coroutine=process,
    hour={i for i in range(0, 25, 4)},
    minute={00},
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
