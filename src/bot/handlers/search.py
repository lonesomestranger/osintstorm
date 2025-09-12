import asyncio
import logging
import os
import re
import textwrap
from urllib.parse import urlparse

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from src.bot.keyboards import (
    build_inline_search_menu,
    get_domain_services_keyboard,
    get_email_services_keyboard,
    get_entrepreneur_services_keyboard,
    get_full_name_services_keyboard,
    get_ip_services_keyboard,
    get_main_menu,
    get_search_type_keyboard,
    get_steam_services_keyboard,
    get_telegram_services_keyboard,
)
from src.services.dorks.namint_module import Namint
from src.services.emails.holehe_module import Holehe
from src.services.ip.ip_parser import IPParser
from src.services.usernames.gosearch_service import gosearch_module
from src.services.usernames.maigret_service.maigret_module import Maigret
from src.services.vk.infoapp.infoapp_module import VkParser
from src.utils.parsing import (
    extract_email,
    extract_phone_number,
    extract_vk_link,
    is_valid_ip,
)

router = Router()


class SearchStates(StatesGroup):
    waiting_for_full_name_input = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_nickname = State()
    choosing_nickname_search_type = State()
    waiting_for_vk = State()
    waiting_for_ip = State()


@router.message(F.text.lower() == "поиск")
@router.message(F.text.lower() == "🔎 поиск")
async def show_search_menu(message: Message, state: FSMContext):
    await state.clear()
    keyboard = build_inline_search_menu()
    await message.answer("Выберите тип поиска:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("search_page:"))
async def navigate_search_pages(query: CallbackQuery, state: FSMContext):
    await state.clear()
    page = int(query.data.split(":")[1])
    keyboard = build_inline_search_menu(page=page)
    await query.message.edit_reply_markup(reply_markup=keyboard)
    await query.answer()


# domain search
@router.message(F.data == "search_domain")
async def request_domain(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о домене и его уязвимостях.",
        reply_markup=get_domain_services_keyboard(),
    )


# crypto search
@router.callback_query(F.data == "search_crypto")
async def request_crypto(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        """
    <b>Список сервисов для проверки кошелька:</b>

<b>BTC:</b>
    - Wallet Explorer: https://www.walletexplorer.com
    - Blockpath: https://blockpath.com
    - Bitcoin Paths: https://bitcoinpaths.com
<b>ETH:</b>
    - Breadcrumbs: https://www.breadcrumbs.app/new
    - Etherscan: https://etherscan.io
    - Ethplorer: https://ethplorer.io
<b>BTC, ETH, SOLANA:</b>
    - Wallet Labels: https://www.walletlabels.xyz
    - Blockchain Explorer: https://www.blockchain.com/explorer
<b>USDT</b>:
    - Blockchair: https://blockchair.com/tether
    - TetherScan: https://tetherscan.org/?attempt=1
<b>TRON</b>:
    - TronScan: https://tronscan.io/#/tokens/list
<b>Wallet Balance:</b>
    - CoinLedger: https://coinledger.io/wallet-balance-check
    	""",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await state.clear()


# ip search
@router.callback_query(F.data == "search_ip")
async def request_ip(query: CallbackQuery, state: FSMContext):
    message = await query.message.answer(
        "Введите IP-адрес в формате xxx.xxx.xxx.xxx для поиска информации об IP."
    )
    await state.update_data(request_message_id=message.message_id)
    await state.set_state(SearchStates.waiting_for_ip)


@router.message(SearchStates.waiting_for_ip)
async def search_ip(message: Message, state: FSMContext):
    ip_addr = message.text
    data = await state.get_data()
    request_message_id = data.get("request_message_id")

    if request_message_id:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=request_message_id
        )
    await message.delete()

    if not is_valid_ip(ip_addr):
        error_message = await message.answer(
            "Неверный формат IP-адреса. Пожалуйста, введите IP в формате xxx.xxx.xxx.xxx."
        )
        await state.update_data(request_message_id=error_message.message_id)
        return

    ip_data = IPParser(str(ip_addr)).parse_info()

    if not ip_data or not ip_data["success"]:
        error_message = await message.answer(
            "Не удалось получить информацию об IP-адресе."
        )
        await state.update_data(request_message_id=error_message.message_id)
        await state.clear()
        return

    ip_addr = ip_data["ip"]
    ip_latitude = ip_data["latitude"]
    ip_longitude = ip_data["longitude"]

    ip_info = textwrap.dedent(f"""
                <b>IP:</b> {ip_addr}
                <b>Страна:</b> {ip_data["country"]}
                <b>Город:</b> {ip_data["city"]}
                <b>Широта:</b> {ip_latitude}
                <b>Долгота:</b> {ip_longitude}
                """)

    await message.answer(
        f"{ip_info}\nВы можете воспользоваться ссылками ниже для получения дополнительной информации об IP.",
        reply_markup=get_ip_services_keyboard(ip_addr, ip_latitude, ip_longitude),
        parse_mode=ParseMode.HTML,
    )
    await state.clear()


# steam search
@router.callback_query(F.data == "search_steam")
async def request_steam(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о пользователе Steam.",
        reply_markup=get_steam_services_keyboard(),
    )
    await state.clear()


# entrepreneur search
@router.callback_query(F.data == "search_entrepreneur")
async def request_entrepreneur(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о предпринимателе (ИП).",
        reply_markup=get_entrepreneur_services_keyboard(),
    )
    await state.clear()


# telegram search
@router.callback_query(F.data == "search_telegram")
async def request_telegram(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Все сервисы по Telegram на данный момент неактуальны. Вы можете воспользоваться ссылками ниже для получения информации о пользователе.",
        reply_markup=get_telegram_services_keyboard(),
    )
    await state.clear()


# full name search
@router.callback_query(F.data == "search_full_name")
async def request_full_name_combined(query: CallbackQuery, state: FSMContext):
    message = await query.message.answer(
        "Введите ФИО и дату рождения (опционально) через пробел.  Пример: `Иван Иванович Иванов 2004`\n\nЕсли отчество или дата рождения неизвестны, пропустите их.",
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.update_data(request_full_name_message_id=message.message_id)
    await state.set_state(SearchStates.waiting_for_full_name_input)
    await query.answer()


@router.message(SearchStates.waiting_for_full_name_input)
async def process_full_name_combined(message: Message, state: FSMContext):
    data = await state.get_data()
    request_full_name_message_id = data.get("request_full_name_message_id")

    if request_full_name_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=request_full_name_message_id
            )
        except TelegramBadRequest:
            pass

    try:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
    except TelegramBadRequest:
        pass

    args = message.text.strip().split()
    num_args = len(args)

    if num_args < 2:
        error_message = await message.answer(
            "Пожалуйста, укажите хотя бы имя и фамилию. Пример: `Иван Иванов`",
            parse_mode=ParseMode.MARKDOWN,
        )
        await state.update_data(request_full_name_message_id=error_message.message_id)
        return

    first_name = args[0]
    last_name = args[-1]
    middle_name = ""
    date_of_birth = ""

    if num_args == 2:
        last_name = args[1]

    elif num_args == 3:
        try:
            int(args[2])
            date_of_birth = args[2]
            last_name = args[1]
        except ValueError:
            middle_name = args[1]
            last_name = args[2]

    elif num_args > 3:
        middle_name = args[1]
        try:
            int(args[-1])
            date_of_birth = args[-1]
            last_name = args[-2]
        except ValueError:
            middle_name = " ".join(args[1:-1])
            last_name = args[-1]

    await message.answer(
        "Вы также можете воспользоваться готовыми дорками для поиска по ФИО, представленными в .txt файле ниже."
    )

    processing_message = await message.answer("Обрабатываю ФИО в базах...")

    namint = Namint(
        name=first_name,
        middle=middle_name,
        surname=last_name,
        date_of_birth=date_of_birth,
        dom1="gmail.com",
    )
    links = namint.generate_links()

    namint_result = f"dorks_{first_name}_{last_name}.txt"

    with open(namint_result, "w", encoding="utf-8") as f:
        f.write(
            "Категории: name_patterns, name_patterns_with_middle, combined_name_search\n"
        )
        f.write("           login_patterns, login_patterns_with_middle, email_search")
        for category, link_list in links.items():
            f.write(f"\n\n--- {category} ---\n\n")
            for link in link_list:
                f.write(f"{link}\n")

    dorks_file = FSInputFile(namint_result)

    try:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=processing_message.message_id
        )
    except TelegramBadRequest:
        pass

    await message.answer(
        "Все сервисы поиска по ФИО на данный момент неактуальны. Вы можете воспользоваться ссылкой ниже для получения информации о пользователе.",
        reply_markup=get_full_name_services_keyboard(
            first_name, last_name, middle_name
        ),
    )
    await message.answer_document(dorks_file)

    try:
        os.remove(namint_result)
    except FileNotFoundError:
        pass

    await state.clear()


