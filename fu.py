import asyncio
import logging
import os
import time

from playwright.async_api import Playwright, async_playwright
from multiprocessing import Process
from dotenv import set_key

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from dotenv_config import l_dot_env

l_dot_env()

TELEGRAM_URL = "https://web.telegram.org/a/"
PHONE_NUMBER = os.getenv("PHONE")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STORAGE_STATE_NAME = "web_telegram.json"
PATH_TO_GAMES = "games"


def games_fu():
    """
    :return: импортируем функции
    """
    files = os.listdir(PATH_TO_GAMES)
    fu = [i.split(".")[0] for i in files if "__" not in i]

    games = {}
    for module_name in fu:
        try:
            module = __import__(PATH_TO_GAMES + "." + module_name)
            func = getattr(module, module_name)
            games[module_name] = func
        except Exception as e:
            logging.warning(f"<games_fu> не удалось импортировать {module_name=} [{e}]")
    return games


async def start_page_at_phone(playwright: Playwright, url: str, browser_context: dict = None, mobile=True):
    context = {}
    if mobile:
        context = playwright.devices['Pixel 7']
    if browser_context:
        context.update(**browser_context)
    browser = await playwright.chromium.launch(headless=False)
    browser_mobile = await browser.new_context(**context)
    page = await browser_mobile.new_page()
    await page.goto(url)
    await asyncio.sleep(5)
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
    for module_name in funcs:
        if module_name != "":
            try:
                module = __import__(name=PATH_TO_GAMES + "." + module_name, fromlist=["refresh_game_url", ])
                fu = module.__dict__.get("refresh_game_url")
                if fu is not None:
                    games.append((fu, module_name))
                elif fu is None:
                    logging.warning(f"<get_fu_refresh_game_urls_name> не удалось импортировать {module_name=} [{fu}]")
            except ImportError as e:
                logging.warning(f"<get_fu_refresh_game_urls_name> не удалось импортировать {module_name=} [{e}]")
    return games


async def refresh_all_games_urls(ctx=None):
    async with async_playwright() as playwright:

        for fu_name in get_fu_refresh_game_urls_name():
            fu, name = fu_name
            try:
                src: str = await fu(playwright)

                if src != "":
                    set_key(dotenv_path=".env", key_to_set=name.upper() + "_URL",
                            value_to_set=src.replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios"))
                elif src == "":
                    logging.warning(f"<refresh_all_games_urls> Не удалось получить ссылку! {name=}")
                logging.info(f"Ссылка обновлена {name=}")

            except Exception as e:
                logging.error(f"Ошибка при обновлении ссылки {name=} [{e}]")


def get_fu_process() -> list:
    """
    :return: автоимпорт функции процессов и имен игр
    """
    files = os.listdir(PATH_TO_GAMES)
    funcs = [i.split(".")[0] for i in files if "__" not in i]
    games = []
    for module_name in funcs:
        if module_name != "":
            try:
                module = __import__(name=PATH_TO_GAMES + "." + module_name, fromlist=["cron_config", ])
                fu = module.__dict__.get("cron_config")
                if fu is not None:
                    games.append(fu)
                logging.info(f"{module_name=} импортирован [{fu}]")
            except ImportError as e:
                logging.error(f"<get_fu_process()> не удалось импортировать {module_name=} [{e}]")
                continue
    return games


if __name__ == '__main__':
    pass
