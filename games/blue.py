import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@bluefarming_bot"
URL = os.getenv(f"{NAME.upper()}_URL")


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)

    await page.get_by_role("link", name="missions").tap()
    time.sleep(2)

    ad_count = await page.locator('//*[@id="root"]/div[2]/div/div[2]/div[1]/div/div/div/div/span[1]').text_content()
    ad_count = int(ad_count.split("/")[0].replace("[", ""))

    if ad_count > 0:
        for _ in range(ad_count):
            await page.locator('//*[@id="root"]/div[2]/div/div[2]/div[1]/div/div/button').tap()
            time.sleep(1)
            try:
                await page.get_by_role("button").filter(has_text="ok").tap(timeout=500)
            except:
                pass
            finally:
                await page.locator('//*[@id="root"]/div[2]/div/div[2]/div[1]/div/div/button').tap()

            time.sleep(20)
            await page.locator('//*[@id="root"]/div[2]/div/div[2]/div[1]/div/div/button').tap()
            time.sleep(3)
            try:
                await page.get_by_role("button").filter(has_text="reward").tap(timeout=500)
            except:
                pass


    start_time = time.time()
    duration = 10 * 60
    await page.get_by_role("link", name="home").tap()
    while True:
        energy = await page.locator('//*[@id="root"]/div[2]/div/div/div[1]/div/span/span').text_content()
        energy = int(energy)

        elapsed_time = time.time() - start_time

        if any([elapsed_time > duration, energy < 10]):
            await page.get_by_role("button").filter(has_text="claim").tap()
            time.sleep(2)
            await browser.close()

        await multy_tap(
            page=page,
            semaphore=20,
            taps=2,
            locator='//*[@id="root"]/div[2]/div/div/div[2]/div/div[1]',
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
    hour={i for i in range(0, 25, 12)},
    minute={50},
    run_at_startup=True,
    timeout=5 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    pass