# email search
@router.callback_query(F.data == "search_email")
async def request_email(query: CallbackQuery, state: FSMContext):
    message = await query.message.answer("Отправьте мне email для поиска.")
    await state.update_data(request_email_message_id=message.message_id)
    await state.set_state(SearchStates.waiting_for_email)
    await query.answer()


@router.message(SearchStates.waiting_for_email)
async def process_email_search(message: Message, state: FSMContext):
    email = extract_email(message.text)
    email_name, email_domain = email.split("@")
    data = await state.get_data()
    request_email_message_id = data.get("request_email_message_id")

    if request_email_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=request_email_message_id
            )
        except TelegramBadRequest:
            pass

    try:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
    except TelegramBadRequest:
        pass

    if email:
        searching_message = await message.answer(f"Ищу информацию по email: {email}...")
        holehe = Holehe(email=email, only_used=True)
        used_services = await holehe.run_holehe()

        if used_services:
            formatted_services = "\n".join(
                [f"- {service.capitalize()}" for service in used_services]
            )
            result_message = (
                f"Использованные сервисы <b>{email}</b>:\n{formatted_services}"
            ).replace("- Email", "")
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=searching_message.message_id
                )
            except TelegramBadRequest:
                pass
            await message.answer(
                result_message,
                parse_mode=ParseMode.HTML,
                reply_markup=get_email_services_keyboard(email_name, email_domain),
            )
        else:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=searching_message.message_id
                )
            except TelegramBadRequest:
                pass
            await message.answer(
                f"Сервисы, использующие email <b>{email}</b>, не найдены.",
                parse_mode=ParseMode.HTML,
                reply_markup=get_email_services_keyboard(email_name, email_domain),
            )

    else:
        await message.answer("Некорректный формат email. Попробуйте еще раз.")
        return

    await state.clear()


