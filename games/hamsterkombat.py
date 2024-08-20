import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_URL, CRON_RUN_AT_STARTUP_TAP

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@hamster_kombat_bot"
URL = os.getenv(f"{NAME.upper()}_URL")
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright, timeout=3)

    try:
        await page.locator('//*[@id="__nuxt"]/div/div[3]/div[2]/div[2]/div/button').tap()  # clime
    except:
        await browser.close()

    while True:
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator('//*[@id="__nuxt"]/div/main/div[2]/div[3]/div[2]/div/p').text_content()
            energy_current = energy_current.split(" ")[0]

            await multy_tap(
                page=page,
                semaphore=3,
                taps=3,
                locator='//*[@id="__nuxt"]/div/main/div[2]/div[3]/button',
            )

            count += 1

            if count == TAP_PAUSE - 1:
                time.sleep(1)
            if int(energy_current) < 10:
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
    hour={i for i in range(0, 25, 4)},
    minute={39},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    max_tries=3,
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
