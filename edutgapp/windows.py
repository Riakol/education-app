import buttons
import operator
from database import requests
from FiniteStateMachine import StudentLevelGroup
# from buttons import (create_level_buttons, create_group_clicked, 
#                     get_groups_clicked, get_group_buttons)
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Back, Button, Row, Select, SwitchTo, Group, ListGroup
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window
)


# async def dialog_get_data(**kwargs):
#     return {
#         "name": "Obayash",
#     }

async def my_window():

    show_levels = await buttons.create_level_buttons()
    show_group_buttons = await buttons.get_group_buttons(await requests.get_lvl_from_current_pos())

    dialog = Dialog(
    Window(
        Format("Hello, {name} 💕"),
        Group(*show_levels, width=2),
        state=StudentLevelGroup.choose_level,
    ),
    Window(
        Format("{selected_level}: Menu ⤵️"),
        Group(
        Button(Const("Create a group"), id="cag", on_click=buttons.create_group_clicked),
        Button(Const("Select a group"), id="sag", on_click=buttons.get_groups_clicked),
        width=1,
        ),       
        Back(text=Const("Back")),
        state=StudentLevelGroup.choose_group,
    ),
    Window(
            Format("{selected_level}: Select a group ⤵️"),
            Select(
                Format("{item.widget_id}"),
                id="s_groups",
                item_id_getter=lambda x: x.widget_id,
                items="group_buttons",
                on_click=buttons.group_selected,
            ),
            Back(text=Const("Back")),
            state=StudentLevelGroup.select_group,
        ),
    getter=buttons.dialog_get_data,
    )

    return dialog