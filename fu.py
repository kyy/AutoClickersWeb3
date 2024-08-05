import asyncio
import logging
import os
import time

import playwright.async_api
from playwright.async_api import Playwright, async_playwright, Error
from multiprocessing import Process
from dotenv import set_key

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
from telethon.sessions import StringSession

from dotenv_config import l_dot_env

l_dot_env()

TELEGRAM_URL = "https://web.telegram.org/a/"
PHONE_NUMBER = os.getenv("PHONE")
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
            logging.warning(f"не удалось импортировать i >> {e}")
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
    with TelegramClient(
            StringSession(),
            int(os.getenv("API_ID")),
            os.getenv("API_HASH"),
    ).start(phone=os.getenv("PHONE")) as client:
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


def get_web_telegram_games_urls_names() -> list:
    """
    :return: получаем словарь с имененм игры и ссылкой web.telegram
    """
    files = os.listdir(PATH_TO_GAMES)
    fu = [i.split(".")[0] for i in files if "__" not in i]

    games = []
    for module_name in fu:
        try:
            module = __import__(name=PATH_TO_GAMES + "." + module_name, fromlist=["refresh_game_url",])
            fu_refresh = module.__dict__["refresh_game_url"]
            games.append(fu_refresh)
        except ImportError as e:
            logging.warning(f"не удалось импортировать i >> {e}")
    return games


def get_telegram_chat():
    string = os.getenv("SESSION_STRING")
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    chat_id = 777000

    with TelegramClient(StringSession(string), api_id, api_hash) as client:
        client.connect()

        # if not client.is_user_authorized():
        #     client.send_code_request(phone_number)
        #     me = client.sign_in(phone_number, input('Enter code: '))

        channel_username = '@Telegram'  # your channel
        channel_entity = client.get_entity(channel_username)
        posts = client(
            GetHistoryRequest(
                peer=channel_entity,
                limit=100,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0,
            )
        )
        print(posts)


async def refresh_all_games_urls(playwright: Playwright):
    [await fu(playwright) for fu in get_web_telegram_games_urls_names()]

if __name__ == '__main__':
    async def main():
        async with async_playwright() as playwright:
            await refresh_all_games_urls(playwright)

    asyncio.run(main())
