from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards import build_inline_search_menu, get_links_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Выбери действие:", reply_markup=build_inline_search_menu())


@router.message(Command("help"))
@router.message(F.text.lower().contains("помощь"))
@router.message(F.text.lower() == "информация")
@router.message(F.text.lower() == "ℹ️ информация")
async def cmd_help(message: Message):
    help_text = (
        "Я могу помочь тебе найти информацию.\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "Просто отправь мне данные для поиска (email, телефон, никнейм, ссылку VK/Instagram) "
        "или выбери действие в меню."
    )
    await message.answer(help_text)


@router.message(Command("links"))
@router.message(F.text.lower().contains("полезные ссылки"))
async def show_links(message: Message):
    await message.answer(
        "Полезные ссылки для OSINT:", reply_markup=get_links_keyboard()
    )