# phone search
@router.callback_query(F.data == "search_phone")
async def request_phone(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Отправьте мне номер телефона для поиска.")
    await state.set_state(SearchStates.waiting_for_phone)
    await query.answer()


@router.message(SearchStates.waiting_for_phone)
async def process_phone_search(message: Message, state: FSMContext):
    phone = extract_phone_number(message.text)
    if phone:
        await message.answer(f"Ищу информацию по номеру телефона: {phone}...")
        await message.answer(
            f"Выполняется поиск по {phone}, реализация еще не добавлена"
        )
    else:
        await message.answer("Некорректный номер телефона. Попробуйте еще раз.")
        return

    await state.clear()


# nickname search
@router.callback_query(F.data == "search_nickname")
async def request_nickname(query: CallbackQuery, state: FSMContext):
    message = await query.message.answer("Отправьте мне никнейм для поиска.")
    await state.update_data(request_nickname_message_id=message.message_id)
    await state.set_state(SearchStates.waiting_for_nickname)
    await query.answer()


@router.message(SearchStates.waiting_for_nickname)
async def process_nickname_entry(message: Message, state: FSMContext):
    data = await state.get_data()
    request_nickname_message_id = data.get("request_nickname_message_id")

    if request_nickname_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=request_nickname_message_id
            )
        except TelegramBadRequest:
            pass

    try:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
    except TelegramBadRequest:
        pass

    choose_type_message = await message.answer(
        "Выберите тип поиска:", reply_markup=get_search_type_keyboard()
    )
    await state.update_data(choose_type_message_id=choose_type_message.message_id)

    await state.update_data(nickname=message.text)
    await state.set_state(SearchStates.choosing_nickname_search_type)


@router.callback_query(SearchStates.choosing_nickname_search_type)
async def process_search_type_selection(query: CallbackQuery, state: FSMContext):
    await query.answer()
    data = await state.get_data()
    nickname = data.get("nickname")
    choose_type_message_id = data.get("choose_type_message_id")

    if choose_type_message_id:
        try:
            await query.message.bot.delete_message(
                chat_id=query.message.chat.id, message_id=choose_type_message_id
            )
        except TelegramBadRequest:
            pass

    if not nickname:
        await query.message.answer("Что-то пошло не так. Начните поиск заново.")
        await state.clear()
        return

    await query.message.answer(f"Идет поиск по никнейму {nickname}...")

    try:
        maigret = Maigret()
        maigret.download_files()
    except Exception as e:
        logging.error(f"Maigret download failed: {e}")

    maigret_logger = logging.getLogger("maigret")
    maigret_logger.setLevel(logging.CRITICAL + 1)
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.CRITICAL + 1)

    if query.data == "search_type_normal":
        top_sites_count = 350
        maigret = Maigret(top_sites_count=top_sites_count)
        maigret_task = asyncio.create_task(maigret.search(nickname))
        maigret_result = await maigret_task
        gosearch_result = None

    elif query.data == "search_type_deep":
        top_sites_count = 2800
        maigret = Maigret(top_sites_count=top_sites_count)
        maigret_task = asyncio.create_task(maigret.search(nickname))
        gosearch_task = asyncio.create_task(gosearch_module.search(nickname))
        maigret_result, gosearch_result = await asyncio.gather(
            maigret_task, gosearch_task
        )

    else:
        await query.message.answer("Неизвестный тип поиска.")
        await state.clear()
        return

    await send_combined_results(
        query.message, maigret_result, gosearch_result, nickname
    )
    await state.clear()


