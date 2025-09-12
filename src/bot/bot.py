import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

import src.bot.handlers.commands
import src.bot.handlers.common
import src.bot.handlers.search
from src.config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(
            command="crypto",
            description="Введите /crypto для поиска по адресам криптокошельков",
        ),
        BotCommand(
            command="email",
            description="Введите /email example@mail.com для поиска по почте",
        ),
        BotCommand(
            command="entrepreneur",
            description="Введите /entrepreneur для поиска информации о предпринимателях (ИП)",
        ),
        BotCommand(
            command="full_name",
            description="Введите /full_name Имя Фамилия (Отчество) (Дата рождения) для поиска информации по ФИО, значения в скобках необязательны",
        ),
        BotCommand(command="help", description="Помощь"),
        BotCommand(
            command="links", description="Полезные ссылки для углубленного изучения"
        ),
        BotCommand(
            command="steam",
            description="Введите /steam для поиска по Steam",
        ),
        BotCommand(
            command="telegram",
            description="Введите /telegram для поиска по Telegram",
        ),
        BotCommand(
            command="username",
            description="Введите /username nickname или /username deep nickname для глубокого поиска",
        ),
        BotCommand(
            command="vk",
            description="Введите /vk username или /vk https://vk.com/username для поиска по VK",
        ),
        BotCommand(
            command="ip",
            description="Введите /ip xxx.xxx.xxx.xxx для поиска по IP",
        ),
        BotCommand(
            command="phone",
            description="Введите /phone +79123456789 для поиска по номеру телефона",
        ),
    ]

    await bot.set_my_commands(commands)


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        src.bot.handlers.common.router,
        src.bot.handlers.search.router,
        src.bot.handlers.commands.router,
    )

    dp["bot"] = bot

    await set_bot_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
