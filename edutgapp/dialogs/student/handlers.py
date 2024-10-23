import FSM

from database.engine import db
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import (
    DialogManager, ChatEvent, StartMode
)
from aiogram_dialog.widgets.kbd import ManagedCheckbox
from database import requests
from typing import Any
from dialogs.group.handlers import get_group_buttons


async def remove_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):

    await requests.remove_student(int(item_id.split('_')[1]))
    await callback.answer(f"✅ the student has been successfully removed!")

    await manager.done()

async def rename_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"rename_student_id_selected": int(item_id.split('_')[1])})

    await manager.switch_to(FSM.Student.update_student_name)


async def payment_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"payment_student_id_selected": int(item_id.split('_')[1])})

    payment_buttons = await get_payment_methods()
    await manager.update({"payment_methods": payment_buttons})

    await manager.switch_to(FSM.Student.payment_method)

async def get_payment_methods():
    payment_method = await requests.get_payment_methods()

    if payment_method:
        payment_buttons = [
            (f"{pm['method_name']}: {int(pm['amount'])}", Button(text=Const(f"Payment method: {pm['method_name']}"), id=f"{pm['id']}", on_click=payment_method_selected))
            for pm in payment_method
        ]
    else:
        payment_buttons = [] 

    return payment_buttons


async def payment_method_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    try:
        student_id = manager.dialog_data.get("payment_student_id_selected")
        eng_lvl_id = await requests.get_lvl_id(manager.start_data["selected_level"])
        group_id = manager.start_data['group_selected_id']
        gdi = await requests.get_group_details_id(eng_lvl_id, group_id)
        student_details_id = await requests.get_student_details_id(student_id, gdi)

        await requests.set_student_payment(student_details_id, int(item_id))

        await callback.answer(f"✅ Payment has been successfully updated!")
        await manager.switch_to(FSM.Student.editing_student_menu)
    except Exception as e:
        await callback.answer(f"❌ An error occurred")
        await manager.switch_to(FSM.Student.editing_student_menu)
        print(f"Error in payment_method_selected: {e}")

async def update_student_name(callback: CallbackQuery, button: Button, manager: DialogManager):
    new_student_name = manager.find("new_student_name").get_value()
    student_id = manager.dialog_data.get("rename_student_id_selected")

    if student_id:
        await requests.update_student_name(new_student_name, student_id)

    await callback.answer(f"✅ the name has been successfully updated!")


async def level_buttons():

    eng_levels = [
        Button(
            Const(x),
            id=f"{x.lower().replace('-', '')}",
            on_click=level_button_clicked,
        ) for x in await requests.student_levels()
    ]

    return eng_levels

async def student_transfer_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    # print(f"This is transfer_student_id_selected {int(item_id.split('_')[1])}") # здесь будет id_42 например
    await manager.update({"transfer_student_id_selected": int(item_id.split('_')[1])})
    await manager.switch_to(FSM.Student.transfer_student_level)


async def level_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_level = button.widget_id
    level_name = requests.levels[selected_level]
    lvl_id = await requests.get_lvl_id(level_name)

    group_buttons = await get_group_buttons(lvl_id)

    await manager.update({"transfer_level": level_name})
    await manager.update({"transfer_level_id": lvl_id})
    await manager.update({"transfer_groups": group_buttons})

    await manager.switch_to(FSM.Student.transfer_student_group)


async def transfer_group_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    await manager.update({"transfer_group_selected": item_id})

    student_id = manager.dialog_data.get("transfer_student_id_selected")
    
    eng_lvl_id = await requests.get_lvl_id(manager.start_data["selected_level"])
    group_id = manager.start_data['group_selected_id']
    gdi = await requests.get_group_details_id(eng_lvl_id, group_id)
    student_details_id = await requests.get_student_details_id(student_id, gdi)

    new_transfer_group = await db.fetch("""
        SELECT id
        FROM group_details
        WHERE eng_lvl_id = $1 AND group_id = $2 AND status = 'active';
                                          """, manager.dialog_data.get("transfer_level_id"),
                                          int(manager.dialog_data.get("transfer_group_selected")))
    
    
    if new_transfer_group:
        new_transfer_group_id = new_transfer_group[0]['id']
    else:
        await callback.answer("❌ New transfer group not found.")
        return

    student_name = await db.fetchval("""
        SELECT name FROM student WHERE id = $1;
    """, student_id)

    existing_student = await db.fetch("""
        SELECT sd.id FROM student_details sd
        JOIN student s ON sd.student_id = s.id
        WHERE sd.group_details_id = $1 AND s.name = $2 AND sd.status = 'active';
    """, new_transfer_group_id, student_name)

    if existing_student:
        await callback.message.answer(f"❌ A student named '{student_name}' already exists in the new group. Please rename the student.")
        await manager.switch_to(FSM.Student.editing_student_menu)
        return

    attendance_records = await db.fetch("""
        SELECT date, status, absence_reason FROM attendance WHERE student_details_id = $1;
    """, student_details_id)

    for record in attendance_records:
        await db.execute("""
            INSERT INTO student_attendance_history (student_id, eng_lvl_id, group_id, date, status, absence_reason)
            VALUES ($1, $2, $3, $4, $5, $6);
        """, student_id, eng_lvl_id, group_id, record['date'], record['status'], record.get('absence_reason', None))

    await db.execute("""
        DELETE FROM attendance 
        WHERE student_details_id = $1;
    """, student_details_id)

    await db.execute("""
        UPDATE student_details 
        SET group_details_id = $1 
        WHERE id = $2;
    """, new_transfer_group_id, student_details_id)

    await callback.answer(f"✅ The student has been successfully transferred to a new group!")

    await manager.switch_to(FSM.Student.editing_student_menu)
    
    

    