def extract_maigret_data(maigret_result: dict) -> list:
    extracted_data = []

    if maigret_result and maigret_result["status"] not in ("error", "no_results"):
        if maigret_result["found_sites"]:
            for site_data in maigret_result["found_sites"]:
                site_name = (
                    site_data.get("site")
                    or site_data.get("tag")
                    or (
                        urlparse(site_data["url_user"]).netloc
                        if "url_user" in site_data
                        else None
                    )
                )

                if "url_user" in site_data and isinstance(site_name, str):
                    try:
                        cleaned_site_name = re.sub(
                            r"\s*\([^)]*\)", "", site_name
                        ).strip()

                        if cleaned_site_name:
                            extracted_data.append(
                                {
                                    "site_name": cleaned_site_name,
                                    "url": site_data["url_user"],
                                }
                            )
                    except Exception as e:
                        logging.error(
                            f"Error processing site_name '{site_name}' with regex: {e}"
                        )
                        extracted_data.append(
                            {"site_name": site_name, "url": site_data["url_user"]}
                        )

                elif "url_user" in site_data and site_name is not None:
                    logging.warning(
                        f"Maigret site_name was not a string ({type(site_name)}): {repr(site_name)} for url {site_data['url_user']}. Using domain as fallback."
                    )

                    domain_fallback = urlparse(site_data["url_user"]).netloc
                    if domain_fallback:
                        extracted_data.append(
                            {"site_name": domain_fallback, "url": site_data["url_user"]}
                        )

    return extracted_data


def extract_gosearch_data(gosearch_result: dict) -> list:
    extracted_data = []
    if gosearch_result and gosearch_result["status"] not in ("error", "no_results"):
        if "raw_output" in gosearch_result:
            matches = re.findall(
                r"\[\+\]\s(.*?):\s(https?://[^\s^\[^\x1b]+)",
                gosearch_result["raw_output"],
            )
            for site_name, url in matches:
                extracted_data.append(
                    {"site_name": site_name.strip(), "url": url.strip()}
                )

        if "compromised_passwords" in gosearch_result:
            for item in gosearch_result["compromised_passwords"]:
                extracted_data.append(
                    {
                        "type": "compromised_password",
                        "email": item["email"],
                        "password": item["password"],
                    }
                )
        if (
            "hudsonrock_status" in gosearch_result
            and gosearch_result["hudsonrock_status"] == "Found in HudsonRock database"
        ):
            hudson_rock_section = re.search(
                r"Searching HudsonRock.+?\n((?:.|\n)+?)(?:⎯⎯⎯|\Z)",
                gosearch_result["raw_output"],
                re.MULTILINE,
            )
            if hudson_rock_section:
                extracted_data.append(
                    {"type": "hudsonrock", "data": hudson_rock_section.group(1)}
                )
    return extracted_data


def combine_and_deduplicate(maigret_data: list, gosearch_data: list) -> list:
    combined_data = []
    seen_domains = set()
    seen_emails = set()

    for item in maigret_data:
        if item.get("site_name") is None:
            continue
        cleaned_site_name = re.sub(r"\s*\([^)]*\)", "", item["site_name"]).strip()
        domain = urlparse(item["url"]).netloc
        if domain not in seen_domains:
            combined_data.append(
                {
                    "site_name": cleaned_site_name,
                    "url": item["url"],
                    "source": "maigret",
                }
            )
            seen_domains.add(domain)

    for item in gosearch_data:
        if item.get("type") == "compromised_password":
            if item["email"] not in seen_emails:
                combined_data.append(item)
                seen_emails.add(item["email"])
            continue

        if item.get("type") == "hudsonrock":
            combined_data.append(item)
            continue

        if item.get("site_name") is None:
            continue

        domain = urlparse(item["url"]).netloc
        if domain not in seen_domains:
            combined_data.append(
                {
                    "site_name": item["site_name"],
                    "url": item["url"],
                    "source": "gosearch",
                }
            )
            seen_domains.add(domain)

    return combined_data


