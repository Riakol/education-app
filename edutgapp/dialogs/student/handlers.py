from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import (
    DialogManager, ChatEvent, StartMode
)
from aiogram_dialog.widgets.kbd import ManagedCheckbox
from database import engine, requests
import FSM
from typing import Any


async def remove_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):

    await requests.remove_student(int(item_id.split('_')[1]))
    await callback.answer(f"✅ the student has been successfully removed!")

    await manager.done()


async def rename_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"rename_student_id_selected": int(item_id.split('_')[1])})

    await manager.switch_to(FSM.Student.update_student_name)


async def update_student_name(callback: CallbackQuery, button: Button, manager: DialogManager):
    new_student_name = manager.find("new_student_name").get_value()
    student_id = manager.dialog_data.get("rename_student_id_selected")

    if student_id:
        await requests.update_student_name(new_student_name, student_id)

    await callback.answer(f"✅ the name has been successfully updated!")

