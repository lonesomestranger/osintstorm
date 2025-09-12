from typing import List, Tuple

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from src.config import USEFUL_LINKS

SEARCH_OPTIONS: List[Tuple[str, str, str]] = [
    ("📨 Telegram", "search_telegram", "telegram"),
    ("📧 Email", "search_email", "email"),
    ("📱 Телефон", "search_phone", "phone"),
    ("👤 Никнейм", "search_nickname", "nickname"),
    ("👤 ФИО", "search_full_name", "full_name"),
    ("👤 ИП", "search_entrepreneur", "entrepreneur"),
    ("🌐 VK", "search_vk", "vk"),
    ("🌐 IP", "search_ip", "ip"),
    ("🌐 Domain", "search_domain", "domain"),
    ("🪙 Криптовалюта", "search_crypto", "crypto"),
    ("🎮 Steam", "search_steam", "steam"),
]


def build_inline_search_menu(page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start_index = page * page_size
    end_index = start_index + page_size
    current_page_options = SEARCH_OPTIONS[start_index:end_index]

    for text, callback_data, _ in current_page_options:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    builder.adjust(2)

    navigation_row = []
    if page > 0:
        navigation_row.append(
            InlineKeyboardButton(text="<<<", callback_data=f"search_page:{page - 1}")
        )
    if end_index < len(SEARCH_OPTIONS):
        navigation_row.append(
            InlineKeyboardButton(text=">>>", callback_data=f"search_page:{page + 1}")
        )
    if navigation_row:
        builder.row(*navigation_row)

    return builder.as_markup()


def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text="🔎 Поиск"))
    keyboard.row(KeyboardButton(text="🔗 Полезные ссылки"))
    keyboard.row(KeyboardButton(text="ℹ️ Информация"))
    return keyboard.as_markup(resize_keyboard=True)


def get_links_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for name, (url, desc) in USEFUL_LINKS.items():
        keyboard.row(InlineKeyboardButton(text=f"{name} ({desc})", url=url))
    return keyboard.as_markup()


def get_search_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Обычный", callback_data="search_type_normal"),
        InlineKeyboardButton(text="Глубокий", callback_data="search_type_deep"),
        width=2,
    )
    return keyboard.as_markup()


def get_ip_services_keyboard(ip, latitude=None, longitude=None) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="torrent-загрузки", url=f"https://iknowwhatyoudownload.com/ru/peer/?ip={ip}"),
        InlineKeyboardButton(text="Google Maps", url=f"https://www.google.com/maps?q={latitude},{longitude}"),
    )
    return keyboard.as_markup()


def get_phone_services_keyboard(phone_number) -> InlineKeyboardMarkup:
    phone_number.replace("+", "%2B")

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="ru98", url="https://ru-98.ru/"),
        InlineKeyboardButton(
            text="mysmsbox", url=f"https://mysmsbox.ru/phone-search/{phone_number}"
        ),
        width=2,
    )
    keyboard.row(
        InlineKeyboardButton(
            text="phoneinfoga",
            url="https://phoneinfoga.net",
        ),
    )
    return keyboard.as_markup()


def get_email_services_keyboard(email_name, email_domain) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="leakpeak", url="https://leakpeek.com"),
        InlineKeyboardButton(
            text="spycloud",
            url=f"https://cye.spycloud.com/freemail?e={email_name}%40{email_domain}&et=CYE-FE%3A%20https%3A%2F%2Fspycloud.com",
        ),
        width=2,
    )
    keyboard.row(
        InlineKeyboardButton(text="haveibeenpwned", url="https://haveibeenpwned.com/"),
    )
    return keyboard.as_markup()


def get_telegram_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="where_a_person_wrote", url="https://t.me/where_a_person_wrote_bot"
        ),
        InlineKeyboardButton(text="Insight", url="https://t.me/socprofile_bot"),
        width=2,
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Lyzem (поисковик Telegram)", url="https://lyzem.com/"
        ),
    )
    return keyboard.as_markup()


def get_entrepreneur_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="checko.ru", url="https://checko.ru/"),
        InlineKeyboardButton(text="rusprofile", url="https://rusprofile.ru/"),
        width=2,
    )
    return keyboard.as_markup()


def get_full_name_services_keyboard(name, surname, full_name) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="freepeoplesearch",
            url=f"https://freepeoplesearchtool.com/#gsc.tab=0&gsc.q={name}%20{surname}%20{full_name}&gsc.sort=",
        )
    )
    return keyboard.as_markup()


def get_steam_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="SteamID",
            url="https://steamid.xyz",
        ),
        InlineKeyboardButton(
            text="SteamDB",
            url="https://steamdb.info/calculator/",
        ),
    )
    return keyboard.as_markup()


def get_domain_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Domain Investigator",
            url="https://cipher387.github.io/domain_investigation_toolbox/",
        ),
        InlineKeyboardButton(
            text="Investigator",
            url="https://abhijithb200.github.io/investigator/",
        ),
        width=2,
    )
    keyboard.row(
        InlineKeyboardButton(
            text="bbot (github)",
            url="https://github.com/blacklanternsecurity/bbot",
        ),
    )
    return keyboard.as_markup()