async def send_combined_results(message, maigret_result, gosearch_result, nickname):
    maigret_data = extract_maigret_data(maigret_result)
    gosearch_data = extract_gosearch_data(gosearch_result)

    combined_data = combine_and_deduplicate(maigret_data, gosearch_data)

    if not combined_data:
        await message.answer("Аккаунтов с данным ником не найдено.")
        return

    combined_message = "<b>Результаты поиска:</b>\n"

    for item in combined_data:
        if item.get("type") == "compromised_password":
            combined_message += (
                f"\n\U0001f512 <b>Слитые пароли:</b>\n"
                f"   Email: <b>{item['email']}</b>\n"
                f"   Password: <b>{item['password']}</b>\n"
            )
        elif item.get("type") == "hudsonrock":
            combined_message += (
                f"\n\U0001f480 <b>HudsonRock информация:</b>\n {item['data']}"
            )
        else:
            combined_message += f"• <b>{item['site_name']}</b>: {item['url']}\n"

    try:
        if len(combined_message) > 4096:
            for i in range(0, len(combined_message), 4096):
                await message.answer(
                    combined_message[i : i + 4096],
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML,
                )
        else:
            await message.answer(
                combined_message,
                disable_web_page_preview=True,
                parse_mode=ParseMode.HTML,
            )
    except Exception as e:
        print(f"Error sending results: {e}")
        return

    if (
        maigret_result
        and maigret_result["report_filename"]
        and os.path.exists(maigret_result["report_filename"])
    ):
        report_file = FSInputFile(maigret_result["report_filename"])
        await message.answer_document(report_file)
        try:
            os.remove(maigret_result["report_filename"])
        except Exception as e:
            print(f"Error deleting report file: {e}")


# VK search
@router.callback_query(F.data == "search_vk")
async def request_vk(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Отправьте мне ссылку на профиль VK или ID пользователя."
    )
    await state.set_state(SearchStates.waiting_for_vk)
    await query.answer()


@router.message(SearchStates.waiting_for_vk)
async def process_vk_search(message: Message, state: FSMContext):
    vk_id = extract_vk_link(message.text)
    if not vk_id:
        await message.answer("Некорректная ссылка на VK. Попробуйте еще раз.")
        return

    wait_message = await message.answer(f"Ищу информацию по VK ID/ссылке: {vk_id}...")
    await state.update_data(wait_message_id=wait_message.message_id)

    try:
        parser = VkParser()
        user_data = parser.parse_user_data(vk_id)

        if user_data:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=(await state.get_data())["wait_message_id"],
            )

            response_text = (
                f"<b>Регистрация:</b> {user_data['registration_date']}\n"
                f"<b>VK ID:</b> {user_data['vk_id']}\n"
                f"<b>Последний визит:</b> {user_data['last_visit']}\n\n"
            )

            if user_data["communities"]:
                response_text += "<b>Сообщества:</b>\n"
                for community in user_data["communities"]:
                    response_text += (
                        f"- [{community['name']}]({community['link']}) "
                        f"({community['participants']})\n"
                    )
            else:
                response_text += "<b>Сообщества:</b> Не найдены\n"

            if user_data["apps"]:
                response_text += "\n<b>Приложения:</b>\n"
                for app in user_data["apps"]:
                    response_text += (
                        f"- [{app['name']}]({app['link']}) ({app['participants']})\n"
                    )
            else:
                response_text += "\n<b>Приложения:</b> Не найдены\n"

            await message.answer(response_text, parse_mode="HTML")
        else:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=(await state.get_data())["wait_message_id"],
            )
            await message.answer("Не удалось получить информацию о пользователе.")
    except Exception as e:
        if "wait_message_id" in await state.get_data():
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=(await state.get_data())["wait_message_id"],
            )

        print(f"Произошла ошибка при поиске: {e}")
        await message.answer("Не удалось получить информацию о пользователе.")
    finally:
        if "wait_message_id" in await state.get_data():
            await state.clear()


@router.message(F.text == "назад")
@router.message(F.text == "⬅️ Назад")
async def go_back(message: Message, state: FSMContext):
    await message.answer("Возвращаюсь в главное меню.", reply_markup=get_main_menu())
    await state.clear()
