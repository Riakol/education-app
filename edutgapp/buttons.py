from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button, Back, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from database import engine, requests


async def level_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_level = button.widget_id
    manager.dialog_data['selected_level'] = requests.levels[selected_level]
    
    await manager.next()


async def create_level_buttons():

    eng_levels = [
        Button(
            Const(x),
            id=f"{x.lower().replace('-', '')}",
            on_click=level_button_clicked,
        ) for x in await engine.student_levels()
    ]

    return eng_levels


async def create_group_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Обработка создания новой группы """
    selected_level = manager.dialog_data.get('selected_level')

    conn = await engine.connect_to_db()

    try:
        group_number = await requests.find_or_create_group(conn, selected_level)
        await callback.answer(f"Группа {group_number} для уровня {selected_level} была создана.")
    finally:
        await engine.close_db_connection(conn)


async def get_group_buttons(selected_level):
    groups = await requests.get_groups_for_level(selected_level)

    if groups:
        group_buttons = [
            Button(Const(f"Group: {group_id}"), id=f"group_{group_id}", on_click=group_selected)
            for group_id in groups
        ]
    else:
        group_buttons = [] 

    return group_buttons 


async def get_groups_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Обработчик для кнопки 'Select a group'."""
    
    selected_level = await requests.get_lvl_id(manager.dialog_data.get('selected_level'))
    user_id = callback.from_user.id

    await requests.insert_lvl_teacher_current_pos(selected_level, await requests.get_teacher_id(user_id))
    group_buttons = await get_group_buttons(selected_level)

    group_buttons_dict = {
        f"Group: {group_id.widget_id}": group_id.widget_id  # Ключ - строка, значение - id группы
        for group_id in group_buttons
    }

    print(group_buttons)
    await manager.update({"group_buttons": group_buttons})
    await manager.update({"group_buttons_text": group_buttons_dict})
    
    
    await manager.next()


async def group_selected(callback: CallbackQuery, button: Button, manager: DialogManager, item_id: str):
    """ Действие при выборе группы """
    # selected_group = manager.dialog_data.get('group_buttons')
    await callback.answer(f"You selected group!")


async def dialog_get_data(dialog_manager: DialogManager, **kwargs):
    context = dialog_manager.current_context()
    data = context.dialog_data  
    return {
        "group_buttons": data.get("group_buttons", []), 
        "group_buttons_text": data.get("group_buttons_text"), 
        "name": "Obayash", 
        "selected_level": data.get("selected_level"),
    }


