import logging
import os
import time
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess

"""
https://web.telegram.org/k/#@CaptainsBayBot
"""

PIRATE_BAY_URL = os.getenv("CAPTAINSBAY_URL")
NAME = "captainsbay"
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=PIRATE_BAY_URL, playwright=playwright)

    while True:
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator('xpath=//*[@id="app"]/div/div/div/main/div[1]/div/div[4]/div/div[3]/span[1]/span[2]/span[1]').text_content()
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


def captainsbay():
    asyncio.run(main())


async def process_captainsbay(ctx=None):
    return create_proccess(target=captainsbay)


if __name__ == '__main__':
    from dotenv_config import l_dot_env
    l_dot_env('../.env')
