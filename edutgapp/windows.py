from FiniteStateMachine import StudentLevelGroup
from buttons import (create_level_buttons, create_group_clicked, 
                    get_groups_clicked, get_group_buttons)
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button, Back, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window
)


async def dialog_get_data(**kwargs):
    return {
        "name": "Obayash",
    }

async def my_window():

    show_levels = await create_level_buttons()

    dialog = Dialog(
    Window(
        Format("Hello, {name} 💕"),
        Group(*show_levels, width=2),
        state=StudentLevelGroup.choose_level,
    ),
    Window(
        Format("Group Menu ⤵️"),
        Group(
        Button(Const("Create a group"), id="cag", on_click=create_group_clicked),
        Button(Const("Select a group"), id="sag", on_click=get_groups_clicked),
        width=1,
        ),       
        Back(text=Const("Back")),
        state=StudentLevelGroup.choose_group,
    ),
    Window(
            Format("Select a group ⤵️"),
            Back(text=Const("Back")),
            state=StudentLevelGroup.select_group,
        ),
    getter=dialog_get_data,
    )

    return dialog