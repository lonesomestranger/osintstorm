import asyncio
import logging
import os
import textwrap

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from src.bot.handlers.search import send_combined_results
from src.bot.keyboards import (
    get_domain_services_keyboard,
    get_email_services_keyboard,
    get_entrepreneur_services_keyboard,
    get_full_name_services_keyboard,
    get_ip_services_keyboard,
    get_phone_services_keyboard,
    get_steam_services_keyboard,
    get_telegram_services_keyboard,
)
from src.config import VK_APP_URL
from src.services.dorks.namint_module import Namint
from src.services.emails.holehe_module import Holehe
from src.services.ip.ip_parser import IPParser
from src.services.usernames.gosearch_service import gosearch_module
from src.services.usernames.maigret_service.maigret_module import Maigret
from src.services.vk.infoapp.infoapp_module import VkParser
from src.utils.parsing import is_valid_ip

router = Router()


@router.message(Command("username"))
async def search_username_command(
        message: Message, command: CommandObject, state: FSMContext
):
    if command.args is None:
        await message.answer(
            "Пожалуйста, укажите никнейм. Пример: /username nickname или /username deep nickname"
        )
        return

    args = command.args.split()
    search_type = "normal"

    if len(args) == 1:
        nickname = args[0]
    elif len(args) == 2 and args[0].lower() == "deep":
        search_type = "deep"
        nickname = args[1]
    else:
        await message.answer(
            "Неверный формат команды. Используйте: /username nickname или /username deep nickname"
        )
        return
    await message.answer(f"Выполняется поиск по никнейму {nickname}...")

    try:
        maigret = Maigret()
        maigret.download_files()
    except Exception as e:
        print(f"Exception while downloading files for maigret: {e}")

    maigret_logger = logging.getLogger("maigret")
    maigret_logger.setLevel(logging.CRITICAL + 1)
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.CRITICAL + 1)

    if search_type == "normal":
        top_sites_count = 350
        maigret = Maigret(top_sites_count=top_sites_count)
        maigret_task = asyncio.create_task(maigret.search(nickname))
        maigret_result = await maigret_task
        gosearch_result = None
    else:
        top_sites_count = 2800
        maigret = Maigret(top_sites_count=top_sites_count)
        maigret_task = asyncio.create_task(maigret.search(nickname))
        gosearch_task = asyncio.create_task(gosearch_module.search(nickname))
        maigret_result, gosearch_result = await asyncio.gather(
            maigret_task, gosearch_task
        )
    await send_combined_results(message, maigret_result, gosearch_result, nickname)


@router.message(Command("email"))
async def search_email_command(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Пожалуйста, укажите email. Пример: /email example@mail.com"
        )
        return

    email = command.args.strip()
    email_name, email_domain = email.split("@")
    searching_message = await message.answer(f"Ищу информацию по email: {email}...")

    holehe = Holehe(email=email, only_used=True)
    used_services = await holehe.run_holehe()

    if used_services:
        formatted_services = "\n".join(
            [f"- {service.capitalize()}" for service in used_services]
        )
        result_message = (
            f"Использованные сервисы <b>{email}</b>:\n{formatted_services}".replace(
                "- Email", ""
            )
        )

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


@router.message(Command("telegram"))
async def search_telegram_command(message: Message, command: CommandObject):
    await message.answer(
        "Все сервисы по Telegram на данный момент неактуальны. Вы можете воспользоваться ссылками ниже для получения информации о пользователе Telegram.",
        reply_markup=get_telegram_services_keyboard(),
    )


@router.message(Command("steam"))
async def search_steam_command(message: Message, command: CommandObject):
    await message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о пользователе Steam.",
        reply_markup=get_steam_services_keyboard(),
    )


