import asyncio
import os
from playwright.async_api import Playwright
from multiprocessing import Process
from dotenv import set_key

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
from telethon.sessions import StringSession

from dotenv_config import l_dot_env

l_dot_env()


async def start_page_at_phone(playwright: Playwright, url: str):
    phone = playwright.devices['Pixel 7']
    browser = await playwright.chromium.launch(headless=False)
    browser_mobile = await browser.new_context(**phone)
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


def get_telegram_chat():
    string = os.getenv("SESSION_STRING")
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")

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


if __name__ == '__main__':
    get_telegram_chat()