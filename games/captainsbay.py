import logging
import os
import time

from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess

NAME = "captainsbay"
TELEGRAM_URL = "https://web.telegram.org/k/#@CaptainsBayBot"
URL = os.getenv(f"{NAME.upper()}_URL")
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)

    while True:
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator(
                'xpath=//*[@id="app"]/div/div/div/main/div[1]/div/div[4]/div/div[3]/span[1]/span[2]/span[1]'
            ).text_content()
            count += 1

            await page.locator('//*[@id="tap-zone"]/div[1]/div').tap(force=True)

            if count == TAP_PAUSE - 1:
                time.sleep(1)
            if energy_current == "1":
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


async def refresh_game_url(playwright: Playwright):
    """
    :param playwright:
    :return: обновляем ссылки игр содержащих временный токен
    """

    browser, page = await start_page_at_phone(
        url=TELEGRAM_URL,
        mobile=False,
        playwright=playwright,
        browser_context={"storage_state": "web_telegram.json"}
    )
    time.sleep(1)
    await page.wait_for_selector('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]')
    await page.locator('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]/div[1]/div[2]').click()
    try:
        await page.locator('xpath=/html/body/div[7]/div/div[2]/button[1]/div').click()  # launch
    except Error:
        pass
    iframe = await page.wait_for_selector('iframe')
    src = await iframe.get_attribute('src')
    await browser.close()
    return src


cron_config: cron = dict(
    coroutine=process,
    hour={i for i in range(1, 24, 3)},
    minute={00},
    run_at_startup=False,
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
