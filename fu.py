import asyncio
import os
import time

from playwright.async_api import Playwright, async_playwright
from multiprocessing import Process
from dotenv import set_key

from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from tqdm import tqdm

from dotenv_config import l_dot_env

l_dot_env()

TELEGRAM_URL = "https://web.telegram.org/a/"
PHONE_NUMBER = os.getenv("PHONE")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STORAGE_STATE_NAME = "web_telegram.json"
PATH_TO_GAMES = "games"


async def start_page_at_phone(playwright: Playwright, url: str, browser_context: dict = None, mobile=True, timeout=5):
    context = {}
    if mobile:
        context = playwright.devices['Pixel 7']
    if browser_context:
        context.update(**browser_context)
    browser = await playwright.chromium.launch(headless=True)
    browser_mobile = await browser.new_context(**context)
    page = await browser_mobile.new_page()
    await page.goto(url)
    time.sleep(timeout)
    return browser, page


def create_proccess(target=None, ctx=None):
    proc = Process(target=target)
    proc.daemon = True
    proc.start()
    return proc


def get_telegram_session():
    with TelegramClient(StringSession(), API_ID, API_HASH).start(phone=PHONE_NUMBER) as client:
        string = client.session.save()
        print(f"{string=}")
        set_key(dotenv_path=".env", key_to_set="SESSION_STRING", value_to_set=string)


async def get_telegram_storage_state(playwright: Playwright) -> None:
    """
    :param playwright:
    :return: сохраняем сессию браузера: "web.telegram" в формате .json
    """
    if not os.path.exists(STORAGE_STATE_NAME):
        browser, page = await start_page_at_phone(playwright=playwright, url=TELEGRAM_URL, mobile=False)
        time.sleep(2)
        await page.locator('xpath=//*[@id="auth-qr-form"]/div/button[1]').click()  # next
        time.sleep(1)
        number = page.locator('xpath=//*[@id="sign-in-phone-number"]')  # phone number
        await number.clear()
        await number.press_sequentially(PHONE_NUMBER)
        await page.locator('xpath=//*[@id="auth-phone-number-form"]/div/form/button[1]/div').click()  # next
        # await page.locator('xpath=//*[@id="sign-in-code"]').press_sequentially(input("sms code:"))
        await asyncio.sleep(30)
        await page.context.storage_state(path=STORAGE_STATE_NAME)
        await browser.close()


def get_fu_refresh_game_urls_name() -> list:
    """
    :return: автоимпорт функции и имен игр
    """
    files = os.listdir(PATH_TO_GAMES)
    funcs = [i.split(".")[0] for i in files if "__" not in i]

    games = []
    for module_name in tqdm(funcs, desc='get_fu_refresh_game_urls_name'):
        if module_name != "":
            try:
                module = __import__(name=PATH_TO_GAMES + "." + module_name, fromlist=["refresh_game_url", ])
                fu = module.__dict__.get("refresh_game_url")
                if fu is not None and fu is not False:
                    games.append((fu, module_name))
                    print(f" импортирован <refresh_game_url> {module_name=}")
                elif fu is None:
                    print(f"<get_fu_refresh_game_urls_name> не удалось импортировать {module_name=} [{fu}]")
            except ImportError as e:
                print(f"<get_fu_refresh_game_urls_name> не удалось импортировать {module_name=} [{e}]")
    return games


def get_fu_process() -> list:
    """
    :return: автоимпорт функции процессов и имен игр
    """
    files = os.listdir(PATH_TO_GAMES)
    funcs = [i.split(".")[0] for i in files if "__" not in i]
    games = []
    for module_name in tqdm(funcs, desc='get_fu_process'):
        if module_name != "":
            try:
                module = __import__(name=PATH_TO_GAMES + "." + module_name, fromlist=["cron_config", ])
                fu = module.__dict__.get("cron_config")
                if fu is not None:
                    games.append(fu)
            except ImportError as e:
                print(f"<get_fu_process()> не удалось импортировать {module_name=} [{e}]")
                continue
    return games


async def multy_tap(page: async_playwright, taps: int, locator: str, semaphore: int = 20):
    semaphore = asyncio.Semaphore(semaphore)

    async def one_tap():
        async with semaphore:
            await page.locator(locator).tap(force=True)

    task_tap = [asyncio.ensure_future(one_tap()) for tap in range(taps)]
    await asyncio.gather(*task_tap)


async def get_canonic_full_game_url(page, browser):
    """
    :param playwright:
    :return: обновляем ссылки игр содержащих временный токен
    """

    await page.wait_for_selector('xpath=//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]')
    await page.locator('//*[@id="column-center"]/div/div/div[4]/div/div[1]/div/div[8]/div[1]').click()  # burger
    await page.locator('xpath=/html/body/div[7]/div/div[2]/button[1]/div').click()  # launch
    iframe = await page.wait_for_selector('iframe')
    src = await iframe.get_attribute('src')
    await browser.close()
    return src


if __name__ == '__main__':
    pass