@router.message(Command("vk"))
async def search_vk_command(message: Message, command: CommandObject):
    if not VK_APP_URL:
        await message.answer(
            "Функция поиска по VK не настроена администратором бота. "
            "Необходимо указать `VK_APP_URL` в файле .env."
        )
        return

    if command.args is None:
        await message.answer(
            "Пожалуйста, укажите ID пользователя VK.\nПример: /vk 123456789, /vk durov, /vk https://vk.com/id123456789",
            disable_web_page_preview=True,
        )
        return

    command_args = command.args.strip().split(" ")
    vk_id = command_args[0]

    searching_message = await message.answer(
        f"Выполняю поиск информации о пользователе VK {vk_id}...",
        disable_web_page_preview=True,
    )

    try:
        parser = VkParser()
        user_data = parser.parse_user_data(vk_id)

        if user_data == "user_not_found":
            await message.answer(f"Пользователь VK {vk_id} не найден.")
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=searching_message.message_id
            )
            return

        if user_data:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=searching_message.message_id
                )
            except TelegramBadRequest as e:
                print(f"Error deleting message: {e}")

            if user_data["last_visit"]:
                response_text = (
                    f"<b>{user_data['name']}</b>\n"
                    f"<b>Регистрация:</b> {user_data['registration_date']}\n"
                    f"<b>VK ID:</b> {user_data['vk_id']}\n"
                    f"<b>Последний визит:</b> {user_data['last_visit']}\n\n"
                )
            else:
                response_text = (
                    f"<b>{user_data['name']}</b>\n"
                    f"<b>Регистрация:</b> {user_data['registration_date']}\n"
                    f"<b>VK ID:</b> {user_data['vk_id']}\n"
                )

            if user_data["communities"]:
                response_text += "<b>Сообщества:</b>\n"
                for community in user_data["communities"]:
                    response_text += f"- <b>{community['name']}</b>: {community['link']} ({community['participants']})\n"
            else:
                response_text += "<b>Сообщества:</b> Не найдены\n"

            if user_data["apps"]:
                response_text += "\n<b>Приложения:</b>\n"
                for app in user_data["apps"]:
                    response_text += f"- <b>{app['name']}</b>: {app['link']} ({app['participants']})\n"
            else:
                response_text += "<b>Приложения:</b> Не найдены\n"

            try:
                await message.answer(
                    response_text,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except TelegramBadRequest as e:
                print(f"Error sending message: {e}")

        else:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=searching_message.message_id,
                )
            except TelegramBadRequest as e:
                print(f"Error deleting message: {e}")

            await message.answer(
                f"Не удалось получить информацию о пользователе {vk_id}."
            )
    except Exception as e:
        print(f"Произошла ошибка при поиске: {e}")

        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=searching_message.message_id,
            )
        except TelegramBadRequest as e:
            print(f"Error deleting message: {e}")

        await message.answer(f"Не удалось получить информацию о пользователе {vk_id}.")


@router.message(Command("ip"))
async def search_ip_command(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer("Пожалуйста, укажите IP-адрес. Пример: /ip 44.44.44.44")
        return

    ip_addr_list = command.args.strip().split(" ")
    ip_addr = ip_addr_list[0]

    if not is_valid_ip(ip_addr):
        await message.answer(
            "Неверный формат IP-адреса. Пожалуйста, введите IP в формате xxx.xxx.xxx.xxx."
        )
        return

    ip_data = IPParser(str(ip_addr)).parse_info()
    if not ip_data or not ip_data["success"]:
        await message.answer("Не удалось получить информацию об IP-адресе.")
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


@router.message(Command("phone"))
async def search_phone_command(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer("Пожалуйста, укажите телефон. Пример: /phone +79111234567")
        return

    phone_args = command.args.strip().split(" ")
    phone = phone_args[0]

    await message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о номере телефона. Вы также можете попробовать воспользоваться Phomber, добавить контакт в Viber/Telegram/Whatsapp/Signal и др. мессенджерах, а также слить свои данные, но воспользоваться GetContact.",
        reply_markup=get_phone_services_keyboard(phone),
    )


@router.message(Command("domain"))
async def search_domain_command(message: Message, command: CommandObject):
    await message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о домене и его уязвимостях.",
        reply_markup=get_domain_services_keyboard(),
    )


@router.message(Command("crypto"))
async def search_crypto_command(message: Message, command: CommandObject):
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
    except TelegramBadRequest:
        pass

    await message.answer(
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


@router.message(Command("entrepreneur"))
async def search_entrepreneur_command(message: Message, command: CommandObject):
    await message.answer(
        "Вы можете воспользоваться ссылками ниже для получения информации о предпринимателе (ИП).",
        reply_markup=get_entrepreneur_services_keyboard(),
    )


@router.message(Command("full_name"))
async def search_full_name_command(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Пожалуйста, укажите ФИО и дату рождения (опционально). Пример: /full_name Иван Иванович Иванов 2004, /full_name Иван Иванов"
        )
        return

    args = command.args.strip().split()
    num_args = len(args)

    if num_args < 2:
        await message.answer(
            "Пожалуйста, укажите хотя бы имя и фамилию. Пример: /full_name Иван Иванов"
        )
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
        "Все сервисы поиска по ФИО на данный момент неактуальны. Вы можете воспользоваться ссылкой ниже для получения информации о пользователе.",
        reply_markup=get_full_name_services_keyboard(
            first_name, last_name, middle_name
        ),
    )

    namint = Namint(
        name=first_name,
        middle=middle_name,
        surname=last_name,
        date_of_birth=date_of_birth,
        dom1="gmail.com",
    )
    links = namint.generate_links()

    await message.answer(
        "Вы также можете воспользоваться готовыми дорками для поиска по ФИО, представленными в .txt файле ниже."
    )

    namint_result = f"namint_links_{first_name}_{last_name}.txt"

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
    await message.answer_document(dorks_file)

    try:
        os.remove(namint_result)
    except FileNotFoundError:
        pass
