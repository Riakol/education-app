import FSM

from aiogram_dialog.widgets.kbd import Group
from aiogram_dialog.widgets.text import Format
from aiogram_dialog import (
    Dialog, Window
)
from dialogs.level import handlers as action

async def level_window():

    show_levels = await action.create_level_buttons()

    dialog = Dialog(
        Window(
            Format("Hello, Obayash 💕"),
            Group(*show_levels, width=2),
            state=FSM.Level.choose_level,
        ),
    )

    return dialog