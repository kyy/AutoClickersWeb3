import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@Yumify_Bot"
URL = os.getenv(f"{NAME.upper()}_URL")


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(
        url=TELEGRAM_URL,
        mobile=False,
        playwright=playwright,
        browser_context={"storage_state": "web_telegram.json"},
    )

    await page.get_by_role("button").filter(has_text="Play").last.click()
    time.sleep(2)
    await page.get_by_role("button", name="Launch").click()

    start_time = time.time()
    duration = 10 * 60

    time.sleep(1)

    iframe = page.frame_locator('iFrame')
    try:
        await iframe.get_by_role("button", name="Thanks").click()
    except:
        pass

    try:
        await iframe.get_by_role("button", name="Collect").click()
    except:
        pass

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > duration:
            await browser.close()

        energy_current = await iframe.locator('//*[@class="h3-digit text-primary"]').last.text_content()

        await iframe.locator('app-clicker-coin').first.click()

        if int(energy_current) < 100:
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

        await page.get_by_role("button").filter(has_text="Play").last.click()
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
    hour={i for i in range(1, 25, 2)},
    minute={44},
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
