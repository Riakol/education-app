from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button, Back, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from database import engine, requests


async def level_button_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_level = button.widget_id  # Получаем ID кнопки (уровень языка)
    manager.dialog_data['selected_level'] = selected_level  # Сохраняем выбор в данные диалога
    
    await manager.next()


async def create_level_buttons():

    # После получения данных создаем список кнопок
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

    if not groups:
        return []  

    group_buttons = [
        Button(Const(f"Group {group_id}"), id=f"group_{group_id}", on_click=group_selected)
        for group_id in groups
    ]
    
    return group_buttons 


async def get_groups_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Обработчик для кнопки 'Select a group'."""
    selected_level = manager.dialog_data.get('selected_level')

    # Получаем Telegram ID пользователя
    user_id = callback.from_user.id
    print(f"User ID: {user_id}")  # Выводим ID пользователя в консоль

    # Получаем кнопки групп
    group_buttons = await get_group_buttons(selected_level)

    if not group_buttons:
        await callback.message.answer("There are no groups.")
        return

    # Сохраняем кнопки в контексте manager
    manager.dialog_data['group_buttons'] = group_buttons
    
    await manager.next()


async def group_selected(callback: CallbackQuery, button: Button, manager: DialogManager):
    """ Действие при выборе группы """
    selected_group = button.widget_id.split('_')[1]
    await callback.answer(f"You selected group {selected_group}!")

