import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess
from games.__const import CRON_RUN_AT_STARTUP

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@gemzcoin_bot"
URL = os.getenv(f"{NAME.upper()}_URL")
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)
    await page.wait_for_selector('//*[@id="root"]/div/div/div[1]/div/div/div/div/div[2]')
    await page.locator('//*[@id="root"]/div/div/div[1]/div/div/div/div/div[2]/div').tap(force=True, timeout=3000)

    try:
        await page.locator('xpath=//*[@id="root"]/div/div/div[1]/div/div/div/img').tap(force=True,
                                                                                       timeout=1000)  # закрыть окно с приглашением
    except:
        pass

    await asyncio.sleep(1)

    while True:
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator(
                'xpath=//*[@id="root"]/div/div/div[2]/footer/div[1]/div[1]/div[1]/div[2]/span[1]').text_content()
            count += 1
            await page.locator('xpath=//*[@id="coin"]/div[1]').tap(force=True)
            if count == TAP_PAUSE - 1:
                time.sleep(1)
            if energy_current[0] == "1":
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
    await asyncio.sleep(0.5)
    await page.wait_for_selector('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]')
    await page.locator('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]/div[1]/div[2]').click(
        force=True, timeout=3)
    try:
        await page.locator('xpath=/html/body/div[7]/div/div[2]/button[1]/div').click(force=True, timeout=1)  # launch
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
    run_at_startup=True,
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
