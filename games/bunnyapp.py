import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@bunnyAppBot"
URL = os.getenv(f"{NAME.upper()}_URL")


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright, timeout=10)

    try:
        await page.get_by_role("button", name="Начать играть").tap()
    except:
        pass

    start_time = time.time()
    duration = 10 * 60
    while True:
        elapsed_time = time.time() - start_time

        energy_current = await page.locator(
            '//*[@id="__nuxt"]/div/main/div/div[5]/div[1]/span').text_content()
        energy_current = int(energy_current.replace(" ", ""))
        await multy_tap(
            page=page,
            semaphore=5,
            taps=5,
            locator='//*[@id="__nuxt"]/div/main/div/div[3]',
        )

        if any([energy_current < 2, elapsed_time > duration]):
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

        await page.get_by_role("button").filter(has_text="Играть").last.click()
        time.sleep(2)
        await page.get_by_role("button", name="Launch").click()

        time.sleep(2)

        iframe = await page.wait_for_selector('iframe')
        src = await iframe.get_attribute('src')
        await browser.close()
        return src
    elif run is False:
        return False


cron_config: cron = dict(
    coroutine=process,
    hour={i for i in range(0, 25, 3)},
    minute={46},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
    timeout=2 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await refresh_game_url(playwright)


    asyncio.run(main())
