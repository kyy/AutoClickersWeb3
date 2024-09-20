import logging
import os
import time
from arq import cron
from playwright.async_api import async_playwright, Playwright, Error
import asyncio
from fu import start_page_at_phone, create_proccess, multy_tap, get_canonic_full_game_url
from games.__const import CRON_RUN_AT_STARTUP_TAP, CRON_RUN_AT_STARTUP_URL

NAME = __name__.split('.')[-1]
TELEGRAM_URL = "https://web.telegram.org/k/#@Frogmates_bot"
URL = os.getenv(f"{NAME.upper()}_URL")


async def run(playwright: Playwright):
    browser, page = await start_page_at_phone(url=URL, playwright=playwright)

    start_time = time.time()
    duration = 10 * 60

    try:
        await page.get_by_role("link", name="Rewards").tap()
        await page.get_by_role("button", name="Claim Now").tap()
    except:
        pass

    await page.get_by_role("link", name="Boost").tap()
    try:
        turbo_count = await page.locator(
            '//*[@id="swagger-ui"]/div[2]/div[2]/div[1]/div/div[1]/div[2]/span[2]').text_content()
        turbo_count = int(turbo_count.split("/")[0])
    except:
        turbo_count = 0

    await page.get_by_role("link", name="Play").tap()

    while True:
        elapsed_time = time.time() - start_time

        if turbo_count > 1:
            try:
                await page.get_by_role("link", name="Boost").tap()
                await page.locator('//*[@id="swagger-ui"]/div[2]/div[2]/div[1]/div/div[1]/div[2]/span[2]').tap()
                time.sleep(1)
                await page.get_by_role("button", name="Get").tap()
            except:
                pass
            finally:
                turbo_count -= 1

        if elapsed_time > duration:
            await browser.close()

        await page.get_by_role("link", name="Play").tap()
        energy_current = await page.locator(
            '//*[@id="swagger-ui"]/div[4]/div[1]/div[2]/div/div/div[2]/div/div/span[1]').text_content()
        energy_current = int(energy_current.split(" ")[-1])

        await multy_tap(
            page=page,
            semaphore=5,
            taps=5,
            locator='//*[@id="swagger-ui"]/div[4]/div[1]/div[2]/div/div/div[1]/div[2]/img',
        )
        if all([energy_current < 50, turbo_count == 0]):
            time.sleep(1)
            await browser.close()


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

        await page.locator(
            '//*[@class="bubbles-group bubbles-group-last"]/div/div/div[2]/div[1]/a/div').click()

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
    hour={i for i in range(0, 25, 2)},
    minute={53},
    run_at_startup=CRON_RUN_AT_STARTUP_TAP,
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
