import logging
import os
import time
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess


COOKIES_FOLDER = r"C:\Users\xibolba\AppData\Local\Google\Chrome\User Data\Default"
TELEGRAM_URL = "https://web.telegram.org/k/#@gemzcoin_bot"
GEMZ_URL = os.getenv("GEMZ_URL")
NAME = "gemz"
TAP_PAUSE = 1000


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=GEMZ_URL, playwright=playwright)

    try:
        await page.get_by_text("claim").tap()
    except:
        await browser.close()

    time.sleep(2)

    while True:
        count = 0
        for i in range(TAP_PAUSE):
            energy_current = await page.locator('xpath=//*[@id="root"]/div/div/div[2]/footer/div[1]/div[1]/div[1]/div[2]/span[1]').text_content()
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


def gemz():
    asyncio.run(main())


async def process_gemz(ctx=None):
    return create_proccess(target=gemz)


if __name__ == '__main__':
    from dotenv_config import l_dot_env

    l_dot_env('../.env')
    TELEGRAM_URL = "https://web.telegram.org/a/"
    PHONE_NUMBER = "375291106914"

    # async def get_refresh_url(playwright: Playwright):
    #     phone = playwright.devices['Pixel 7']
    #     browser = await playwright.chromium.launch(headless=False)
    #     browser_mobile = await browser.new_context(**phone)
    #     page = await browser_mobile.new_page()
    #     await page.goto(TELEGRAM_URL)
    #     time.sleep(7)
    #     await page.locator('xpath=//*[@id="auth-qr-form"]/div/button[1]').tap()  # next
    #     time.sleep(1)
    #     number = page.locator('xpath=//*[@id="sign-in-phone-number"]')  # phone number
    #     await number.clear()
    #     await number.press_sequentially(PHONE_NUMBER)
    #     await page.locator('xpath=//*[@id="auth-phone-number-form"]/div/form/button[1]/div').tap()  # next
    #     await page.locator('xpath=//*[@id="sign-in-code"]').press_sequentially("CODE")
    #     await page.pause()
    #
    #
    #     # return print(await page.frame_locator("iframe").get_by_text("src").text_content())
    #
    #
    # async def go(ctx=None):
    #     async with async_playwright() as playwright:
    #         await get_refresh_url(playwright)
    #
    # asyncio.run(go())











