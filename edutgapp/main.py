import logging
import asyncio
import FSM
import winds 

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

    dp.include_router(await winds.my_window())
    setup_dialogs(dp)


    @dp.message(Command("start"))
    async def start(message: Message, dialog_manager: DialogManager):
        await dialog_manager.start(FSM.StudentWorkflow.choose_level, mode=StartMode.RESET_STACK)
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