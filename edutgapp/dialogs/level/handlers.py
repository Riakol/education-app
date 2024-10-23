from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import (
    DialogManager, ChatEvent, 
)
from aiogram_dialog.widgets.text import Const
from database import requests
from FSM import Group
from typing import Any

async def level_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_level = button.widget_id
    level_name = requests.levels[selected_level]

    await manager.start(Group.choose_group, data={"selected_level": level_name})


async def create_level_buttons():

    eng_levels = [
        Button(
            Const(x),
            id=f"{x.lower().replace('-', '')}",
            on_click=level_button_clicked,
        ) for x in await requests.student_levels()
    ]

    return eng_levels