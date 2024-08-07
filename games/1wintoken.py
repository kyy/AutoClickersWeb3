import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess
from games.__const import CRON_RUN_AT_STARTUP

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@token1win_bot"
URL = os.getenv(f"{NAME.upper()}_URL")
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)

    await page.locator('//*[@id="root"]/div[1]/div/button').tap(force=True)  # continue
    time.sleep(0.25)
    await page.locator('//*[@id="root"]/div[1]/div/button').tap(force=True)  # continue
    time.sleep(0.25)
    await page.locator('//*[@id="root"]/div[1]/div/button').tap(force=True)  # continue
    time.sleep(1)
    try:
        await page.locator('//*[@id="root"]/div[3]/div/div/div[4]/div/button').tap(force=True)  # get money
    except:
        pass
    time.sleep(1)
    try:
        await page.locator('//*[@id="root"]/div[3]/div/div/div[4]/div/button').tap(force=True)  # close
    except:
        pass
    time.sleep(1)
    try:
        await page.locator('//*[@id="root"]/div[3]/div/div/div[4]/div/button').tap(force=True)  # close
    except:
        pass
    while True:
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator(
                'xpath=//*[@id="root"]/div[1]/div/footer/div[1]/div/div/div/div/span[1]').text_content()
            count += 1
            await page.locator('xpath=//*[@id="root"]/div[1]/div/main/div/div[3]').tap(force=True)
            if count == TAP_PAUSE - 1:
                time.sleep(1)
            if energy_current == "1":
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
    time.sleep(1)
    await page.wait_for_selector(
        'xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]')
    await page.locator(
        'xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]/div[1]').click()  # burger
    time.sleep(0.25)
    await page.locator(
        'xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[1]/div/div[2]/div/div[3]').click()  # start
    time.sleep(0.25)
    await page.locator(
        'xpath=//*[@class="bubbles-group bubbles-group-last"]/div/div/div[2]/div[1]/button/div').click()  # run
    time.sleep(0.25)
    await page.locator(
        'xpath=/html/body/div[7]/div/div[2]/button[1]/div').click()  # accept run

    iframe = await page.wait_for_selector('iframe')
    src = await iframe.get_attribute('src')
    await browser.close()
    return src


cron_config: cron = dict(
    coroutine=process,
    hour={i for i in range(1, 24, 4)},
    minute={00},
    run_at_startup=CRON_RUN_AT_STARTUP,
    max_tries=3,
    timeout=30 * 60,
    unique=True,
    name=NAME,
    job_id=f'{NAME}_001',
)

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await run(playwright)


    asyncio.run(main())
