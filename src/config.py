import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VK_APP_URL = os.getenv("VK_APP_URL")

USEFUL_LINKS = {
    "OSINT Framework": (
        "https://osintframework.com",
        "OSINT сайты в виде графов",
    ),
    "suip": (
        "https://suip.biz/",
        "поиск информации об IP-адресах (email, домен, хостинг)",
    ),
    "OSINTRocks": (
        "https://osint.rocks/",
        "OSINT поисковик",
    ),
    "Hash Cracker": (
        "https://crackstation.net",
        "разные виды шифрования",
    ),
}