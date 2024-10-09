import logging
import asyncio
import FSM
import dialogs.group.window
import dialogs.level.window
import dialogs.attendace.window
import dialogs.student.window

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    DialogManager, setup_dialogs, StartMode
)
from aiogram_dialog import DialogManager
from decouple import config




storage = MemoryStorage()
bot = Bot(config('TOKEN'))
dp = Dispatcher(storage=storage)

async def main():

    dp.include_router(await dialogs.level.window.level_window())
    dp.include_router(await dialogs.group.window.groups())
    dp.include_router(await dialogs.attendace.window.attendance_window())
    dp.include_router(await dialogs.student.window.student_window())
    setup_dialogs(dp)


    @dp.message(Command("start"))
    async def start(message: Message, dialog_manager: DialogManager):
        await dialog_manager.start(FSM.Level.choose_level, mode=StartMode.RESET_STACK)
    try:
        await dp.start_polling(bot, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # DEBUG ONLY !

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")