import logging
import asyncio
import buttons
import FiniteStateMachine
import windows
from database import engine, requests


from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Button, Back, Group
from aiogram_dialog.widgets.text import Const, Format
from decouple import config


storage = MemoryStorage()
bot = Bot(config('TOKEN'))
dp = Dispatcher(storage=storage)

async def main():
    dp.include_router(await windows.my_window())
    setup_dialogs(dp)

    ALLOWED_TELEGRAM_ID = await requests.access_start()

    @dp.message(Command("start"))
    async def start(message: Message, dialog_manager: DialogManager):
        print(message.from_user.id)

        if message.from_user.id in ALLOWED_TELEGRAM_ID:
            await dialog_manager.start(FiniteStateMachine.StudentLevelGroup.choose_level, mode=StartMode.RESET_STACK)
        else:
            await message.reply("You don't have access ❌")

    await dp.start_polling(bot, skip_updates=True)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # DEBUG ONLY !

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")